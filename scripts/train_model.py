"""
Script: train_model.py
Trains and evaluates the Random Forest biological activity prediction model
on the validated BACE benchmark dataset.
"""

import sys
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np
import logging

from src.data_loader import load_config
from src.preprocessing import prepare_datasets
from src.activity_model import ActivityPredictionModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    config = load_config()
    data_cfg = config["data"]
    model_cfg = config["model"]
    feat_cfg = config["features"]
    
    logger.info("=== Stage 4: Biological Activity Prediction Model Training ===")
    
    # 1. Load Cleaned Data
    processed_file = data_cfg.get("processed_file", "data/processed_bace.csv")
    df = pd.read_csv(processed_file)
    logger.info(f"Loaded {len(df)} validated molecules from {processed_file}.")
    
    # 2. Featurize and Split
    dataset_dict = prepare_datasets(
        df,
        smiles_col=data_cfg.get("smiles_col", "mol"),
        target_col=data_cfg.get("target_col", "Class"),
        split_col=data_cfg.get("split_col", "Model"),
        split_strategy=data_cfg.get("split_strategy", "stratified"),
        test_size=model_cfg.get("test_size", 0.2),
        random_state=model_cfg.get("random_state", 42),
        morgan_radius=feat_cfg.get("morgan_radius", 2),
        morgan_n_bits=feat_cfg.get("morgan_n_bits", 512)
    )
    
    X_train = dataset_dict["X_train"]
    y_train = dataset_dict["y_train"]
    X_test = dataset_dict["X_test"]
    y_test = dataset_dict["y_test"]
    df_test = dataset_dict["df_test"]
    scaler = dataset_dict["scaler"]
    feature_names = dataset_dict["feature_names"]
    
    logger.info(f"Dataset Split -> Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
    
    # 3. Train Model
    clf = ActivityPredictionModel(
        n_estimators=model_cfg.get("n_estimators", 150),
        max_depth=model_cfg.get("max_depth", 14),
        min_samples_split=model_cfg.get("min_samples_split", 4),
        class_weight=model_cfg.get("class_weight", "balanced"),
        random_state=model_cfg.get("random_state", 42)
    )
    clf.fit(X_train, y_train, scaler=scaler, feature_names=feature_names)
    
    # 4. Evaluate on Test Split
    metrics = clf.evaluate(X_test, y_test)
    
    # 5. Generate and Save Test Predictions
    y_test_prob = clf.model.predict_proba(X_test)[:, 1]
    y_test_pred = clf.model.predict(X_test)
    
    df_test["predicted_class"] = y_test_pred
    df_test["predicted_prob_active"] = np.round(y_test_prob, 4)
    df_test["is_correct"] = (df_test["predicted_class"] == df_test[data_cfg["target_col"]]).astype(int)
    
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    predictions_file = results_dir / "test_predictions.csv"
    df_test.to_csv(predictions_file, index=False)
    logger.info(f"Saved test set predictions to {predictions_file}")
    
    metrics_file = results_dir / "model_evaluation.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Saved evaluation metrics to {metrics_file}")
    
    # 6. Persist Model and Preprocessing Metadata
    clf.save(model_cfg.get("model_path", "models/activity_rf_model.joblib"),
             model_cfg.get("metadata_path", "models/model_metadata.joblib"))
             
    print("\n================ MODEL PERFORMANCE ================")
    print(f"  Test Samples:      {metrics['test_samples']}")
    print(f"  Accuracy:          {metrics['accuracy']:.4f}")
    print(f"  Precision:         {metrics['precision']:.4f}")
    print(f"  Recall:            {metrics['recall']:.4f}")
    print(f"  F1-Score:          {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC:           {metrics['roc_auc']:.4f}")
    print(f"  Confusion Matrix:  {metrics['confusion_matrix']}")
    print("===================================================\n")


if __name__ == "__main__":
    main()
