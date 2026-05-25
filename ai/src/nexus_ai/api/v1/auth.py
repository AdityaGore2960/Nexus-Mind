"""
Auth API routes — /api/v1/auth/*

All heavy logic is delegated to AuthService; routes stay thin.
"""
from __future__ import annotations

from fastapi import APIRouter, status

from nexus_ai.core.dependencies import (
    AppSettings,
    CurrentUserId,
    DBSession,
    RedisClient,
)
from nexus_ai.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    SignupResponse,
    TokenResponse,
    UserOut,
)
from nexus_ai.services.auth_service import AuthService

router = APIRouter()


def _svc(db: DBSession, redis: RedisClient, settings: AppSettings) -> AuthService:
    """Inline factory — keeps route signatures minimal."""
    return AuthService(db=db, redis=redis, settings=settings)


# ── POST /signup ──────────────────────────────────────────────────────────────
@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def signup(
    body: SignupRequest,
    db: DBSession,
    redis: RedisClient,
    settings: AppSettings,
) -> SignupResponse:
    user, tokens = await _svc(db, redis, settings).signup(body)
    return SignupResponse(user=user, tokens=tokens)


# ── POST /login ───────────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=SignupResponse,
    summary="Login and receive JWT token pair",
)
async def login(
    body: LoginRequest,
    db: DBSession,
    redis: RedisClient,
    settings: AppSettings,
) -> SignupResponse:
    user, tokens = await _svc(db, redis, settings).login(body.email, body.password)
    return SignupResponse(user=user, tokens=tokens)


# ── POST /refresh ─────────────────────────────────────────────────────────────
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotate refresh token and get a new token pair",
)
async def refresh_token(
    body: RefreshRequest,
    db: DBSession,
    redis: RedisClient,
    settings: AppSettings,
) -> TokenResponse:
    return await _svc(db, redis, settings).refresh(body.refresh_token)


# ── POST /logout ──────────────────────────────────────────────────────────────
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke refresh token",
)
async def logout(
    body: RefreshRequest,
    db: DBSession,
    redis: RedisClient,
    settings: AppSettings,
) -> None:
    await _svc(db, redis, settings).logout(body.refresh_token)


# ── GET /me ───────────────────────────────────────────────────────────────────
@router.get(
    "/me",
    response_model=UserOut,
    summary="Return the currently authenticated user",
)
async def get_me(
    user_id: CurrentUserId,
    db: DBSession,
    redis: RedisClient,
    settings: AppSettings,
) -> UserOut:
    from nexus_ai.core.dependencies import get_current_user
    return await get_current_user(user_id=user_id, db=db)


# ── PATCH /me/password ────────────────────────────────────────────────────────
@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user's password",
)
async def change_password(
    body: ChangePasswordRequest,
    user_id: CurrentUserId,
    db: DBSession,
    redis: RedisClient,
    settings: AppSettings,
) -> None:
    import uuid
    await _svc(db, redis, settings).change_password(
        uuid.UUID(user_id), body.current_password, body.new_password
    )
