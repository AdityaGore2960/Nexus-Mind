"""
DatasetService — orchestrates upload validation, metadata extraction,
S3 storage, and database persistence.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import anyio
import structlog
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from nexus_ai.config import Settings
from nexus_ai.models.dataset import Dataset, DatasetStatus, DatasetType
from nexus_ai.schemas.dataset import DatasetListOut, DatasetOut, UploadResponse
from nexus_ai.services.storage_service import StorageService
from nexus_ai.utils.geo_metadata import (
    extract_csv_metadata,
    extract_geotiff_metadata,
    geotiff_extent_wkt,
)
from nexus_ai.utils.validators import validate_csv, validate_geotiff

logger = structlog.get_logger(__name__)

# S3 key templates
_GEOTIFF_KEY = "raw/geotiff/{owner_id}/{dataset_id}/{filename}"
_CSV_KEY = "raw/csv/{owner_id}/{dataset_id}/{filename}"


class DatasetService:
    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self._db = db
        self._settings = settings
        self._storage = StorageService(settings)

    # ── Upload GeoTIFF ────────────────────────────────────────────────────────

    async def upload_geotiff(
        self,
        file: UploadFile,
        owner_id: uuid.UUID,
        name: str,
        project_id: uuid.UUID | None = None,
    ) -> UploadResponse:
        # 1. Validate
        await validate_geotiff(file)

        # 2. Read file bytes into memory (validated size ≤ 2 GB)
        data = await file.read()

        # 3. Extract metadata in thread (rasterio is sync/CPU-bound)
        try:
            meta = await anyio.to_thread.run_sync(
                lambda: extract_geotiff_metadata(data)
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        # 4. Build DB record (pending)
        dataset_id = uuid.uuid4()
        s3_key = _GEOTIFF_KEY.format(
            owner_id=owner_id,
            dataset_id=dataset_id,
            filename=file.filename or "upload.tif",
        )

        extent_wkt = geotiff_extent_wkt(meta.bbox)

        dataset = Dataset(
            id=dataset_id,
            owner_id=owner_id,
            project_id=project_id,
            name=name,
            original_filename=file.filename or "upload.tif",
            dataset_type=DatasetType.GEOTIFF,
            status=DatasetStatus.PROCESSING,
            s3_bucket=self._settings.S3_BUCKET_RAW,
            s3_key=s3_key,
            file_size_bytes=len(data),
            content_type=file.content_type or "image/tiff",
            metadata_=meta.model_dump(),
            extent=extent_wkt,
        )
        self._db.add(dataset)
        await self._db.flush()

        # 5. Upload to S3
        await self._storage.upload(
            data=data,
            bucket=self._settings.S3_BUCKET_RAW,
            key=s3_key,
            content_type=file.content_type or "image/tiff",
        )

        # 6. Mark ready
        dataset.status = DatasetStatus.READY
        dataset.updated_at = datetime.now(timezone.utc)
        await self._db.flush()

        logger.info(
            "geotiff_uploaded",
            dataset_id=str(dataset_id),
            crs=meta.crs,
            bands=meta.band_count,
            size_bytes=len(data),
        )

        return UploadResponse(dataset=DatasetOut.model_validate(dataset))

    # ── Upload CSV ────────────────────────────────────────────────────────────

    async def upload_csv(
        self,
        file: UploadFile,
        owner_id: uuid.UUID,
        name: str,
        project_id: uuid.UUID | None = None,
    ) -> UploadResponse:
        # 1. Validate
        await validate_csv(file)

        # 2. Read
        data = await file.read()

        # 3. Extract metadata in thread (pandas is sync)
        try:
            meta = await anyio.to_thread.run_sync(
                lambda: extract_csv_metadata(data)
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        # 4. Build DB record
        dataset_id = uuid.uuid4()
        s3_key = _CSV_KEY.format(
            owner_id=owner_id,
            dataset_id=dataset_id,
            filename=file.filename or "upload.csv",
        )

        dataset = Dataset(
            id=dataset_id,
            owner_id=owner_id,
            project_id=project_id,
            name=name,
            original_filename=file.filename or "upload.csv",
            dataset_type=DatasetType.CSV,
            status=DatasetStatus.PROCESSING,
            s3_bucket=self._settings.S3_BUCKET_RAW,
            s3_key=s3_key,
            file_size_bytes=len(data),
            content_type=file.content_type or "text/csv",
            metadata_=meta.model_dump(),
        )
        self._db.add(dataset)
        await self._db.flush()

        # 5. Upload to S3
        await self._storage.upload(
            data=data,
            bucket=self._settings.S3_BUCKET_RAW,
            key=s3_key,
            content_type=file.content_type or "text/csv",
        )

        # 6. Mark ready
        dataset.status = DatasetStatus.READY
        dataset.updated_at = datetime.now(timezone.utc)
        await self._db.flush()

        logger.info(
            "csv_uploaded",
            dataset_id=str(dataset_id),
            rows=meta.row_count,
            columns=meta.column_count,
            size_bytes=len(data),
        )

        return UploadResponse(dataset=DatasetOut.model_validate(dataset))

    # ── Query ─────────────────────────────────────────────────────────────────

    async def list_datasets(
        self,
        owner_id: uuid.UUID,
        dataset_type: DatasetType | None = None,
        project_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> DatasetListOut:
        q = select(Dataset).where(Dataset.owner_id == owner_id)
        count_q = select(func.count()).select_from(Dataset).where(Dataset.owner_id == owner_id)

        if dataset_type:
            q = q.where(Dataset.dataset_type == dataset_type)
            count_q = count_q.where(Dataset.dataset_type == dataset_type)
        if project_id:
            q = q.where(Dataset.project_id == project_id)
            count_q = count_q.where(Dataset.project_id == project_id)

        total = (await self._db.execute(count_q)).scalar_one()
        rows = (await self._db.execute(q.order_by(Dataset.created_at.desc()).limit(limit).offset(offset))).scalars().all()

        return DatasetListOut(
            total=total,
            items=[DatasetOut.model_validate(r) for r in rows],
        )

    async def get_dataset(
        self,
        dataset_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> UploadResponse:
        result = await self._db.execute(
            select(Dataset).where(Dataset.id == dataset_id, Dataset.owner_id == owner_id)
        )
        dataset = result.scalar_one_or_none()
        if dataset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

        presigned_url: str | None = None
        if dataset.status == DatasetStatus.READY:
            try:
                presigned_url = await self._storage.presigned_url(
                    bucket=dataset.s3_bucket,
                    key=dataset.s3_key,
                )
            except HTTPException:
                pass  # non-fatal — return dataset without download URL

        return UploadResponse(
            dataset=DatasetOut.model_validate(dataset),
            presigned_download_url=presigned_url,
        )

    async def delete_dataset(
        self,
        dataset_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> None:
        result = await self._db.execute(
            select(Dataset).where(Dataset.id == dataset_id, Dataset.owner_id == owner_id)
        )
        dataset = result.scalar_one_or_none()
        if dataset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

        await self._storage.delete(dataset.s3_bucket, dataset.s3_key)
        await self._db.delete(dataset)
        await self._db.flush()
