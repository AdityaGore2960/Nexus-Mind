"""
Middleware stack for NEXUS-MIND AI backend.

Registration order matters — each middleware wraps the next:
  1. TrustedHostMiddleware   – reject invalid Host headers (production)
  2. CORSMiddleware          – handle preflight / origin checks
  3. RequestIDMiddleware     – inject X-Request-ID into every request/response
  4. RequestTimingMiddleware – add X-Process-Time-Ms header
  5. RateLimitMiddleware     – sliding-window IP rate limit via Redis
"""
from __future__ import annotations

import time
import uuid

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from nexus_ai.config import Settings

logger = structlog.get_logger(__name__)


# ── Request ID ────────────────────────────────────────────────────────────────
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ── Request Timing ────────────────────────────────────────────────────────────
class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
        logger.debug(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=elapsed_ms,
        )
        return response


# ── Sliding-window IP rate limiter (Redis) ────────────────────────────────────
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests: int, window: int) -> None:
        super().__init__(app)
        self._requests = requests
        self._window = window

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Health/metrics endpoints are exempt
        if request.url.path in {"/health", "/metrics", "/docs", "/openapi.json"}:
            return await call_next(request)

        from nexus_ai.db.redis import get_redis
        try:
            redis = get_redis()
            ip = request.client.host if request.client else "unknown"
            key = f"rl:{ip}"
            pipe = redis.pipeline()
            now = int(time.time())
            window_start = now - self._window
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(uuid.uuid4()): now})
            pipe.zcard(key)
            pipe.expire(key, self._window)
            results = await pipe.execute()
            count: int = results[2]
            if count > self._requests:
                return Response(
                    content='{"detail":"Rate limit exceeded"}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={"Retry-After": str(self._window)},
                )
        except Exception:
            pass  # Redis unavailable → fail open

        return await call_next(request)


# ── Registration helper ───────────────────────────────────────────────────────
def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Apply all middleware to the FastAPI app (outermost first)."""

    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.nexusmind.io", "localhost"],
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time-Ms"],
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(RequestTimingMiddleware)

    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(
            RateLimitMiddleware,
            requests=settings.RATE_LIMIT_REQUESTS,
            window=settings.RATE_LIMIT_WINDOW_SECONDS,
        )
