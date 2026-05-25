"""
Ensemble Learning Pipeline.
Combines CNN (vision) and Tree-based (Random Forest, XGBoost) models.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]

from nexus_ai.ml.pipelines.cnn_pipeline import CNNPipeline
from nexus_ai.ml.pipelines.random_forest import RFPipeline
from nexus_ai.ml.pipelines.xgboost_pipeline import XGBoostPipeline


class EnsemblePipeline:
    """
    Combines predictions from multiple models using weighted averaging 
    or a trained meta-classifier (stacking).
    """

    def __init__(
        self,
        cnn_pipeline: CNNPipeline | None = None,
        xgb_pipeline: XGBoostPipeline | None = None,
        rf_pipeline: RFPipeline | None = None,
        method: str = "weighted",  # "weighted" or "stacking"
        weights: dict[str, float] | None = None
    ):
        self.cnn = cnn_pipeline
        self.xgb = xgb_pipeline
        self.rf = rf_pipeline
        self.method = method
        
        # Default weights if not provided
        self.weights = weights or {"cnn": 0.5, "xgb": 0.3, "rf": 0.2}
        
        # Meta-learner for stacking
        self.meta_learner = LogisticRegression()
        self._is_stacked_trained = False

    def train_stacking(self, df_tabular: pd.DataFrame, cnn_dataloader: Any, y_true: np.ndarray) -> None:
        """
        Train the meta-learner using out-of-fold predictions from base models.
        (Requires base models to already be trained).
        """
        if self.method != "stacking":
            raise ValueError("Method must be 'stacking' to train meta-learner.")
            
        base_preds = self._get_base_probabilities(df_tabular, cnn_dataloader)
        
        # Stack probabilities horizontally: shape (N_samples, N_models)
        X_meta = np.column_stack(list(base_preds.values()))
        
        self.meta_learner.fit(X_meta, y_true)
        self._is_stacked_trained = True

    def _get_base_probabilities(self, df_tabular: pd.DataFrame | None, cnn_dataloader: Any | None) -> dict[str, np.ndarray]:
        """Helper to collect probabilities from all available base models."""
        preds = {}
        
        if self.cnn is not None and cnn_dataloader is not None:
            cnn_probs, _ = self.cnn.predict(cnn_dataloader)
            preds["cnn"] = np.array(cnn_probs)
            
        if self.xgb is not None and df_tabular is not None:
            _, xgb_probs = self.xgb.predict(df_tabular)
            preds["xgb"] = xgb_probs
            
        if self.rf is not None and df_tabular is not None:
            _, rf_probs = self.rf.predict(df_tabular)
            preds["rf"] = rf_probs
            
        return preds

    def predict(self, df_tabular: pd.DataFrame | None, cnn_dataloader: Any | None) -> tuple[np.ndarray, np.ndarray]:
        """
        Run ensemble inference.
        Returns: (predictions, probabilities)
        """
        base_preds = self._get_base_probabilities(df_tabular, cnn_dataloader)
        
        if not base_preds:
            raise RuntimeError("No models available for prediction or missing input data.")

        if self.method == "stacking":
            if not self._is_stacked_trained:
                raise RuntimeError("Meta-learner is not trained.")
            
            X_meta = np.column_stack([base_preds[k] for k in ["cnn", "xgb", "rf"] if k in base_preds])
            probabilities = self.meta_learner.predict_proba(X_meta)[:, 1]
            
        else:
            # Weighted Average
            probabilities = np.zeros(len(list(base_preds.values())[0]))
            total_weight = sum(self.weights[k] for k in base_preds.keys())
            
            for k, probs in base_preds.items():
                normalized_weight = self.weights[k] / total_weight
                probabilities += probs * normalized_weight

        predictions = (probabilities > 0.5).astype(int)
        return predictions, probabilities

    def save(self, filepath: str | Path) -> None:
        """Save ensemble configuration and meta-learner."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "method": self.method,
            "weights": self.weights,
            "meta_learner": self.meta_learner if self._is_stacked_trained else None,
            "is_stacked_trained": self._is_stacked_trained
        }, filepath)

    @classmethod
    def load(
        cls, 
        filepath: str | Path, 
        cnn: CNNPipeline | None = None,
        xgb: XGBoostPipeline | None = None,
        rf: RFPipeline | None = None
    ) -> EnsemblePipeline:
        """Load ensemble config and attach loaded base models."""
        data = joblib.load(filepath)
        
        instance = cls(
            cnn_pipeline=cnn,
            xgb_pipeline=xgb,
            rf_pipeline=rf,
            method=data["method"],
            weights=data["weights"]
        )
        
        if data["meta_learner"] is not None:
            instance.meta_learner = data["meta_learner"]
            instance._is_stacked_trained = data["is_stacked_trained"]
            
        return instance
