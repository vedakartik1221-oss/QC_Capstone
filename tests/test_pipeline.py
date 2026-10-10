"""
End-to-End Pipeline Integration Test
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from src.data_loader import load_dataset
from src.preprocessing import prepare_datasets
from src.activity_model import ActivityPredictionModel
from src.qubo_formulation import compute_composite_scores, DrugScreeningQUBO
from src.qaoa_optimizer import DrugScreeningQAOA
from src.classical_baseline import solve_exact_qubo, solve_top_k_baseline, compare_screenings


def test_end_to_end_screening_pipeline():
    # 1. Load vetted sample dataset
    df, report = load_dataset(use_sample=True)
    assert len(df) == 25
    
    # 2. Featurize and prepare datasets
    data_dict = prepare_datasets(
        df,
        smiles_col="mol",
        target_col="Class",
        split_strategy="stratified",
        test_size=0.3,
        random_state=42,
        morgan_n_bits=256
    )
    
    # 3. Train Activity Prediction model
    model = ActivityPredictionModel(n_estimators=30, max_depth=6, random_state=42)
    model.fit(data_dict["X_train"], data_dict["y_train"], scaler=data_dict["scaler"], feature_names=data_dict["feature_names"])
    metrics = model.evaluate(data_dict["X_test"], data_dict["y_test"])
    assert "accuracy" in metrics
    assert "roc_auc" in metrics
    
    # 4. Predict on a small pool of 5 candidates
    test_df = data_dict["df_test"].head(5).copy().reset_index(drop=True)
    test_X = data_dict["X_test"][:5]
    test_df["predicted_prob_active"] = model.model.predict_proba(test_X)[:, 1]
    
    # 5. Compute composite scores
    scores = compute_composite_scores(
        test_df,
        pred_prob_col="predicted_prob_active",
        affinity_col="pIC50",
        lipinski_col="calc_LipinskiPassRate"
    )
    assert len(scores) == 5
    
    # 6. Formulate QUBO with budget K=2
    qubo = DrugScreeningQUBO(scores=scores, k=2, penalty_multiplier=2.0)
    
    # 7. Exact classical optimum
    exact_res = solve_exact_qubo(qubo)
    assert exact_res["is_feasible"] is True
    assert exact_res["num_selected"] == 2
    
    # 8. QAOA screening on Aer simulator
    qaoa = DrugScreeningQAOA(qubo, p=1, shots=500, max_iter=15, seed=42)
    qaoa_res = qaoa.sample_circuit()
    assert qaoa_res["selection_evaluation"]["is_feasible"] is True
    
    # 9. Classical Top-K baseline
    top_k_res = solve_top_k_baseline(qubo)
    
    # 10. Benchmarking comparison
    comparison = compare_screenings(qubo, qaoa_res, top_k_res, exact_res)
    assert "QAOA" in comparison["methods"]
    assert "Exact_QUBO" in comparison["methods"]
    assert comparison["methods"]["QAOA"]["optimality_gap"] >= 0.0
