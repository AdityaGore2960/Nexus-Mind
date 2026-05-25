"""
FastAPI dependency injection factories.

All dependencies are importable from this single module to avoid circular imports.
"""
from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated, TYPE_CHECKING

if TYPE_CHECKING:
    from nexus_ai.models.user import User, UserRole

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt  # type: ignore[import-untyped]
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_ai.config import Settings, get_settings
from nexus_ai.db.redis import get_redis
from nexus_ai.db.session import get_db

# ── Type aliases for clean signatures ────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[Redis, Depends(get_redis)]
AppSettings = Annotated[Settings, Depends(get_settings)]

_bearer = HTTPBearer(auto_error=True)


# ── JWT → user ID ─────────────────────────────────────────────────────────────
async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    settings: AppSettings,
) -> str:
    """
    Decode JWT Bearer token and return the subject (user UUID string).
    Raises HTTP 401 on any failure.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "access":
            raise JWTError("Not an access token")
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise JWTError("missing sub")
        return user_id
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── JWT → full User ORM object ────────────────────────────────────────────────
async def get_current_user(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: DBSession,
) -> "User":  # noqa: F821 — forward ref resolved at runtime
    """
    Load the authenticated User from the database.
    Raises HTTP 401 if the user no longer exists or is deactivated.
    """
    from nexus_ai.models.user import User  # local import avoids circular deps

    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ── Role-based access guard factory ──────────────────────────────────────────
def require_roles(*allowed_roles: "UserRole") -> Callable:  # noqa: F821
    """
    Returns a FastAPI dependency that raises HTTP 403 unless the
    current user's role is in *allowed_roles*.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles(UserRole.ADMIN))])
    """
    async def _guard(user: Annotated["User", Depends(get_current_user)]) -> "User":  # noqa: F821
        from nexus_ai.models.user import UserRole  # local import
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {[r.value for r in allowed_roles]}",
            )
        return user
    return _guard


# ── Convenience aliases ───────────────────────────────────────────────────────
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
CurrentUser = Annotated["User", Depends(get_current_user)]  # noqa: F821

# Pre-built role guards
from nexus_ai.models.user import UserRole  # noqa: E402

RequireAnalyst = Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))
RequireAdmin = Depends(require_roles(UserRole.ADMIN))
