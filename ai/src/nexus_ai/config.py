"""
NEXUS-MIND AI Backend — Application Settings
Loaded from environment variables / .env file using pydantic-settings v2.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "nexus-mind-ai"
    APP_VERSION: str = "0.1.0"
    ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Server ───────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    WORKERS: int = 1
    ROOT_PATH: str = ""

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: PostgresDsn | str = Field(
        default="postgresql+asyncpg://nexus:nexus@localhost:5432/nexusmind"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE_SECONDS: int = 3600
    DB_ECHO: bool = False

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: RedisDsn | str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = 50

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(default="change-me-in-production-use-openssl-rand-hex-64")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 200
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Object Storage (S3 / MinIO) ────────────────────────────────────────
    S3_ENDPOINT_URL: str | None = None           # None → real AWS S3
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_REGION: str = "ap-south-1"
    S3_BUCKET_RAW: str = "nexus-raw"
    S3_BUCKET_PROCESSED: str = "nexus-processed"
    S3_BUCKET_ML: str = "nexus-ml"

    # ── ML / Model ────────────────────────────────────────────────────────────
    MODEL_REGISTRY_PATH: str = "models/"
    INFERENCE_BATCH_SIZE: int = 64
    DEVICE: Literal["cpu", "cuda", "mps"] = "cpu"

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "text"

    # ── Downstream Services ───────────────────────────────────────────────────
    GATEWAY_URL: str = "http://localhost:8000"

    # ── Celery ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def database_url_str(self) -> str:
        return str(self.DATABASE_URL)


@lru_cache
def get_settings() -> Settings:
    return Settings()
