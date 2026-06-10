# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 gdal-bin libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /build/
COPY src /build/src

RUN pip install --no-cache-dir --prefix=/install -e ".[standard]" \
    && pip install --no-cache-dir --prefix=/install -e /build


# ── Production stage ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash nexus

USER nexus
WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=nexus:nexus src /app/src

ENV PYTHONPATH="/app/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/api/v1/health')"

CMD ["uvicorn", "nexus_ai.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8001", \
    "--workers", "2", \
    "--loop", "uvloop", \
    "--http", "httptools", \
    "--no-access-log"]
