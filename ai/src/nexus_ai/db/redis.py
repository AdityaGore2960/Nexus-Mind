"""
Redis connection pool — async via redis-py.
"""
from __future__ import annotations

import redis.asyncio as aioredis
from redis.asyncio import Redis

_redis_client: Redis | None = None


def init_redis(redis_url: str, max_connections: int = 50) -> None:
    global _redis_client
    _redis_client = aioredis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=max_connections,
    )


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> Redis:
    """FastAPI dependency — returns the shared Redis client."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialised. Call init_redis() at startup.")
    return _redis_client
