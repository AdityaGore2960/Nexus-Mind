"""
Machine learning preprocessing and feature engineering utilities.
"""
from __future__ import annotations

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sklearn.compose import ColumnTransformer  # type: ignore[import-untyped]
from sklearn.impute import SimpleImputer  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]


def build_preprocessor(numeric_features: list[str]) -> ColumnTransformer:
    """
    Build a scikit-learn preprocessing pipeline for numeric geospatial features.
    Handles missing values via median imputation and scales features to zero mean / unit variance.
    """
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
        ],
        remainder="passthrough"  # keep other columns as-is, if any
    )
    
    return preprocessor


def extract_spatial_features(df: pd.DataFrame, lat_col: str = "lat", lon_col: str = "lon") -> pd.DataFrame:
    """
    Generate derived spatial features (e.g. proximity, distance to structures)
    from coordinates, if applicable.
    """
    df_out = df.copy()
    
    # Example feature engineering: Distance to center of bounding box
    if lat_col in df.columns and lon_col in df.columns:
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Simple Euclidean distance as a proxy feature
        df_out["dist_to_center"] = np.sqrt(
            (df[lat_col] - center_lat)**2 + (df[lon_col] - center_lon)**2
        )
        
    return df_out
