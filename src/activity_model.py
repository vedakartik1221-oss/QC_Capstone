"""
Biological Activity Prediction Model Module
Trains, tunes, evaluates, and persists a Random Forest classifier
for predicting BACE-1 biological activity from molecular features.
"""

from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import joblib
import logging

from src.preprocessing import featurize_single_smiles, NUMERICAL_DESCRIPTORS

logger = logging.getLogger(__name__)

SCIENTIFIC_DISCLAIMER = (
    "DISCLAIMER: Predicted activity probabilities are statistical estimations derived from "
    "a machine learning model trained on human BACE-1 benchmark assay data. They do NOT "
    "guarantee binding affinity, specificity, biological efficacy, pharmacokinetic suitability, "
    "or safety. Experimental in vitro and in vivo validation is mandatory."
)


class ActivityPredictionModel:
    """Random Forest Classifier for Molecular Activity Screening."""
    
    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: Optional[int] = 14,
        min_samples_split: int = 4,
        class_weight: str = "balanced",
        random_state: int = 42
    ):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            class_weight=class_weight,
            random_state=random_state,
            n_jobs=-1
        )
        self.scaler = None
        self.feature_names = []
        self.metadata = {}
        self.is_trained = False
        
    def fit(self, X_train: np.ndarray, y_train: np.ndarray, scaler=None, feature_names=None):
        """Fit model on training feature matrix."""
        logger.info(f"Training Random Forest classifier on {len(X_train)} samples...")
        self.model.fit(X_train, y_train)
        self.scaler = scaler
        self.feature_names = feature_names or []
        self.is_trained = True
        logger.info("Random Forest training completed.")
        return self
        
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate model performance on held-out test data.
        
        Returns:
            Dictionary with accuracy, precision, recall, f1, roc_auc, confusion_matrix, etc.
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before evaluation.")
            
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)[:, 1]
        
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_prob)) if len(np.unique(y_test)) > 1 else 0.5
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        metrics = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": cm,
            "test_samples": int(len(y_test)),
            "test_actives": int(np.sum(y_test == 1)),
            "test_inactives": int(np.sum(y_test == 0))
        }
        
        self.metadata["test_metrics"] = metrics
        logger.info(
            f"Test Evaluation -> Acc: {acc:.3f}, ROC-AUC: {roc_auc:.3f}, "
            f"F1: {f1:.3f}, Precision: {prec:.3f}, Recall: {rec:.3f}"
        )
        return metrics

    def predict_smiles(
        self,
        smiles: str,
        morgan_radius: int = 2,
        morgan_n_bits: int = 512
    ) -> Optional[Dict[str, Any]]:
        """
        Predict activity for an arbitrary input SMILES string.
        
        Returns:
            Dictionary containing prediction probability, active/inactive call, descriptors, disclaimer.
        """
        if not self.is_trained or self.scaler is None:
            raise RuntimeError("Model and scaler must be initialized.")
            
        result = featurize_single_smiles(
            smiles, self.scaler, morgan_radius=morgan_radius, morgan_n_bits=morgan_n_bits
        )
        if result is None:
            return None
            
        feat_vector, descriptors = result
        prob_active = float(self.model.predict_proba(feat_vector)[0, 1])
        predicted_class = int(prob_active >= 0.5)
        
        return {
            "smiles": smiles,
            "canonical_smiles": descriptors.get("CanonicalSMILES", smiles),
            "predicted_class": predicted_class,
            "class_label": "Active (Inhibitor)" if predicted_class == 1 else "Inactive",
            "prob_active": round(prob_active, 4),
            "prob_inactive": round(1.0 - prob_active, 4),
            "descriptors": descriptors,
            "disclaimer": SCIENTIFIC_DISCLAIMER
        }

    def save(self, model_path: str = "models/activity_rf_model.joblib", meta_path: str = "models/model_metadata.joblib"):
        """Save trained model, scaler, and metadata to disk."""
        m_path = Path(model_path)
        m_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, m_path)
        
        meta = {
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "metadata": self.metadata,
            "is_trained": self.is_trained
        }
        meta_p = Path(meta_path)
        meta_p.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(meta, meta_p)
        logger.info(f"Model saved to {model_path} and metadata to {meta_path}")

    @classmethod
    def load(cls, model_path: str = "models/activity_rf_model.joblib", meta_path: str = "models/model_metadata.joblib") -> "ActivityPredictionModel":
        """Load trained model and metadata from disk."""
        m_path = Path(model_path)
        meta_p = Path(meta_path)
        if not m_path.exists() or not meta_p.exists():
            raise FileNotFoundError(f"Saved model or metadata file not found at {model_path} or {meta_path}")
            
        inst = cls()
        inst.model = joblib.load(m_path)
        meta = joblib.load(meta_p)
        inst.scaler = meta.get("scaler")
        inst.feature_names = meta.get("feature_names", [])
        inst.metadata = meta.get("metadata", {})
        inst.is_trained = meta.get("is_trained", True)
        return inst
