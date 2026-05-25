"""
InferenceService — orchestrates ML inference jobs.
"""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_ai.config import Settings
from nexus_ai.models.inference import InferenceJob
from nexus_ai.schemas.inference import InferenceJobOut, InferenceRequest
from nexus_ai.services.storage_service import StorageService
from nexus_ai.tasks.ml_tasks import run_inference_task


class InferenceService:
    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self._db = db
        self._settings = settings
        self._storage = StorageService(settings)

    def _bbox_to_wkt(self, bbox) -> str:
        w, s, e, n = bbox.min_lon, bbox.min_lat, bbox.max_lon, bbox.max_lat
        return f"POLYGON(({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))"

    async def create_job(self, owner_id: uuid.UUID, body: InferenceRequest) -> InferenceJobOut:
        job_id = uuid.uuid4()
        dataset_ids = [str(ds_id) for ds_id in body.dataset_ids]

        job = InferenceJob(
            id=job_id,
            owner_id=owner_id,
            project_id=body.project_id,
            dataset_ids=dataset_ids,
            area_of_interest=self._bbox_to_wkt(body.area_of_interest),
            model_version=body.model_version,
        )
        self._db.add(job)
        await self._db.flush()

        # Enqueue Celery task
        run_inference_task.delay(str(job_id))

        return InferenceJobOut.model_validate(job)

    async def get_job(self, owner_id: uuid.UUID, job_id: uuid.UUID) -> InferenceJobOut:
        result = await self._db.execute(
            select(InferenceJob).where(InferenceJob.id == job_id, InferenceJob.owner_id == owner_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        # Get presigned URLs if completed
        result_url = None
        shap_url = None
        if job.result_s3_key:
            try:
                result_url = await self._storage.presigned_url(self._settings.S3_BUCKET_PROCESSED, job.result_s3_key)
            except Exception:
                pass
        if job.shap_s3_key:
            try:
                shap_url = await self._storage.presigned_url(self._settings.S3_BUCKET_ML, job.shap_s3_key)
            except Exception:
                pass

        out = InferenceJobOut.model_validate(job)
        out.result_presigned_url = result_url
        out.shap_presigned_url = shap_url
        return out
