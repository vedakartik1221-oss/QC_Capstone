"""
Classical Baselines Module
Implements:
1. Greedy Top-K Ranking baseline
2. Exact Classical Brute-Force QUBO optimization
Calculates optimality gaps, overlap metrics, and runtime benchmarks.
"""

from typing import Dict, Any, List, Tuple
import itertools
import time
import numpy as np
import logging

from src.qubo_formulation import DrugScreeningQUBO

logger = logging.getLogger(__name__)


def solve_top_k_baseline(qubo: DrugScreeningQUBO) -> Dict[str, Any]:
    """
    Solve the fixed-budget screening problem using a greedy Top-K ranking strategy.
    Selects the K candidates with the highest individual composite scores.
    
    Returns:
        Evaluation dictionary including energy, score, timing, and selected IDs.
    """
    t_start = time.perf_counter()
    n = qubo.num_candidates
    k = qubo.k
    
    # Sort indices by score descending
    sorted_indices = np.argsort(-qubo.scores)
    selected_indices = sorted_indices[:k].tolist()
    
    # Construct binary bitstring
    bit_array = np.zeros(n, dtype=int)
    bit_array[selected_indices] = 1
    bitstring = "".join(str(b) for b in bit_array)
    
    t_end = time.perf_counter()
    runtime_sec = round(t_end - t_start, 6)
    
    eval_result = qubo.evaluate_bitstring(bitstring)
    eval_result["method"] = "Top-K Greedy Ranking"
    eval_result["execution_time_sec"] = runtime_sec
    return eval_result


def solve_exact_qubo(qubo: DrugScreeningQUBO) -> Dict[str, Any]:
    """
    Solve the QUBO selection problem exactly via brute-force enumeration.
    Evaluates all 2^N bitstrings, identifies the global minimum of the energy function E(x),
    and validates feasibility against the cardinality constraint sum(x_i) == K.
    
    Returns:
        Exact global optimum solution dictionary.
    """
    t_start = time.perf_counter()
    n = qubo.num_candidates
    
    best_energy = float("inf")
    best_bitstring = None
    all_evaluated = 0
    feasible_count = 0
    
    # Enumerate all 2^N binary assignments
    for bits in itertools.product([0, 1], repeat=n):
        all_evaluated += 1
        b_str = "".join(str(b) for b in bits)
        eval_res = qubo.evaluate_bitstring(b_str)
        
        if eval_res["is_feasible"]:
            feasible_count += 1
            
        if eval_res["energy"] < best_energy:
            best_energy = eval_res["energy"]
            best_bitstring = b_str
            
    t_end = time.perf_counter()
    runtime_sec = round(t_end - t_start, 6)
    
    optimal_eval = qubo.evaluate_bitstring(best_bitstring)
    optimal_eval["method"] = "Exact Classical QUBO (Enumeration)"
    optimal_eval["execution_time_sec"] = runtime_sec
    optimal_eval["total_evaluated_states"] = all_evaluated
    optimal_eval["feasible_states_count"] = feasible_count
    return optimal_eval


def compare_screenings(
    qubo: DrugScreeningQUBO,
    qaoa_result: Dict[str, Any],
    top_k_result: Dict[str, Any],
    exact_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare QAOA, Top-K, and Exact Classical solutions across quality,
    candidate overlap, and execution time.
    """
    exact_energy = exact_result["energy"]
    qaoa_energy = qaoa_result["final_objective_energy"]
    top_k_energy = top_k_result["energy"]
    
    # Optimality gaps: Gap = E_method - E_exact (0.0 means fully optimal)
    qaoa_gap = round(max(0.0, qaoa_energy - exact_energy), 4)
    top_k_gap = round(max(0.0, top_k_energy - exact_energy), 4)
    
    # Set overlap
    exact_set = set(exact_result["selected_ids"])
    qaoa_set = set(qaoa_result["selected_ids"])
    top_k_set = set(top_k_result["selected_ids"])
    
    qaoa_exact_overlap = len(exact_set.intersection(qaoa_set)) / len(exact_set) if len(exact_set) > 0 else 1.0
    topk_exact_overlap = len(exact_set.intersection(top_k_set)) / len(exact_set) if len(exact_set) > 0 else 1.0
    
    comparison = {
        "methods": {
            "QAOA": {
                "energy": qaoa_energy,
                "total_score": qaoa_result["final_total_score"],
                "is_feasible": qaoa_result["selection_evaluation"]["is_feasible"],
                "optimality_gap": qaoa_gap,
                "selected_ids": qaoa_result["selected_ids"],
                "overlap_with_exact": round(qaoa_exact_overlap, 3),
                "runtime_sec": qaoa_result["timing_sec"].get("simulator_sampling_time_sec", 0.0) +
                               qaoa_result["timing_sec"].get("classical_optimization_time_sec", 0.0)
            },
            "Top-K": {
                "energy": top_k_energy,
                "total_score": top_k_result["total_score"],
                "is_feasible": top_k_result["is_feasible"],
                "optimality_gap": top_k_gap,
                "selected_ids": top_k_result["selected_ids"],
                "overlap_with_exact": round(topk_exact_overlap, 3),
                "runtime_sec": top_k_result["execution_time_sec"]
            },
            "Exact_QUBO": {
                "energy": exact_energy,
                "total_score": exact_result["total_score"],
                "is_feasible": exact_result["is_feasible"],
                "optimality_gap": 0.0,
                "selected_ids": exact_result["selected_ids"],
                "overlap_with_exact": 1.0,
                "runtime_sec": exact_result["execution_time_sec"]
            }
        },
        "summary": {
            "exact_optimal_energy": exact_energy,
            "qaoa_found_exact_optimum": bool(qaoa_gap <= 1e-4),
            "qaoa_optimality_gap": qaoa_gap,
            "top_k_optimality_gap": top_k_gap
        }
    }
    return comparison
