"""
Async S3/MinIO storage service.
boto3 is synchronous; we offload all S3 calls to a thread via
anyio.to_thread.run_sync() to avoid blocking the asyncio event loop.
"""
from __future__ import annotations

import functools
import io
from typing import Any

import anyio
import boto3
import structlog
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, status

from nexus_ai.config import Settings

logger = structlog.get_logger(__name__)


class StorageService:
    """Thin async wrapper around boto3 S3 operations."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = self._build_client()

    def _build_client(self):
        kwargs: dict[str, Any] = {
            "region_name": self._settings.S3_REGION,
            "aws_access_key_id": self._settings.S3_ACCESS_KEY,
            "aws_secret_access_key": self._settings.S3_SECRET_KEY,
        }
        if self._settings.S3_ENDPOINT_URL:          # MinIO / localstack
            kwargs["endpoint_url"] = self._settings.S3_ENDPOINT_URL
        return boto3.client("s3", **kwargs)

    # ── Internal sync helpers (run in thread) ─────────────────────────────────

    def _upload_bytes(self, data: bytes, bucket: str, key: str, content_type: str) -> None:
        self._client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    def _generate_presigned_url(self, bucket: str, key: str, expires: int) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires,
        )

    def _delete_object(self, bucket: str, key: str) -> None:
        self._client.delete_object(Bucket=bucket, Key=key)

    # ── Public async API ──────────────────────────────────────────────────────

    async def upload(
        self,
        data: bytes,
        bucket: str,
        key: str,
        content_type: str,
    ) -> None:
        """Upload *data* to S3 at *bucket/key*. Non-blocking."""
        try:
            await anyio.to_thread.run_sync(
                functools.partial(self._upload_bytes, data, bucket, key, content_type)
            )
            logger.info("s3_upload_ok", bucket=bucket, key=key, size=len(data))
        except (BotoCoreError, ClientError) as exc:
            logger.error("s3_upload_failed", bucket=bucket, key=key, error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Object storage upload failed. Please retry.",
            ) from exc

    async def presigned_url(
        self,
        bucket: str,
        key: str,
        expires: int = 3600,
    ) -> str:
        """Return a presigned GET URL valid for *expires* seconds."""
        try:
            return await anyio.to_thread.run_sync(
                functools.partial(self._generate_presigned_url, bucket, key, expires)
            )
        except (BotoCoreError, ClientError) as exc:
            logger.warning("s3_presign_failed", bucket=bucket, key=key, error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not generate download URL.",
            ) from exc

    async def delete(self, bucket: str, key: str) -> None:
        """Delete *bucket/key* — ignores 'key not found' errors."""
        try:
            await anyio.to_thread.run_sync(
                functools.partial(self._delete_object, bucket, key)
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "NoSuchKey":
                logger.warning("s3_delete_failed", bucket=bucket, key=key, error=str(exc))
