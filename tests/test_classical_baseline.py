"""
Tests for Classical Baselines Module
"""

import pytest
from src.qubo_formulation import DrugScreeningQUBO
from src.classical_baseline import solve_top_k_baseline, solve_exact_qubo, compare_screenings


def test_solve_top_k_baseline():
    scores = [0.1, 0.9, 0.4, 0.8]
    qubo = DrugScreeningQUBO(scores=scores, k=2)
    res = solve_top_k_baseline(qubo)
    
    assert res["is_feasible"] is True
    # Highest scores are idx 1 (0.9) and idx 3 (0.8) => bitstring "0101"
    assert res["bitstring"] == "0101"
    assert res["total_score"] == pytest.approx(1.7, abs=1e-4)
    assert res["energy"] == pytest.approx(-1.7, abs=1e-4)


def test_solve_exact_qubo():
    scores = [0.2, 0.85, 0.15, 0.75]
    qubo = DrugScreeningQUBO(scores=scores, k=2)
    res = solve_exact_qubo(qubo)
    
    assert res["is_feasible"] is True
    assert res["bitstring"] == "0101"
    assert res["total_score"] == pytest.approx(1.6, abs=1e-4)
    assert res["energy"] == pytest.approx(-1.6, abs=1e-4)
    assert res["total_evaluated_states"] == 16


def test_compare_screenings():
    scores = [0.9, 0.8, 0.2]
    qubo = DrugScreeningQUBO(scores=scores, k=1)
    
    exact = solve_exact_qubo(qubo)
    top_k = solve_top_k_baseline(qubo)
    
    # Mock qaoa_result
    qaoa_res = {
        "final_objective_energy": exact["energy"],
        "final_total_score": exact["total_score"],
        "selected_ids": exact["selected_ids"],
        "selection_evaluation": {"is_feasible": True},
        "timing_sec": {"simulator_sampling_time_sec": 0.05, "classical_optimization_time_sec": 0.1}
    }
    
    comp = compare_screenings(qubo, qaoa_res, top_k, exact)
    assert comp["summary"]["qaoa_found_exact_optimum"] is True
    assert comp["summary"]["qaoa_optimality_gap"] == 0.0
    assert comp["methods"]["QAOA"]["overlap_with_exact"] == 1.0
