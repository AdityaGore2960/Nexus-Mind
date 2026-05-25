"""
Geological and Terrain Feature Engineering Pipeline.
Calculates spectral indices and topographical derivations for mineral prospectivity.
"""
from __future__ import annotations

import geopandas as gpd  # type: ignore[import-untyped]
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from scipy.ndimage import gaussian_gradient_magnitude, sobel  # type: ignore[import-untyped]
from shapely.geometry import Point  # type: ignore[import-untyped]


class GeologyFeatureEngineer:
    """
    Computes derived geological and spectral features from base satellite 
    bands, elevation models, and vector data.
    """

    @staticmethod
    def calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """
        Calculate Normalized Difference Vegetation Index (NDVI).
        NDVI = (NIR - RED) / (NIR + RED)
        Vegetation obscures mineral signatures, so this is used to mask or weight areas.
        """
        # Prevent division by zero
        denominator = nir_band + red_band
        denominator[denominator == 0] = 1e-7
        
        ndvi = (nir_band - red_band) / denominator
        # Clip to valid range just in case of slight numerical noise
        return np.clip(ndvi, -1.0, 1.0)

    @staticmethod
    def calculate_iron_oxide(red_band: np.ndarray, blue_band: np.ndarray) -> np.ndarray:
        """
        Calculate Iron Oxide Index.
        Typically Red / Blue (or Red / Green depending on the satellite sensor).
        High values indicate gossans or oxidized alterations often associated with deposits.
        """
        blue_safe = blue_band.copy()
        blue_safe[blue_safe == 0] = 1e-7
        
        return red_band / blue_safe

    @staticmethod
    def calculate_clay_alteration(swir1_band: np.ndarray, swir2_band: np.ndarray) -> np.ndarray:
        """
        Calculate Clay Alteration Index (SWIR1 / SWIR2).
        Highlights argillic alteration zones common in porphyry and epithermal systems.
        """
        swir2_safe = swir2_band.copy()
        swir2_safe[swir2_safe == 0] = 1e-7
        
        return swir1_band / swir2_safe

    @staticmethod
    def calculate_terrain_features(dem: np.ndarray, resolution_x: float, resolution_y: float) -> tuple[np.ndarray, np.ndarray]:
        """
        Calculate Slope and Aspect from a Digital Elevation Model (DEM).
        Uses Sobel filters to approximate 2D derivatives.
        
        Returns:
            - slope: in degrees [0, 90]
            - aspect: in degrees [0, 360]
        """
        # Convert resolution to positive absolute values
        dx = abs(resolution_x)
        dy = abs(resolution_y)
        
        # Calculate gradients
        dz_dx = sobel(dem, axis=1) / (8.0 * dx)
        dz_dy = sobel(dem, axis=0) / (8.0 * dy)
        
        # Slope in radians, then converted to degrees
        slope_rad = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2))
        slope_deg = np.degrees(slope_rad)
        
        # Aspect in radians, then converted to degrees
        aspect_rad = np.arctan2(dz_dy, -dz_dx)
        aspect_deg = np.degrees(aspect_rad)
        
        # Normalize aspect to [0, 360]
        aspect_deg = np.where(aspect_deg < 0, 360 + aspect_deg, aspect_deg)
        
        return slope_deg, aspect_deg

    @staticmethod
    def calculate_fault_distance(df: pd.DataFrame, faults_gdf: gpd.GeoDataFrame, x_col: str = "x", y_col: str = "y") -> np.ndarray:
        """
        Calculate the Euclidean distance from each pixel to the nearest fault line.
        Requires the DataFrame to have x, y coordinates and the GeoDataFrame to be in
        the same projected CRS (so distances are in meters).
        """
        # Note: For very large rasters, iterating over points is slow.
        # A more optimal approach in production is using scipy.spatial.cKDTree 
        # or rasterizing the fault lines and computing a Euclidean Distance Map via OpenCV.
        
        # Union all fault lines into a single MultiLineString for faster nearest calculation
        unified_faults = faults_gdf.union_all() if hasattr(faults_gdf, "union_all") else faults_gdf.unary_union
        
        def _get_dist(row: pd.Series) -> float:
            return Point(row[x_col], row[y_col]).distance(unified_faults)
            
        return df.apply(_get_dist, axis=1).to_numpy()
