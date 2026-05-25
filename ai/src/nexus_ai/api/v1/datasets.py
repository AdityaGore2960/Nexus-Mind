"""
Dataset APIs — /api/v1/datasets/*
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from sqlalchemy.ext.asyncio import AsyncSession
from nexus_ai.config import Settings
from nexus_ai.models.user import User

from nexus_ai.core.dependencies import (
    RequireAnalyst,
    get_current_user,
)
from nexus_ai.db.session import get_db
from nexus_ai.config import get_settings
from nexus_ai.models.dataset import DatasetType
from nexus_ai.schemas.dataset import DatasetListOut, UploadResponse
from nexus_ai.services.dataset_service import DatasetService

router = APIRouter()


def _svc(db: AsyncSession, settings: Settings) -> DatasetService:
    return DatasetService(db=db, settings=settings)


# ── POST /datasets/geotiff ───────────────────────────────────────────────────
@router.post(
    "/geotiff",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a GeoTIFF dataset",
    dependencies=[RequireAnalyst],
)
async def upload_geotiff(
    file: UploadFile = File(...),
    name: str = Form(..., min_length=1, max_length=255),
    project_id: uuid.UUID | None = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """
    Upload a GeoTIFF file. Extracts metadata (CRS, bounds, resolution) and
    uploads to S3. Max size: 2 GB.
    """
    return await _svc(db, settings).upload_geotiff(
        file=file,
        owner_id=user.id,
        name=name,
        project_id=project_id,
    )


# ── POST /datasets/csv ───────────────────────────────────────────────────────
@router.post(
    "/csv",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a CSV dataset",
    dependencies=[RequireAnalyst],
)
async def upload_csv(
    file: UploadFile = File(...),
    name: str = Form(..., min_length=1, max_length=255),
    project_id: uuid.UUID | None = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """
    Upload a CSV file (e.g. geochemistry or geophysics data).
    Extracts column metadata and uploads to S3. Max size: 500 MB.
    """
    return await _svc(db, settings).upload_csv(
        file=file,
        owner_id=user.id,
        name=name,
        project_id=project_id,
    )


# ── GET /datasets ────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=DatasetListOut,
    summary="List my datasets",
)
async def list_datasets(
    dataset_type: DatasetType | None = None,
    project_id: uuid.UUID | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DatasetListOut:
    """List datasets owned by the authenticated user."""
    return await _svc(db, settings).list_datasets(
        owner_id=user.id,
        dataset_type=dataset_type,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )


# ── GET /datasets/{id} ───────────────────────────────────────────────────────
@router.get(
    "/{dataset_id}",
    response_model=UploadResponse,
    summary="Get dataset details (with S3 download URL)",
)
async def get_dataset(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> UploadResponse:
    """Get metadata and a temporary S3 presigned URL for a specific dataset."""
    return await _svc(db, settings).get_dataset(
        dataset_id=dataset_id,
        owner_id=user.id,
    )


# ── DELETE /datasets/{id} ────────────────────────────────────────────────────
@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a dataset",
    dependencies=[RequireAnalyst],
)
async def delete_dataset(
    dataset_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> None:
    """Delete a dataset from the database and remove the file from S3."""
    await _svc(db, settings).delete_dataset(
        dataset_id=dataset_id,
        owner_id=user.id,
    )
