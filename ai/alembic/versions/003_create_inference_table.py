"""create inference table

Revision ID: 003
Revises: 002
Create Date: 2026-05-22
"""
from __future__ import annotations

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    job_status = postgresql.ENUM("queued", "running", "completed", "failed", name="job_status", create_type=True)
    job_status.create(op.get_bind())

    op.create_table(
        "inference_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "area_of_interest",
            geoalchemy2.types.Geometry(
                geometry_type="POLYGON",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum("queued", "running", "completed", "failed", name="job_status", create_constraint=True),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("result_s3_key", sa.String(length=1024), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("shap_s3_key", sa.String(length=1024), nullable=True),
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

    op.create_index("ix_inference_jobs_owner_id", "inference_jobs", ["owner_id"])
    op.create_index("ix_inference_jobs_project_id", "inference_jobs", ["project_id"])
    op.create_index("ix_inference_project_status", "inference_jobs", ["project_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_inference_project_status", table_name="inference_jobs")
    op.drop_index("ix_inference_jobs_project_id", table_name="inference_jobs")
    op.drop_index("ix_inference_jobs_owner_id", table_name="inference_jobs")
    op.drop_table("inference_jobs")
    op.execute("DROP TYPE IF EXISTS job_status")
