"""
Celery App Configuration
"""
from __future__ import annotations

import os

from celery import Celery

# Load default config via pydantic if environment variables aren't set
from nexus_ai.config import get_settings

settings = get_settings()

celery_app = Celery(
    "nexus_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["nexus_ai.tasks.ml_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per job
)
