"""
Cryptographic utilities:
  - bcrypt password hashing (passlib)
  - JWT access & refresh token creation / verification (python-jose)
  - Refresh token JTI stored in Redis for revocation support
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from nexus_ai.config import Settings
from nexus_ai.models.user import UserRole
from nexus_ai.schemas.auth import TokenPayload

# ── Password hashing ──────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

REFRESH_TOKEN_REDIS_PREFIX = "refresh:"


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of *plain*. Max 72 bytes (bcrypt limit)."""
    return _pwd_context.hash(plain[:72])


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time comparison of *plain* against stored *hashed* password."""
    return _pwd_context.verify(plain[:72], hashed)


# ── Token creation ─────────────────────────────────────────────────────────────

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    user_id: uuid.UUID,
    role: UserRole,
    settings: Settings,
) -> tuple[str, int]:
    """
    Return (encoded_jwt, expires_in_seconds).
    expires_in is used by the client to schedule a refresh before expiry.
    """
    jti = str(uuid.uuid4())
    expire = _utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "type": "access",
        "jti": jti,
        "exp": int(expire.timestamp()),
        "iat": int(_utcnow().timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def create_refresh_token(
    user_id: uuid.UUID,
    role: UserRole,
    settings: Settings,
) -> tuple[str, str]:
    """
    Return (encoded_jwt, jti).
    The caller must store the jti in Redis with the appropriate TTL.
    """
    jti = str(uuid.uuid4())
    expire = _utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "type": "refresh",
        "jti": jti,
        "exp": int(expire.timestamp()),
        "iat": int(_utcnow().timestamp()),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti


# ── Token verification ────────────────────────────────────────────────────────

def decode_token(token: str, settings: Settings, expected_type: str) -> TokenPayload:
    """
    Decode and validate a JWT.

    Args:
        token:          Raw JWT string.
        settings:       App settings (secret key, algorithm).
        expected_type:  "access" or "refresh" — validated against the "type" claim.

    Raises:
        JWTError: on any validation failure (expired, bad signature, wrong type).
    """
    try:
        raw = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise

    if raw.get("type") != expected_type:
        raise JWTError(f"Expected token type '{expected_type}', got '{raw.get('type')}'")

    return TokenPayload(**raw)


# ── Redis key helper ──────────────────────────────────────────────────────────

def refresh_redis_key(jti: str) -> str:
    """Redis key for a refresh token's JTI whitelist entry."""
    return f"{REFRESH_TOKEN_REDIS_PREFIX}{jti}"
