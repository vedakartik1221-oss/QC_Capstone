"""
Tests for QAOA Circuit and Optimization Module
"""

import pytest
import numpy as np
from src.qubo_formulation import DrugScreeningQUBO
from src.qaoa_optimizer import DrugScreeningQAOA


def test_qaoa_circuit_construction():
    qubo = DrugScreeningQUBO([0.8, 0.4, 0.6], k=1)
    qaoa = DrugScreeningQAOA(qubo, p=2, shots=100)
    
    gamma = np.array([0.2, 0.3])
    beta = np.array([0.4, 0.5])
    qc = qaoa.build_circuit(gamma, beta, add_measurements=True)
    
    assert qc.num_qubits == 3
    # Check that measurements are added
    assert qc.num_clbits == 3


def test_qaoa_parameter_optimization_and_sampling():
    qubo = DrugScreeningQUBO([0.9, 0.2, 0.8], k=2, penalty_multiplier=2.5)
    qaoa = DrugScreeningQAOA(qubo, p=1, shots=500, max_iter=15, seed=42)
    
    params, energy = qaoa.optimize_parameters()
    assert len(params) == 2  # p=1: 1 gamma + 1 beta
    assert isinstance(energy, float)
    
    results = qaoa.sample_circuit(params)
    assert results["shots"] == 500
    assert "chosen_bitstring" in results
    assert len(results["chosen_bitstring"]) == 3
    assert results["feasibility_rate"] > 0.0
    assert results["selection_evaluation"]["is_feasible"] is True
    assert len(results["selected_ids"]) == 2
