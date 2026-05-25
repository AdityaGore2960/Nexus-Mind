"""create datasets table

Revision ID: 002
Revises: 001
Create Date: 2026-05-22
"""
from __future__ import annotations

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enums
    dataset_type = postgresql.ENUM("geotiff", "csv", name="dataset_type", create_type=True)
    dataset_type.create(op.get_bind())

    dataset_status = postgresql.ENUM(
        "pending", "processing", "ready", "failed", name="dataset_status", create_type=True
    )
    dataset_status.create(op.get_bind())

    op.create_table(
        "datasets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column(
            "dataset_type",
            sa.Enum("geotiff", "csv", name="dataset_type", create_constraint=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "ready", "failed", name="dataset_status", create_constraint=True),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("s3_bucket", sa.String(255), nullable=False),
        sa.Column("s3_key", sa.String(1024), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("content_type", sa.String(127), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "extent",
            geoalchemy2.types.Geometry(
                geometry_type="POLYGON",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=True,
            ),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
    )

    op.create_index("ix_datasets_owner_id", "datasets", ["owner_id"])
    op.create_index("ix_datasets_project_id", "datasets", ["project_id"])
    op.create_index("ix_datasets_s3_key", "datasets", ["s3_key"], unique=True)
    op.create_index("ix_datasets_owner_type", "datasets", ["owner_id", "dataset_type"])
    op.create_index("ix_datasets_project_status", "datasets", ["project_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_datasets_project_status", table_name="datasets")
    op.drop_index("ix_datasets_owner_type", table_name="datasets")
    op.drop_index("ix_datasets_s3_key", table_name="datasets")
    op.drop_index("ix_datasets_project_id", table_name="datasets")
    op.drop_index("ix_datasets_owner_id", table_name="datasets")
    op.drop_table("datasets")
    op.execute("DROP TYPE IF EXISTS dataset_status")
    op.execute("DROP TYPE IF EXISTS dataset_type")
