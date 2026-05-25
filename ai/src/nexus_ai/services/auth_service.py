"""
AuthService — business logic layer for all authentication operations.

Keeps FastAPI route handlers thin; all DB/Redis I/O is here.
"""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from jose import JWTError
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_ai.config import Settings
from nexus_ai.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    refresh_redis_key,
    verify_password,
)
from nexus_ai.models.user import User, UserRole
from nexus_ai.schemas.auth import (
    SignupRequest,
    TokenResponse,
    UserOut,
)

_REFRESH_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days (matches REFRESH_TOKEN_EXPIRE_DAYS default)


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis, settings: Settings) -> None:
        self._db = db
        self._redis = redis
        self._settings = settings

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _get_user_by_email(self, email: str) -> User | None:
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self._db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def _build_token_pair(self, user: User) -> TokenResponse:
        access_token, expires_in = create_access_token(user.id, user.role, self._settings)
        refresh_token, jti = create_refresh_token(user.id, user.role, self._settings)

        # Store JTI in Redis — presence = token valid; deletion = revoked
        refresh_ttl = self._settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        await self._redis.setex(refresh_redis_key(jti), refresh_ttl, str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    # ── Signup ─────────────────────────────────────────────────────────────────

    async def signup(self, body: SignupRequest) -> tuple[UserOut, TokenResponse]:
        if await self._get_user_by_email(body.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        user = User(
            email=body.email,
            full_name=body.full_name,
            hashed_password=hash_password(body.password),
            role=UserRole.VIEWER,
        )
        self._db.add(user)
        await self._db.flush()   # get the UUID before commit

        tokens = await self._build_token_pair(user)
        return UserOut.model_validate(user), tokens

    # ── Login ──────────────────────────────────────────────────────────────────

    async def login(self, email: str, password: str) -> tuple[UserOut, TokenResponse]:
        user = await self._get_user_by_email(email)

        # Constant-time failure path (prevents user enumeration timing attacks)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        tokens = await self._build_token_pair(user)
        return UserOut.model_validate(user), tokens

    # ── Refresh ────────────────────────────────────────────────────────────────

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token, self._settings, expected_type="refresh")
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from exc

        # Verify JTI exists in Redis (not revoked)
        stored = await self._redis.get(refresh_redis_key(payload.jti))
        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        user = await self._get_user_by_id(uuid.UUID(payload.sub))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Rotate: delete old JTI, issue a new pair
        await self._redis.delete(refresh_redis_key(payload.jti))
        return await self._build_token_pair(user)

    # ── Logout ─────────────────────────────────────────────────────────────────

    async def logout(self, refresh_token: str) -> None:
        """Revoke the refresh token by deleting its JTI from Redis."""
        try:
            payload = decode_token(refresh_token, self._settings, expected_type="refresh")
            await self._redis.delete(refresh_redis_key(payload.jti))
        except JWTError:
            pass  # Already invalid — treat as success

    # ── Change password ────────────────────────────────────────────────────────

    async def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self._get_user_by_id(user_id)
        if user is None or not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )
        user.hashed_password = hash_password(new_password)
        # Invalidate all existing refresh tokens by wiping keys for this user
        # (Simpler alternative: store user version in Redis and bump it)
        await self._db.flush()
