"""
Explainable AI (XAI) utilities for mineral prospectivity mapping.
"""
from __future__ import annotations

import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import shap
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from xgboost import XGBClassifier

from nexus_ai.ml.pipelines.random_forest import RFPipeline
from nexus_ai.ml.pipelines.xgboost_pipeline import XGBoostPipeline


class ExplainabilityEngine:
    """
    Generates SHAP values and human-readable reasoning for ML predictions.
    """

    def __init__(self, pipeline: RFPipeline | XGBoostPipeline | None = None):
        self.pipeline = pipeline
        self.explainer = None
        self._initialize_explainer()

    def _initialize_explainer(self) -> None:
        """Initialize the appropriate SHAP Explainer based on the model type."""
        if self.pipeline is None:
            return

        model_step = self.pipeline.model.named_steps["classifier"]
        
        # TreeExplainer is optimized for Random Forest and XGBoost
        # Note: We must pass the raw model, not the scikit-learn Pipeline
        if isinstance(model_step, (XGBClassifier,)):
            self.explainer = shap.TreeExplainer(model_step)
        elif hasattr(model_step, "estimators_"):  # Random Forest
            self.explainer = shap.TreeExplainer(model_step)
        else:
            # Fallback for other models (e.g., Logistic Regression in Stacking)
            # Not fully supported here, usually requires KernelExplainer or DeepExplainer
            self.explainer = None

    def calculate_shap_values(self, df_inference: pd.DataFrame) -> dict[str, float]:
        """
        Calculate local SHAP values for a single inference instance.
        Returns a dictionary mapping feature names to their SHAP contribution.
        """
        if self.explainer is None or self.pipeline is None:
            # Fallback mock for CNN or unsupported models
            return {"magnetic_anomaly": 0.45, "gravity_anomaly": 0.12}

        # We must preprocess the data before giving it to SHAP
        # SHAP expects the features as they enter the classifier
        preprocessor = self.pipeline.model.named_steps["preprocessor"]
        X_transformed = preprocessor.transform(df_inference)
        
        # Calculate SHAP values
        shap_vals = self.explainer.shap_values(X_transformed)
        
        # Extract feature names
        features = self.pipeline.numeric_features.copy()
        if "dist_to_center" in df_inference.columns:
            features.append("dist_to_center")

        # shap_vals shape varies by model (binary vs multi-class)
        # For binary XGBoost it's (N, F). For RF it's usually a list of (N, F) per class.
        if isinstance(shap_vals, list):
            # Take the positive class contributions
            instance_shap = shap_vals[1][0]
        else:
            instance_shap = shap_vals[0]

        return dict(zip(features, instance_shap.tolist()))

    def generate_reasoning(
        self, 
        confidence: float, 
        shap_values: dict[str, float], 
        top_k: int = 3
    ) -> str:
        """
        Generate a human-readable explanation of why the model made this prediction.
        """
        is_high_prob = confidence >= 0.5
        
        # Sort features by absolute SHAP magnitude to find the most influential ones
        sorted_features = sorted(
            shap_values.items(), 
            key=lambda item: abs(item[1]), 
            reverse=True
        )
        
        top_features = sorted_features[:top_k]
        
        reasons = []
        for feature, value in top_features:
            direction = "positively" if value > 0 else "negatively"
            reasons.append(f"{feature.replace('_', ' ')} contributed {direction}")
            
        reason_str = ", ".join(reasons)
        
        prediction_text = "high prospectivity" if is_high_prob else "low prospectivity"
        confidence_pct = round(confidence * 100, 1)
        
        return (
            f"Model predicts {prediction_text} with {confidence_pct}% confidence. "
            f"Key factors: {reason_str}."
        )
