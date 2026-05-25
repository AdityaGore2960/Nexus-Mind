"""
Random Forest Pipeline for Mineral Prospectivity Prediction.
Combines preprocessing and the ensemble ML model into a single scikit-learn Pipeline.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sklearn.ensemble import RandomForestClassifier  # type: ignore[import-untyped]
from sklearn.metrics import classification_report, roc_auc_score  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]

from nexus_ai.ml.preprocessing import build_preprocessor, extract_spatial_features


class RFPipeline:
    """
    End-to-End Random Forest Pipeline managing preprocessing, training, 
    evaluation, and inference for mineral prospectivity.
    """

    def __init__(self, numeric_features: list[str], random_state: int = 42):
        self.numeric_features = numeric_features
        self.random_state = random_state
        
        # Build the scikit-learn pipeline
        preprocessor = build_preprocessor(numeric_features)
        
        self.model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                (
                    "classifier", 
                    RandomForestClassifier(
                        n_estimators=200,
                        max_depth=15,
                        class_weight="balanced",
                        random_state=self.random_state,
                        n_jobs=-1  # Use all cores
                    )
                )
            ]
        )
        self._is_trained = False

    def train(self, df_train: pd.DataFrame, target_col: str) -> None:
        """Train the model pipeline on historical geospatial features."""
        # 1. Feature Engineering
        df_processed = extract_spatial_features(df_train)
        
        # 2. Split X and y
        X = df_processed[self.numeric_features + ["dist_to_center"]] if "dist_to_center" in df_processed else df_processed[self.numeric_features]
        y = df_processed[target_col]

        # 3. Fit
        self.model.fit(X, y)
        self._is_trained = True

    def evaluate(self, df_test: pd.DataFrame, target_col: str) -> dict[str, Any]:
        """Evaluate the model and return metrics."""
        if not self._is_trained:
            raise RuntimeError("Model must be trained before evaluation.")

        df_processed = extract_spatial_features(df_test)
        X = df_processed[self.numeric_features + ["dist_to_center"]] if "dist_to_center" in df_processed else df_processed[self.numeric_features]
        y_true = df_processed[target_col]

        y_pred = self.model.predict(X)
        y_proba = self.model.predict_proba(X)[:, 1]

        report = classification_report(y_true, y_pred, output_dict=True)
        roc_auc = roc_auc_score(y_true, y_proba)

        return {
            "classification_report": report,
            "roc_auc": roc_auc
        }

    def predict(self, df_inference: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        """
        Run inference on new data.
        Returns: (predictions, probabilities)
        """
        if not self._is_trained:
            raise RuntimeError("Model must be trained or loaded before inference.")

        df_processed = extract_spatial_features(df_inference)
        X = df_processed[self.numeric_features + ["dist_to_center"]] if "dist_to_center" in df_processed else df_processed[self.numeric_features]

        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]

        return predictions, probabilities

    def get_feature_importances(self) -> dict[str, float]:
        """Extract feature importances from the Random Forest model."""
        if not self._is_trained:
            raise RuntimeError("Model is not trained.")
            
        rf_model = self.model.named_steps["classifier"]
        
        # For simplicity, assuming the preprocessor keeps feature order exactly (no one-hot encoding changing dimension)
        # In a real scenario, getting feature names out of ColumnTransformer can be complex.
        features = self.numeric_features
        if "dist_to_center" in rf_model.feature_names_in_:
            features.append("dist_to_center")
            
        importances = rf_model.feature_importances_
        
        return dict(zip(features, importances))

    def save(self, filepath: str | Path) -> None:
        """Persist the trained pipeline to disk using joblib."""
        if not self._is_trained:
            raise RuntimeError("Cannot save an untrained model.")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "numeric_features": self.numeric_features,
            }, 
            filepath
        )

    @classmethod
    def load(cls, filepath: str | Path) -> RFPipeline:
        """Load a trained pipeline from disk."""
        data = joblib.load(filepath)
        
        # Instantiate empty class and overwrite
        instance = cls(numeric_features=data["numeric_features"])
        instance.model = data["model"]
        instance._is_trained = True
        return instance
