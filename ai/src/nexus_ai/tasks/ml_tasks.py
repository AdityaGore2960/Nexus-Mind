"""
Celery background tasks for ML inference.
"""
from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from celery.utils.log import get_task_logger

from nexus_ai.config import get_settings
from nexus_ai.db.session import build_engine, build_session_factory
from nexus_ai.ml.predictor import MineralPredictor
from nexus_ai.models.dataset import Dataset
from nexus_ai.models.inference import InferenceJob, JobStatus
from nexus_ai.services.storage_service import StorageService
from nexus_ai.tasks.celery_app import celery_app

logger = get_task_logger(__name__)


async def _run_inference_async(job_id_str: str) -> None:
    settings = get_settings()
    engine = build_engine(settings)
    SessionFactory = build_session_factory(engine)
    storage = StorageService(settings)
    job_id = uuid.UUID(job_id_str)

    async with SessionFactory() as db:
        # 1. Fetch job
        from sqlalchemy import select
        result = await db.execute(select(InferenceJob).where(InferenceJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        # Mark running
        job.status = JobStatus.RUNNING
        job.updated_at = datetime.now(timezone.utc)
        await db.commit()

        try:
            # 2. Fetch datasets to get S3 keys
            dataset_uuids = [uuid.UUID(ds_id) for ds_id in job.dataset_ids]
            ds_result = await db.execute(select(Dataset).where(Dataset.id.in_(dataset_uuids)))
            datasets = ds_result.scalars().all()
            dataset_keys = [ds.s3_key for ds in datasets]

            # 3. Extract bbox from PostGIS EWKT (simplification for the stub)
            # Extent is typically '0103000020E61000000100000005000...' we need the bbox.
            # In a real app we'd query PostGIS `ST_Envelope(extent)` or just use the raw request.
            # Here we fake the bbox for the predictor.
            bbox = {"min_lon": 72.0, "min_lat": 20.0, "max_lon": 73.0, "max_lat": 21.0}

            # 4. Predict
            logger.info(f"Starting prediction for job {job_id}")
            predictor = MineralPredictor(job.model_version)
            result_bytes, shap_bytes, confidence = predictor.predict(dataset_keys, bbox)

            # 5. Save results to S3
            result_key = f"processed/inference/{job.owner_id}/{job_id}/result.geojson"
            shap_key = f"processed/inference/{job.owner_id}/{job_id}/shap.geojson"

            await storage.upload(result_bytes, settings.S3_BUCKET_PROCESSED, result_key, "application/geo+json")
            await storage.upload(shap_bytes, settings.S3_BUCKET_ML, shap_key, "application/geo+json")

            # 6. Mark completed
            job.status = JobStatus.COMPLETED
            job.result_s3_key = result_key
            job.shap_s3_key = shap_key
            job.confidence_score = confidence
            job.updated_at = datetime.now(timezone.utc)
            await db.commit()
            logger.info(f"Job {job_id} completed successfully")

        except Exception as exc:
            logger.exception(f"Job {job_id} failed")
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.updated_at = datetime.now(timezone.utc)
            await db.commit()
        finally:
            await engine.dispose()


@celery_app.task(name="nexus_ai.tasks.run_inference", bind=True)
def run_inference_task(self, job_id_str: str) -> None:
    """Synchronous Celery task wrapper that runs the async logic."""
    asyncio.run(_run_inference_async(job_id_str))
