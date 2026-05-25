"""
ML Inference API Routes — /api/v1/inference/*
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession
from nexus_ai.config import Settings
from nexus_ai.models.user import User

from nexus_ai.core.dependencies import (
    RequireAnalyst,
    get_current_user,
)
from nexus_ai.db.session import get_db
from nexus_ai.config import get_settings
from nexus_ai.schemas.inference import InferenceJobCreatedOut, InferenceJobOut, InferenceRequest
from nexus_ai.services.inference_service import InferenceService

router = APIRouter()


def _svc(db: AsyncSession, settings: Settings) -> InferenceService:
    return InferenceService(db=db, settings=settings)


@router.post(
    "/run",
    response_model=InferenceJobCreatedOut,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger ML inference",
    dependencies=[RequireAnalyst],
)
async def run_inference(
    body: InferenceRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> InferenceJobCreatedOut:
    """
    Queue a mineral prospectivity inference job.
    Returns immediately with a job_id for polling.
    """
    job = await _svc(db, settings).create_job(user.id, body)
    return InferenceJobCreatedOut(job=job)


@router.get(
    "/{job_id}/status",
    response_model=InferenceJobOut,
    summary="Get job status & result URLs",
)
async def get_job_status(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> InferenceJobOut:
    """Poll inference job status and get presigned S3 URLs if completed."""
    return await _svc(db, settings).get_job(user.id, job_id)
