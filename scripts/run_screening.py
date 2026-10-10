"""
Script: run_screening.py
Executes end-to-end drug screening workflow:
1. Selects candidate molecules from test partition.
2. Evaluates biological activity predictions and composite scores.
3. Formulates QUBO and executes QAOA on Qiskit Aer simulator.
4. Evaluates classical baselines (Top-K and Exact QUBO).
5. Compares results and exports artifacts.
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
from src.activity_model import ActivityPredictionModel
from src.qubo_formulation import compute_composite_scores, DrugScreeningQUBO
from src.qaoa_optimizer import DrugScreeningQAOA
from src.classical_baseline import solve_top_k_baseline, solve_exact_qubo, compare_screenings
from src.evaluation import export_screening_candidates_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    config = load_config()
    opt_cfg = config["optimization"]
    score_cfg = config["scoring"]
    qaoa_cfg = opt_cfg["qaoa"]
    
    logger.info("=== Stage 6 & 7: QAOA and Classical Baseline Screening ===")
    
    # 1. Load Trained Model
    model = ActivityPredictionModel.load(
        config["model"]["model_path"],
        config["model"]["metadata_path"]
    )
    
    # 2. Load Candidate Pool (from test predictions)
    test_pred_path = Path("results/test_predictions.csv")
    if not test_pred_path.exists():
        raise FileNotFoundError("Run 'python scripts/train_model.py' first.")
    df_pool = pd.read_csv(test_pred_path)
    
    # 3. Select reproducible candidate subset (e.g., N=8)
    n_candidates = opt_cfg.get("default_num_candidates", 8)
    k_target = opt_cfg.get("default_k", 3)
    
    # Reproducible sampling using fixed random_state
    df_subset = df_pool.sample(n=n_candidates, random_state=42).copy().reset_index(drop=True)
    
    # 4. Compute composite scores
    scores = compute_composite_scores(
        df_subset,
        pred_prob_col="predicted_prob_active",
        affinity_col="pIC50",
        lipinski_col="calc_LipinskiPassRate",
        w_pred=score_cfg.get("w_pred", 0.60),
        w_affinity=score_cfg.get("w_affinity", 0.25),
        w_lipinski=score_cfg.get("w_lipinski", 0.15)
    )
    df_subset["composite_score"] = scores
    
    candidate_ids = [f"MOL_{cid}" for cid in df_subset["CID"]]
    df_subset["CandidateID"] = candidate_ids
    
    logger.info(f"Screening candidate pool: N={n_candidates}, Selection Budget K={k_target}")
    for i, row in df_subset.iterrows():
        logger.info(
            f"  Candidate [{i}] {row['CandidateID']}: PredProb={row['predicted_prob_active']:.3f}, "
            f"pIC50={row.get('pIC50', 'N/A')}, Lipinski={row.get('calc_LipinskiPassRate', 1.0):.2f} -> Score={row['composite_score']:.3f}"
        )
        
    # 5. Formulate QUBO
    qubo = DrugScreeningQUBO(
        scores=scores,
        k=k_target,
        penalty_multiplier=opt_cfg.get("penalty_multiplier", 2.0),
        candidate_ids=candidate_ids
    )
    
    # 6. Execute QAOA on Aer Simulator
    logger.info("Executing QAOA on AerSimulator...")
    qaoa = DrugScreeningQAOA(
        qubo=qubo,
        p=qaoa_cfg.get("p", 1),
        shots=qaoa_cfg.get("shots", 1024),
        optimizer_name=qaoa_cfg.get("optimizer", "COBYLA"),
        max_iter=qaoa_cfg.get("max_iter", 40),
        seed=qaoa_cfg.get("seed", 42)
    )
    qaoa.optimize_parameters()
    qaoa_results = qaoa.sample_circuit()
    
    # 7. Classical Baselines
    logger.info("Executing Classical Baselines (Top-K and Exact QUBO)...")
    top_k_res = solve_top_k_baseline(qubo)
    exact_res = solve_exact_qubo(qubo)
    
    # 8. Compare Screenings
    comparison = compare_screenings(qubo, qaoa_results, top_k_res, exact_res)
    
    # 9. Save Results
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    screening_output = {
        "candidate_pool": df_subset[["CandidateID", "mol", "Class", "pIC50", "predicted_prob_active", "composite_score"]].to_dict(orient="records"),
        "qaoa": qaoa_results,
        "top_k": top_k_res,
        "exact_qubo": exact_res,
        "comparison": comparison
    }
    
    with open(results_dir / "screening_results.json", "w", encoding="utf-8") as f:
        # Exclude complex objects if any
        json.dump(screening_output, f, indent=2)
        
    # Export selected candidates table
    export_screening_candidates_csv(df_subset, qaoa_results["selected_indices"])
    
    # Print formatted comparison table
    print("\n" + "="*80)
    print("                    SCREENING BENCHMARK COMPARISON TABLE")
    print("="*80)
    print(f"{'Method':<25} | {'Energy (E)':<12} | {'Score Sum':<10} | {'Feasible':<10} | {'Gap':<8} | {'Overlap':<8} | {'Time (s)':<10}")
    print("-" * 80)
    for method_name, m_data in comparison["methods"].items():
        print(
            f"{method_name:<25} | "
            f"{m_data['energy']:<12.4f} | "
            f"{m_data['total_score']:<10.4f} | "
            f"{str(m_data['is_feasible']):<10} | "
            f"{m_data['optimality_gap']:<8.4f} | "
            f"{m_data['overlap_with_exact']*100:<7.1f}% | "
            f"{m_data['runtime_sec']:<10.4f}"
        )
    print("="*80)
    print(f"QAOA Feasibility Rate: {qaoa_results['feasibility_rate']*100:.1f}% ({qaoa_results['feasible_shots']}/{qaoa_results['shots']} shots)")
    print(f"QAOA Chosen Bitstring: {qaoa_results['chosen_bitstring']} -> Candidates: {qaoa_results['selected_ids']}")
    print(f"Exact Optimal Bitstring: {exact_res['bitstring']} -> Candidates: {exact_res['selected_ids']}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
