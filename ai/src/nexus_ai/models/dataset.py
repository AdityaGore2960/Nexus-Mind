"""
Dataset ORM model — tracks uploaded geospatial and tabular datasets.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from nexus_ai.db.session import Base


class DatasetType(str, enum.Enum):
    GEOTIFF = "geotiff"
    CSV = "csv"


class DatasetStatus(str, enum.Enum):
    PENDING = "pending"         # upload queued or in progress
    PROCESSING = "processing"   # metadata extraction / tiling running
    READY = "ready"             # available for ML pipelines
    FAILED = "failed"           # processing error


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Ownership
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    # File identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    dataset_type: Mapped[DatasetType] = mapped_column(
        Enum(DatasetType, name="dataset_type", create_constraint=True),
        nullable=False,
        index=True,
    )
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus, name="dataset_status", create_constraint=True),
        nullable=False,
        default=DatasetStatus.PENDING,
        server_default=DatasetStatus.PENDING.value,
        index=True,
    )

    # Storage
    s3_bucket: Mapped[str] = mapped_column(String(255), nullable=False)
    s3_key: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(127), nullable=False)

    # Extracted metadata (structure varies per dataset_type)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    # Geospatial extent (populated for GeoTIFFs after processing)
    extent: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326),
        nullable=True,
    )

    # Error details on failure
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )

    __table_args__ = (
        Index("ix_datasets_owner_type", "owner_id", "dataset_type"),
        Index("ix_datasets_project_status", "project_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Dataset id={self.id} name={self.name!r} type={self.dataset_type} status={self.status}>"
