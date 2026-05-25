"""Projects domain — CRUD stubs (to be expanded)."""
from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel

from nexus_ai.core.dependencies import CurrentUserId, DBSession

router = APIRouter()


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str | None


@router.get("", response_model=list[ProjectOut], status_code=status.HTTP_200_OK)
async def list_projects(db: DBSession, user_id: CurrentUserId) -> list[ProjectOut]:
    """Return all mineral prospectivity projects for the authenticated user."""
    # TODO: delegate to ProjectService
    return []


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, db: DBSession, user_id: CurrentUserId) -> ProjectOut:
    # TODO: delegate to ProjectService
    raise NotImplementedError
