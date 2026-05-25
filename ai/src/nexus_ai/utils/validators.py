"""
File validation utilities — enforce type, magic bytes, and size limits
before any I/O is performed.
"""
from __future__ import annotations

import io

from fastapi import HTTPException, UploadFile, status

# ── Limits ─────────────────────────────────────────────────────────────────────
MAX_GEOTIFF_BYTES = 2 * 1024 * 1024 * 1024   # 2 GB
MAX_CSV_BYTES = 500 * 1024 * 1024             # 500 MB

# ── Accepted MIME types ────────────────────────────────────────────────────────
GEOTIFF_CONTENT_TYPES = {
    "image/tiff",
    "image/geotiff",
    "image/geo+tiff",
    "application/octet-stream",  # many clients send this for .tif
}
CSV_CONTENT_TYPES = {
    "text/csv",
    "text/plain",
    "application/csv",
    "application/octet-stream",
}

# ── Magic byte signatures ──────────────────────────────────────────────────────
# TIFF little-endian: 49 49 2A 00  |  big-endian: 4D 4D 00 2A
_TIFF_MAGIC = {b"\x49\x49\x2a\x00", b"\x4d\x4d\x00\x2a"}
_CSV_SNIFF_BYTES = 4096   # inspect first 4 KB


def _read_header(file: UploadFile, n: int) -> bytes:
    """Read *n* bytes from the file, then seek back to 0."""
    header = file.file.read(n)
    file.file.seek(0)
    return header


async def validate_geotiff(file: UploadFile) -> None:
    """
    Raise HTTP 422 if *file* is not a valid GeoTIFF, or exceeds size limit.
    Leaves the file cursor at position 0.
    """
    # Content-Type hint (not authoritative, but catches obvious mistakes)
    if file.content_type not in GEOTIFF_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid content type '{file.content_type}'. Expected a TIFF file.",
        )

    header = _read_header(file, 4)
    if len(header) < 4 or header[:4] not in _TIFF_MAGIC:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File magic bytes do not match TIFF format.",
        )

    # Size — stream-count without loading fully into memory
    total = _count_size(file)
    if total > MAX_GEOTIFF_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"GeoTIFF exceeds maximum size of {MAX_GEOTIFF_BYTES // (1024**2)} MB.",
        )


async def validate_csv(file: UploadFile) -> None:
    """
    Raise HTTP 422 if *file* is not parseable as CSV, or exceeds size limit.
    Leaves the file cursor at position 0.
    """
    if file.content_type not in CSV_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid content type '{file.content_type}'. Expected a CSV file.",
        )

    sample = _read_header(file, _CSV_SNIFF_BYTES)
    try:
        text = sample.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File is not valid UTF-8 text. CSV must be UTF-8 encoded.",
        )

    if "," not in text and "\t" not in text and ";" not in text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File does not appear to be delimited (no comma, tab, or semicolon found).",
        )

    total = _count_size(file)
    if total > MAX_CSV_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"CSV exceeds maximum size of {MAX_CSV_BYTES // (1024**2)} MB.",
        )


def _count_size(file: UploadFile) -> int:
    """Count total bytes by reading in chunks; seek back to 0."""
    total = 0
    chunk_size = 65_536  # 64 KB
    while chunk := file.file.read(chunk_size):
        total += len(chunk)
    file.file.seek(0)
    return total
