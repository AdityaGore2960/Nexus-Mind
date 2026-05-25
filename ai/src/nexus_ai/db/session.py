"""
Async SQLAlchemy 2.0 engine + session factory with PostGIS support.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from nexus_ai.config import Settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def build_engine(settings: Settings):
    """
    Create the async SQLAlchemy engine.
    NullPool is used in test/CLI contexts; connection pooling for app runtime.
    """
    connect_args: dict = {}

    return create_async_engine(
        settings.database_url_str,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def build_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


# ── Module-level singletons (initialized in app lifespan) ────────────────────
_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db(settings: Settings) -> None:
    global _engine, _session_factory
    _engine = build_engine(settings)
    _session_factory = build_session_factory(_engine)


async def close_db() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session per request."""
    if _session_factory is None:
        raise RuntimeError("Database not initialised. Call init_db() at startup.")
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
