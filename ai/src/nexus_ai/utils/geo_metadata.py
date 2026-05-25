"""
Metadata extraction from GeoTIFF (rasterio) and CSV (pandas).
All functions are synchronous (CPU-bound); callers must use
anyio.to_thread.run_sync() to avoid blocking the event loop.
"""
from __future__ import annotations

import io
from typing import Any

from nexus_ai.schemas.dataset import CSVMetadata, GeoTIFFMetadata

# ── GeoTIFF ────────────────────────────────────────────────────────────────────

def extract_geotiff_metadata(data: bytes) -> GeoTIFFMetadata:
    """
    Parse *data* as a GeoTIFF and return typed metadata.
    Raises ValueError on any rasterio error (caller maps to HTTP 422).
    """
    import rasterio
    from rasterio.crs import CRS
    from rasterio.errors import RasterioError
    from rasterio.transform import array_bounds

    try:
        with rasterio.open(io.BytesIO(data)) as src:
            crs: CRS = src.crs or CRS.from_epsg(4326)

            transform = src.transform
            bounds = src.bounds

            # Reproject bounds to WGS-84 for a canonical bbox
            from rasterio.warp import transform_bounds
            if crs.to_epsg() != 4326:
                west, south, east, north = transform_bounds(
                    crs, "EPSG:4326",
                    bounds.left, bounds.bottom, bounds.right, bounds.top,
                )
            else:
                west, south, east, north = bounds.left, bounds.bottom, bounds.right, bounds.top

            return GeoTIFFMetadata(
                crs=crs.to_string(),
                crs_is_geographic=crs.is_geographic,
                width=src.width,
                height=src.height,
                band_count=src.count,
                dtype=str(src.dtypes[0]),
                nodata=float(src.nodata) if src.nodata is not None else None,
                resolution_x=abs(float(transform.a)),
                resolution_y=abs(float(transform.e)),
                bbox={
                    "min_lon": west,
                    "min_lat": south,
                    "max_lon": east,
                    "max_lat": north,
                },
                compression=src.compression.name if src.compression else None,
                driver=src.driver,
            )
    except (RasterioError, Exception) as exc:
        raise ValueError(f"Failed to read GeoTIFF: {exc}") from exc


def geotiff_extent_wkt(bbox: dict[str, float]) -> str:
    """
    Convert a bbox dict to a WKT POLYGON string for PostGIS storage.
    bbox keys: min_lon, min_lat, max_lon, max_lat
    """
    w, s, e, n = bbox["min_lon"], bbox["min_lat"], bbox["max_lon"], bbox["max_lat"]
    return (
        f"POLYGON(({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))"
    )


# ── CSV ────────────────────────────────────────────────────────────────────────

_GEO_COLUMN_HINTS = {
    "lat", "latitude", "lon", "lng", "longitude",
    "x", "y", "geometry", "geom", "wkt", "wkb",
    "easting", "northing",
}


def extract_csv_metadata(data: bytes) -> CSVMetadata:
    """
    Parse *data* as a CSV and return typed metadata.
    Raises ValueError on parse failure.
    """
    import pandas as pd  # type: ignore[import-untyped]

    try:
        # Auto-detect delimiter
        sample = data[:4096].decode("utf-8", errors="replace")
        sep = _sniff_delimiter(sample)

        df = pd.read_csv(io.BytesIO(data), sep=sep, low_memory=False)
    except Exception as exc:
        raise ValueError(f"Failed to parse CSV: {exc}") from exc

    columns = df.columns.tolist()
    dtypes = {col: str(df[col].dtype) for col in columns}
    null_counts = {col: int(df[col].isna().sum()) for col in columns}

    lower_cols = {c.lower() for c in columns}
    geo_cols = [c for c in columns if c.lower() in _GEO_COLUMN_HINTS]
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    # Safe sample — replace NaN with None for JSON serialisation
    head = df.head(3)
    sample_rows: list[dict[str, Any]] = [
        {str(col): (None if pd.isna(val) else val) for col, val in row.items()}
        for row in head.to_dict(orient="records")
    ]

    return CSVMetadata(
        row_count=len(df),
        column_count=len(columns),
        columns=columns,
        dtypes=dtypes,
        null_counts=null_counts,
        has_geometry=bool(geo_cols),
        geometry_columns=geo_cols,
        numeric_columns=numeric_cols,
        sample_rows=sample_rows,
    )


def _sniff_delimiter(sample: str) -> str:
    """Heuristic delimiter detection: comma > tab > semicolon > pipe."""
    counts = {
        ",": sample.count(","),
        "\t": sample.count("\t"),
        ";": sample.count(";"),
        "|": sample.count("|"),
    }
    return max(counts, key=counts.get)  # type: ignore[arg-type]
