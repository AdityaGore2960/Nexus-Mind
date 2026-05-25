"""
Pydantic v2 schemas for ML inference.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from nexus_ai.models.inference import JobStatus


class BBox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class InferenceRequest(BaseModel):
    project_id: uuid.UUID
    dataset_ids: list[uuid.UUID] = Field(..., min_length=1)
    area_of_interest: BBox
    model_version: str = "latest"


class InferenceJobOut(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    project_id: uuid.UUID
    dataset_ids: list[str]
    model_version: str
    status: JobStatus
    confidence_score: float | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    result_presigned_url: str | None = None
    shap_presigned_url: str | None = None

    model_config = {"from_attributes": True}


class InferenceJobCreatedOut(BaseModel):
    job: InferenceJobOut
    message: str = "Inference job queued successfully"
