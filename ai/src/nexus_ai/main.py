"""
NEXUS-MIND AI Backend — Application Entry Point

Lifespan manages startup/shutdown of DB, Redis, and ML model registry.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from nexus_ai.api.router import api_router
from nexus_ai.config import Settings, get_settings
from nexus_ai.core.logging import configure_logging
from nexus_ai.core.middleware import register_middleware
from nexus_ai.db.redis import close_redis, init_redis
from nexus_ai.db.session import close_db, init_db

logger = structlog.get_logger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings: Settings = get_settings()
    configure_logging(settings.LOG_LEVEL, settings.LOG_FORMAT)

    logger.info("startup_begin", service=settings.APP_NAME, version=settings.APP_VERSION)

    # Database
    init_db(settings)
    logger.info("database_engine_initialised", url=settings.database_url_str)

    # Redis
    init_redis(str(settings.REDIS_URL), settings.REDIS_MAX_CONNECTIONS)
    logger.info("redis_pool_connected", url=str(settings.REDIS_URL))

    # ── Future: warm ML model registry ────────────────────────────────────
    # from nexus_ai.ml.registry import ModelRegistry
    # app.state.model_registry = await ModelRegistry.load(settings.MODEL_REGISTRY_PATH)

    logger.info("startup_complete", env=settings.ENV)

    yield  # ─── application running ──────────────────────────────────────

    # Teardown
    await close_db()
    await close_redis()
    logger.info("shutdown_complete")


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="NEXUS-MIND AI API",
        description=(
            "AI-Powered Geospatial Mineral Prospectivity Mapping Platform. "
            "Combines satellite imagery, geological maps, geochemistry, "
            "geophysics, and ensemble ML to predict exploration zones."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # Middleware (order: outermost → innermost)
    register_middleware(app, settings)

    # Routers
    app.include_router(api_router)

    # ── Global exception handlers ─────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()
