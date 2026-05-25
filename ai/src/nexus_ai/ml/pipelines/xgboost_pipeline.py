"""
XGBoost Pipeline for Mineral Prospectivity Prediction.
Includes hyperparameter tuning, cross-validation, and feature importance.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sklearn.metrics import classification_report, roc_auc_score  # type: ignore[import-untyped]
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold  # type: ignore[import-untyped]
from sklearn.pipeline import Pipeline  # type: ignore[import-untyped]
from xgboost import XGBClassifier

from nexus_ai.ml.preprocessing import build_preprocessor, extract_spatial_features


class XGBoostPipeline:
    """
    End-to-End XGBoost Pipeline managing preprocessing, hyperparameter tuning,
    training, evaluation, and inference for mineral prospectivity.
    """

    def __init__(self, numeric_features: list[str], random_state: int = 42):
        self.numeric_features = numeric_features
        self.random_state = random_state
        
        preprocessor = build_preprocessor(numeric_features)
        
        # Base XGBoost model
        # scale_pos_weight is typically used instead of class_weight="balanced" in XGBoost
        # We start with scale_pos_weight=1.0 and let hyperparameter tuning optimize it if needed.
        base_xgb = XGBClassifier(
            objective="binary:logistic",
            eval_metric="auc",
            random_state=self.random_state,
            n_jobs=-1,
            use_label_encoder=False
        )
        
        self.model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("classifier", base_xgb)
            ]
        )
        self._is_trained = False
        self.cv_results_ = None
        self.best_params_ = None

    def _prepare_data(self, df: pd.DataFrame, target_col: str | None = None) -> tuple[pd.DataFrame, pd.Series | None]:
        """Apply spatial feature extraction and subset columns."""
        df_processed = extract_spatial_features(df)
        features = self.numeric_features.copy()
        if "dist_to_center" in df_processed.columns:
            features.append("dist_to_center")
            
        X = df_processed[features]
        y = df_processed[target_col] if target_col else None
        return X, y

    def tune_hyperparameters(
        self, 
        df_train: pd.DataFrame, 
        target_col: str, 
        n_iter: int = 20, 
        cv: int = 5
    ) -> dict[str, Any]:
        """
        Perform randomized search cross-validation to find the best hyperparameters.
        """
        X, y = self._prepare_data(df_train, target_col)
        
        # Calculate a dynamic scale_pos_weight for imbalanced classes
        neg_count = int(np.sum(y == 0))
        pos_count = int(np.sum(y == 1))
        default_scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0

        # Define the hyperparameter search space
        param_distributions = {
            "classifier__n_estimators": [100, 200, 300, 500],
            "classifier__learning_rate": [0.01, 0.05, 0.1, 0.2],
            "classifier__max_depth": [3, 5, 7, 9],
            "classifier__subsample": [0.6, 0.8, 1.0],
            "classifier__colsample_bytree": [0.6, 0.8, 1.0],
            "classifier__min_child_weight": [1, 3, 5],
            "classifier__scale_pos_weight": [1.0, default_scale_pos_weight, default_scale_pos_weight * 2]
        }

        # Stratified K-Fold ensures class distribution is preserved across folds
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=self.random_state)
        
        search = RandomizedSearchCV(
            estimator=self.model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            scoring="roc_auc",
            cv=skf,
            verbose=1,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        search.fit(X, y)
        
        self.model = cast(Pipeline, search.best_estimator_)
        self._is_trained = True
        self.best_params_ = search.best_params_
        self.cv_results_ = search.cv_results_
        
        return {
            "best_score_auc": search.best_score_,
            "best_params": self.best_params_
        }

    def train(self, df_train: pd.DataFrame, target_col: str) -> None:
        """Train the model with default hyperparameters."""
        X, y = self._prepare_data(df_train, target_col)
        self.model.fit(X, y)
        self._is_trained = True

    def evaluate(self, df_test: pd.DataFrame, target_col: str) -> dict[str, Any]:
        """Evaluate the model on a test set."""
        if not self._is_trained:
            raise RuntimeError("Model must be trained before evaluation.")

        X, y_true = self._prepare_data(df_test, target_col)
        assert y_true is not None, "y_true must not be None when target_col is provided"

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

        X, _ = self._prepare_data(df_inference)

        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]

        return predictions, probabilities

    def get_feature_importances(self, importance_type: str = "weight") -> dict[str, float]:
        """
        Extract feature importances from the XGBoost model.
        importance_type: 'weight', 'gain', or 'cover'
        """
        if not self._is_trained:
            raise RuntimeError("Model is not trained.")
            
        xgb_model: XGBClassifier = self.model.named_steps["classifier"]
        
        features = self.numeric_features.copy()
        # Since we use passthrough, dist_to_center will be appended if it exists in data
        # XGBoost natively tracks feature names if passed a DataFrame, but pipeline strips it.
        # We align with the preprocessor output order.
        if hasattr(xgb_model, "feature_names_in_"):
            # Some versions of sklearn/xgboost keep names
            pass
        else:
            # We assume order is preserved: transformed numeric, then remainder
            if len(xgb_model.feature_importances_) > len(features):
                features.append("dist_to_center")
                
        importances = xgb_model.feature_importances_
        
        return dict(zip(features, importances))

    def save(self, filepath: str | Path) -> None:
        """Persist the trained pipeline to disk using joblib."""
        if not self._is_trained:
            raise RuntimeError("Cannot save an untrained model.")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "numeric_features": self.numeric_features,
                "best_params": self.best_params_
            }, 
            filepath
        )

    @classmethod
    def load(cls, filepath: str | Path) -> XGBoostPipeline:
        """Load a trained pipeline from disk."""
        data = joblib.load(filepath)
        
        instance = cls(numeric_features=data["numeric_features"])
        instance.model = data["model"]
        instance.best_params_ = data.get("best_params")
        instance._is_trained = True
        return instance
