"""
Geospatial processing utilities.
Handles reading GeoTIFFs, clipping, coordinate transformations,
normalization, and converting rasters to tabular data for ML.
"""
from __future__ import annotations

import io
from typing import Literal

import geopandas as gpd  # type: ignore[import-untyped]
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import rasterio  # type: ignore[import-untyped]
from rasterio.mask import mask  # type: ignore[import-untyped]
from rasterio.warp import calculate_default_transform, reproject, Resampling  # type: ignore[import-untyped]
from shapely.geometry import box  # type: ignore[import-untyped]


class GeoProcessor:
    """Pipeline for geospatial data extraction and manipulation."""

    @staticmethod
    def read_and_clip(
        raster_path_or_bytes: str | bytes, 
        bbox_wgs84: tuple[float, float, float, float],
        nodata_val: float = 0.0
    ) -> tuple[np.ndarray, rasterio.profiles.Profile]:
        """
        Reads a GeoTIFF and clips it to the specified WGS84 bounding box.
        Handles CRS reprojection of the bounding box if the raster is not in EPSG:4326.
        bbox_wgs84: (min_lon, min_lat, max_lon, max_lat)
        """
        source = io.BytesIO(raster_path_or_bytes) if isinstance(raster_path_or_bytes, bytes) else raster_path_or_bytes
        
        with rasterio.open(source) as src:
            raster_crs = src.crs
            
            # Create a GeoDataFrame for the bounding box in WGS84
            minx, miny, maxx, maxy = bbox_wgs84
            geom = box(minx, miny, maxx, maxy)
            gdf = gpd.GeoDataFrame({"geometry": [geom]}, crs="EPSG:4326")
            
            # Reproject clipping geometry to match raster CRS
            if raster_crs.to_epsg() != 4326:
                gdf = gdf.to_crs(raster_crs)
                
            # Clip the raster
            shapes = [feature["geometry"] for _, feature in gdf.iterrows()]
            out_image, out_transform = mask(src, shapes, crop=True, nodata=nodata_val)
            
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
            
            return out_image, out_meta

    @staticmethod
    def extract_bands(image_array: np.ndarray, bands: list[int] | None = None) -> np.ndarray:
        """
        Extract specific bands from a raster array (Channels, Height, Width).
        bands: 1-indexed list of bands to extract. If None, returns all.
        """
        if bands is None:
            return image_array
        
        # Convert 1-indexed to 0-indexed
        indices = [b - 1 for b in bands]
        return image_array[indices, :, :]

    @staticmethod
    def normalize_raster(
        image_array: np.ndarray, 
        method: Literal["minmax", "zscore"] = "zscore",
        nodata_val: float = 0.0
    ) -> np.ndarray:
        """
        Normalize raster bands. Ignores nodata values during calculation.
        """
        out_array = np.zeros_like(image_array, dtype=np.float32)
        
        for i in range(image_array.shape[0]):
            band = image_array[i].astype(np.float32)
            valid_mask = band != nodata_val
            
            if not valid_mask.any():
                continue # Skip entirely empty bands
                
            valid_data = band[valid_mask]
            
            if method == "minmax":
                b_min, b_max = valid_data.min(), valid_data.max()
                if b_max > b_min:
                    band[valid_mask] = (valid_data - b_min) / (b_max - b_min)
                else:
                    band[valid_mask] = 0.0
            elif method == "zscore":
                mean, std = valid_data.mean(), valid_data.std()
                if std > 0:
                    band[valid_mask] = (valid_data - mean) / std
                else:
                    band[valid_mask] = 0.0
                    
            out_array[i] = band
            
        return out_array

    @staticmethod
    def raster_to_dataframe(
        image_array: np.ndarray, 
        transform: rasterio.transform.Affine, 
        band_names: list[str] | None = None,
        nodata_val: float = 0.0
    ) -> pd.DataFrame:
        """
        Converts a spatial raster array (C, H, W) into a tabular pandas DataFrame.
        Each row represents a valid pixel with 'x' and 'y' spatial coordinates.
        This is required for feeding spatial data into XGBoost/Random Forest.
        """
        c, h, w = image_array.shape
        
        if band_names is None:
            band_names = [f"band_{i+1}" for i in range(c)]
            
        if len(band_names) != c:
            raise ValueError(f"Provided {len(band_names)} band names but image has {c} bands.")

        # Create coordinate grids
        cols, rows = np.meshgrid(np.arange(w), np.arange(h))
        
        # Transform pixel indices to spatial coordinates
        xs, ys = rasterio.transform.xy(transform, rows.flatten(), cols.flatten())
        
        # Flatten image bands
        flattened_bands = {name: image_array[i].flatten() for i, name in enumerate(band_names)}
        
        # Build DataFrame
        df = pd.DataFrame({
            "x": xs,
            "y": ys,
            **flattened_bands
        })
        
        # Filter out nodata pixels (assuming all bands are nodata if the first is nodata, for efficiency)
        df = df[df[band_names[0]] != nodata_val].reset_index(drop=True)
        
        return df
