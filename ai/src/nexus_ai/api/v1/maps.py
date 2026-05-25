"""Geospatial map layer endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query, status
from pydantic import BaseModel

from nexus_ai.core.dependencies import CurrentUserId, DBSession

router = APIRouter()


class BoundingBox(BaseModel):
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float


class MapLayerOut(BaseModel):
    layer_id: str
    layer_type: str   # "satellite" | "geology" | "geochemistry" | "prospectivity"
    tile_url: str
    metadata: dict


@router.get("/{project_id}/layers", response_model=list[MapLayerOut])
async def get_map_layers(
    project_id: str,
    db: DBSession,
    user_id: CurrentUserId,
) -> list[MapLayerOut]:
    """Return all map layers associated with a project."""
    # TODO: delegate to MapService
    return []


@router.get("/{project_id}/prospectivity-grid")
async def get_prospectivity_grid(
    project_id: str,
    min_lon: float = Query(...),
    min_lat: float = Query(...),
    max_lon: float = Query(...),
    max_lat: float = Query(...),
    db: DBSession = ...,
    user_id: CurrentUserId = ...,
):
    """
    Return a GeoJSON FeatureCollection of prospectivity prediction cells
    clipped to the supplied bounding box.
    """
    # TODO: delegate to MapService
    return {"type": "FeatureCollection", "features": []}
