"""
Quantum Approximate Optimization Algorithm (QAOA) Module
Constructs and executes genuine QAOA quantum circuits on Qiskit Aer simulator
for fixed-budget drug candidate screening.
"""

from typing import Dict, Any, List, Tuple, Optional
import time
import numpy as np
import scipy.optimize as opt
import logging

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from src.qubo_formulation import DrugScreeningQUBO

logger = logging.getLogger(__name__)


class DrugScreeningQAOA:
    """
    QAOA Implementation for Molecular QUBO Screening.
    
    Circuit Structure:
        1. Initialization: |+>^N via Hadamard gates on all qubits.
        2. Alternating layers (depth p):
           - Cost Unitary U(C, gamma) = exp(-i * gamma * H_C)
             * RZ(2 * gamma * h_i) on each qubit i
             * RZZ(2 * gamma * J_ij) on each interacting pair (i, j)
           - Mixer Unitary U(B, beta) = exp(-i * beta * H_B)
             * RX(2 * beta) on each qubit i
        3. Measurement: Projective computational basis sampling on Aer simulator.
    """

    def __init__(
        self,
        qubo: DrugScreeningQUBO,
        p: int = 1,
        shots: int = 1024,
        optimizer_name: str = "COBYLA",
        max_iter: int = 40,
        seed: int = 42
    ):
        self.qubo = qubo
        self.n = qubo.num_candidates
        self.p = max(1, int(p))
        self.shots = int(shots)
        self.optimizer_name = optimizer_name
        self.max_iter = int(max_iter)
        self.seed = int(seed)
        
        self.simulator = AerSimulator(seed_simulator=self.seed)
        
        # State tracking
        self.optimal_params: Optional[np.ndarray] = None
        self.optimization_history: List[Dict[str, Any]] = []
        self.timing_info: Dict[str, float] = {}

    def build_circuit(self, gamma: np.ndarray, beta: np.ndarray, add_measurements: bool = False) -> QuantumCircuit:
        """
        Build the parameterized QAOA quantum circuit.
        
        Args:
            gamma: Array of length p containing cost unitary rotation angles
            beta: Array of length p containing mixer unitary rotation angles
            add_measurements: If True, adds measure_all() to circuit
            
        Returns:
            Qiskit QuantumCircuit
        """
        qc = QuantumCircuit(self.n)
        
        # 1. State Preparation: |+>^N
        for q in range(self.n):
            qc.h(q)
            
        # 2. Alternating QAOA layers
        for layer in range(self.p):
            g = float(gamma[layer])
            b = float(beta[layer])
            
            # --- Cost Unitary: U(C, gamma) ---
            # Single-qubit linear terms: RZ(2 * gamma * h_i)
            for i in range(self.n):
                angle = 2.0 * g * self.qubo.h[i]
                qc.rz(angle, i)
                
            # Two-qubit quadratic terms: RZZ(2 * gamma * J_ij)
            for i in range(self.n):
                for j in range(i + 1, self.n):
                    angle = 2.0 * g * self.qubo.J[i, j]
                    qc.rzz(angle, i, j)
                    
            # --- Mixer Unitary: U(B, beta) ---
            # Transverse field mixer: RX(2 * beta)
            for i in range(self.n):
                qc.rx(2.0 * b, i)
                
        if add_measurements:
            qc.measure_all()
            
        return qc

    def compute_energy_expectation(self, params: np.ndarray) -> float:
        """
        Compute the expected energy <H_C> for given (gamma, beta) angles.
        Uses exact statevector evaluation for rapid, noise-free classical parameter convergence.
        """
        gamma = params[:self.p]
        beta = params[self.p:]
        
        qc = self.build_circuit(gamma, beta, add_measurements=False)
        sv = Statevector.from_instruction(qc)
        probs = sv.probabilities()
        
        # Compute <E> = sum_x P(x) * E(x)
        expected_energy = 0.0
        n_states = 1 << self.n
        for idx in range(n_states):
            p_val = float(probs[idx])
            if p_val > 1e-7:
                # Format bitstring with leading zeros (qubit n-1 ... qubit 0)
                # In Qiskit, bitstring convention: qubit 0 is rightmost
                raw_bits = f"{idx:0{self.n}b}"
                # Reverse to align qubit 0 with candidate index 0
                bitstring = raw_bits[::-1]
                eval_res = self.qubo.evaluate_bitstring(bitstring)
                expected_energy += p_val * eval_res["energy"]
                
        return float(expected_energy)

    def optimize_parameters(self) -> Tuple[np.ndarray, float]:
        """
        Execute classical parameter optimization for QAOA angles (gamma, beta).
        
        Returns:
            Tuple of (optimal_params, minimum_expected_energy)
        """
        # Initial guess: small angles
        rng = np.random.default_rng(self.seed)
        initial_gamma = rng.uniform(0.1, np.pi / 2, self.p)
        initial_beta = rng.uniform(0.1, np.pi / 4, self.p)
        initial_params = np.concatenate([initial_gamma, initial_beta])
        
        self.optimization_history = []
        iteration_count = [0]
        
        def callback(x):
            iteration_count[0] += 1
            cost = self.compute_energy_expectation(x)
            self.optimization_history.append({
                "iteration": iteration_count[0],
                "energy": round(cost, 4),
                "gamma": [round(float(g), 4) for g in x[:self.p]],
                "beta": [round(float(b), 4) for b in x[self.p:]]
            })
            
        t_start = time.perf_counter()
        
        res = opt.minimize(
            self.compute_energy_expectation,
            initial_params,
            method=self.optimizer_name,
            callback=callback,
            options={"maxiter": self.max_iter, "disp": False}
        )
        
        t_end = time.perf_counter()
        self.timing_info["classical_optimization_time_sec"] = round(t_end - t_start, 4)
        
        self.optimal_params = res.x
        optimal_energy = float(res.fun)
        
        logger.info(
            f"QAOA Optimization finished in {self.timing_info['classical_optimization_time_sec']}s: "
            f"Expected Energy = {optimal_energy:.4f}"
        )
        return self.optimal_params, optimal_energy

    def sample_circuit(self, params: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Execute the optimized QAOA circuit on Aer simulator with shot-based measurement.
        Decodes bitstrings, evaluates QUBO energies, and identifies optimal selections.
        
        Returns:
            Comprehensive screening results dictionary.
        """
        if params is None:
            if self.optimal_params is None:
                self.optimize_parameters()
            params = self.optimal_params
            
        gamma = params[:self.p]
        beta = params[self.p:]
        
        t_sim_start = time.perf_counter()
        qc_meas = self.build_circuit(gamma, beta, add_measurements=True)
        job = self.simulator.run(qc_meas, shots=self.shots)
        result = job.result()
        raw_counts = result.get_counts()
        t_sim_end = time.perf_counter()
        self.timing_info["simulator_sampling_time_sec"] = round(t_sim_end - t_sim_start, 4)
        
        # Process and decode sampled bitstrings
        # In Qiskit, counts keys are formatted with qubit 0 rightmost: string[::-1] gives qubit 0 first
        decoded_distribution = {}
        feasible_count = 0
        best_bitstring = None
        best_energy = float("inf")
        best_feasible_bitstring = None
        best_feasible_energy = float("inf")
        
        for qiskit_str, count in raw_counts.items():
            candidate_bitstring = qiskit_str[::-1]
            eval_info = self.qubo.evaluate_bitstring(candidate_bitstring)
            energy = eval_info["energy"]
            is_feasible = eval_info["is_feasible"]
            
            prob = count / self.shots
            decoded_distribution[candidate_bitstring] = {
                "count": count,
                "probability": round(prob, 4),
                "energy": energy,
                "total_score": eval_info["total_score"],
                "is_feasible": is_feasible,
                "num_selected": eval_info["num_selected"],
                "selected_ids": eval_info["selected_ids"]
            }
            
            if is_feasible:
                feasible_count += count
                if energy < best_feasible_energy:
                    best_feasible_energy = energy
                    best_feasible_bitstring = candidate_bitstring
                    
            if energy < best_energy:
                best_energy = energy
                best_bitstring = candidate_bitstring
                
        feasibility_rate = round(feasible_count / self.shots, 4)
        
        # Most frequent measured bitstring
        most_frequent_bitstring = max(decoded_distribution.keys(), key=lambda b: decoded_distribution[b]["count"])
        
        # Primary selection: Best feasible bitstring if found, otherwise repaired best bitstring
        used_repair = False
        if best_feasible_bitstring is not None:
            chosen_bitstring = best_feasible_bitstring
            selection_details = self.qubo.evaluate_bitstring(chosen_bitstring)
        else:
            used_repair = True
            chosen_bitstring, selection_details = self.qubo.repair_bitstring(best_bitstring)
            
        summary = {
            "num_candidates": self.n,
            "k_target": self.qubo.k,
            "qaoa_depth_p": self.p,
            "shots": self.shots,
            "optimal_gamma": [round(float(g), 4) for g in gamma],
            "optimal_beta": [round(float(b), 4) for b in beta],
            "feasibility_rate": feasibility_rate,
            "feasible_shots": feasible_count,
            "most_frequent_bitstring": most_frequent_bitstring,
            "best_energy_bitstring": best_bitstring,
            "best_feasible_bitstring": best_feasible_bitstring,
            "chosen_bitstring": chosen_bitstring,
            "used_repair_procedure": used_repair,
            "selection_evaluation": selection_details,
            "selected_ids": selection_details["selected_ids"],
            "selected_indices": selection_details["selected_indices"],
            "final_objective_energy": selection_details["energy"],
            "final_total_score": selection_details["total_score"],
            "timing_sec": self.timing_info,
            "optimization_history": self.optimization_history,
            "distribution": decoded_distribution
        }
        
        logger.info(
            f"QAOA Sampling complete: Chosen {chosen_bitstring} (Energy: {selection_details['energy']}, "
            f"Score: {selection_details['total_score']}, Feasible Rate: {feasibility_rate*100:.1f}%)"
        )
        return summary
