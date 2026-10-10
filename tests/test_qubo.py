"""
Tests for QUBO Formulation and Mathematical Invariants
"""

import pytest
import numpy as np
from src.qubo_formulation import DrugScreeningQUBO, compute_composite_scores
import pandas as pd


def test_qubo_hand_calculated_invariants():
    """
    Test against analytical 2-variable problem:
        scores = [0.8, 0.4], K = 1, penalty_multiplier = 2.5
        max(s) = 0.8 => A = 2.0
        Feasible bitstring '10': E = -0.8 + 2.0*(1 - 1)^2 = -0.8
        Feasible bitstring '01': E = -0.4 + 2.0*(1 - 1)^2 = -0.4
        Infeasible bitstring '00': E = 0 + 2.0*(0 - 1)^2 = 2.0
        Infeasible bitstring '11': E = -(0.8 + 0.4) + 2.0*(2 - 1)^2 = 0.8
    """
    qubo = DrugScreeningQUBO(scores=[0.8, 0.4], k=1, penalty_multiplier=2.5)
    
    # Check penalty multiplier
    assert qubo.penalty_A == pytest.approx(2.0, rel=1e-5)
    
    # Check evaluations
    res_10 = qubo.evaluate_bitstring("10")
    assert res_10["is_feasible"] is True
    assert res_10["energy"] == pytest.approx(-0.8, abs=1e-4)
    assert res_10["total_score"] == pytest.approx(0.8, abs=1e-4)
    assert res_10["penalty_cost"] == pytest.approx(0.0, abs=1e-4)
    
    res_01 = qubo.evaluate_bitstring("01")
    assert res_01["is_feasible"] is True
    assert res_01["energy"] == pytest.approx(-0.4, abs=1e-4)
    
    res_00 = qubo.evaluate_bitstring("00")
    assert res_00["is_feasible"] is False
    assert res_00["energy"] == pytest.approx(2.0, abs=1e-4)
    
    res_11 = qubo.evaluate_bitstring("11")
    assert res_11["is_feasible"] is False
    assert res_11["energy"] == pytest.approx(0.8, abs=1e-4)


def test_qubo_ising_hamiltonian_consistency():
    """
    Verify that the derived Ising spin Hamiltonian eigenvalues
    match the QUBO cost function on all 2^N basis states.
    """
    scores = [0.9, 0.5, 0.7]
    qubo = DrugScreeningQUBO(scores=scores, k=2, penalty_multiplier=2.0)
    
    # Enumerate all 8 states
    for idx in range(8):
        bitstring = f"{idx:03b}"
        # Evaluate via QUBO
        qubo_val = qubo.evaluate_bitstring(bitstring)["energy"]
        
        # Evaluate via Ising spins Z_i = 1 - 2*x_i
        # in {+1, -1}
        x = np.array([int(b) for b in bitstring])
        z = 1.0 - 2.0 * x
        
        ising_val = float(np.sum(qubo.h * z))
        for i in range(3):
            for j in range(i + 1, 3):
                ising_val += qubo.J[i, j] * z[i] * z[j]
        ising_val += qubo.hamiltonian_offset
        
        assert ising_val == pytest.approx(qubo_val, abs=1e-4)


def test_qubo_repair_bitstring():
    scores = [0.9, 0.3, 0.7, 0.1]
    qubo = DrugScreeningQUBO(scores=scores, k=2, penalty_multiplier=2.0)
    
    # Case 1: Infeasible with too many (3 ones), should drop candidate with lowest score (idx 1: 0.3)
    repaired_str, eval_res = qubo.repair_bitstring("1110")
    assert repaired_str == "1010"
    assert eval_res["is_feasible"] is True
    assert eval_res["num_selected"] == 2
    
    # Case 2: Infeasible with too few (0 ones), should pick top 2 highest (idx 0 and 2)
    repaired_str, eval_res = qubo.repair_bitstring("0000")
    assert repaired_str == "1010"
    assert eval_res["is_feasible"] is True
    assert eval_res["num_selected"] == 2
