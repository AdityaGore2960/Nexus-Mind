"""
Pydantic v2 schemas for dataset upload and retrieval.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from nexus_ai.models.dataset import DatasetStatus, DatasetType


# ── Shared metadata sub-schemas ───────────────────────────────────────────────

class GeoTIFFMetadata(BaseModel):
    """Extracted from rasterio."""
    crs: str                            # e.g. "EPSG:4326"
    crs_is_geographic: bool
    width: int                          # pixels
    height: int                         # pixels
    band_count: int
    dtype: str                          # e.g. "float32"
    nodata: float | None
    resolution_x: float                 # units depend on CRS
    resolution_y: float
    bbox: dict[str, float]              # {min_lon, min_lat, max_lon, max_lat}
    compression: str | None
    driver: str                         # e.g. "GTiff"


class CSVMetadata(BaseModel):
    """Extracted from pandas."""
    row_count: int
    column_count: int
    columns: list[str]
    dtypes: dict[str, str]              # col → pandas dtype name
    null_counts: dict[str, int]
    has_geometry: bool                  # True if lat/lon/geometry columns found
    geometry_columns: list[str]
    numeric_columns: list[str]
    sample_rows: list[dict[str, Any]]   # first 3 rows for preview


# ── Request schemas ────────────────────────────────────────────────────────────

class DatasetUploadQuery(BaseModel):
    """Query params injected alongside the multipart file."""
    name: str = Field(..., min_length=1, max_length=255)
    project_id: uuid.UUID | None = None
    description: str | None = Field(None, max_length=1024)


# ── Response schemas ───────────────────────────────────────────────────────────

class DatasetOut(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    project_id: uuid.UUID | None
    name: str
    original_filename: str
    dataset_type: DatasetType
    status: DatasetStatus
    s3_bucket: str
    s3_key: str
    file_size_bytes: int
    content_type: str
    metadata_: dict | None = Field(None, alias="metadata")
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class DatasetListOut(BaseModel):
    total: int
    items: list[DatasetOut]


class UploadResponse(BaseModel):
    dataset: DatasetOut
    presigned_download_url: str | None = None   # populated when status=READY
