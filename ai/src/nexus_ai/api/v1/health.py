"""Health check endpoints — used by load balancers and monitoring."""
from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel

from nexus_ai.core.dependencies import DBSession, RedisClient

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
)
async def health_check(db: DBSession, redis: RedisClient) -> HealthResponse:
    from sqlalchemy import text

    db_status = "ok"
    redis_status = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "degraded"

    try:
        await redis.ping()
    except Exception:
        redis_status = "degraded"

    return HealthResponse(
        status="ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        database=db_status,
        redis=redis_status,
        version="0.1.0",
    )
