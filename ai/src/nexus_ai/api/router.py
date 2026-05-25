"""
API router registry — collects all versioned routers.
Add new route modules here as the project grows.
"""
from __future__ import annotations

from fastapi import APIRouter

from nexus_ai.api.v1 import auth, datasets, health, inference, maps, projects

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(health.router, tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(maps.router, prefix="/maps", tags=["maps"])
api_router.include_router(inference.router, prefix="/inference", tags=["inference"])
