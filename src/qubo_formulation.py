"""
QUBO & Ising Hamiltonian Formulation Module
Constructs the fixed-budget candidate selection QUBO and maps it
analytically to an Ising Cost Hamiltonian for QAOA execution.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def compute_composite_scores(
    df: pd.DataFrame,
    pred_prob_col: str = "pred_prob_active",
    affinity_col: str = "pIC50",
    lipinski_col: str = "calc_LipinskiPassRate",
    w_pred: float = 0.60,
    w_affinity: float = 0.25,
    w_lipinski: float = 0.15
) -> np.ndarray:
    """
    Compute normalized composite candidate scores s_i in [0, 1].
    
    Formula:
        s_i = w_pred * P(active)_i + w_affinity * Norm(pIC50)_i + w_lipinski * LipinskiPassRate_i
        
    Args:
        df: DataFrame containing candidate records
        pred_prob_col: Column with ML predicted active probability [0, 1]
        affinity_col: Column with experimental binding affinity pIC50
        lipinski_col: Column with fraction of Lipinski rules met [0, 1]
        w_pred: Weight for ML prediction
        w_affinity: Weight for experimental affinity
        w_lipinski: Weight for drug-likeness compliance
        
    Returns:
        numpy 1D array of composite scores s_i
    """
    n = len(df)
    if n == 0:
        return np.array([])
        
    # 1. Prediction probability
    if pred_prob_col in df.columns:
        p_active = df[pred_prob_col].fillna(0.5).to_numpy(dtype=float)
    else:
        p_active = np.full(n, 0.5)
        
    # 2. Normalized affinity pIC50
    if affinity_col in df.columns and df[affinity_col].notna().any():
        aff_vals = df[affinity_col].to_numpy(dtype=float)
        # BACE pIC50 typically spans ~3.0 to ~10.0
        min_aff = np.nanmin(aff_vals)
        max_aff = np.nanmax(aff_vals)
        if max_aff > min_aff:
            norm_aff = (aff_vals - min_aff) / (max_aff - min_aff)
        else:
            norm_aff = np.full(n, 0.5)
        norm_aff = np.nan_to_num(norm_aff, nan=0.5)
    else:
        norm_aff = np.full(n, 0.5)
        
    # 3. Lipinski pass rate
    if lipinski_col in df.columns:
        lip_rate = df[lipinski_col].fillna(1.0).to_numpy(dtype=float)
    else:
        lip_rate = np.full(n, 1.0)
        
    # Weighted composite score
    total_w = w_pred + w_affinity + w_lipinski
    scores = (w_pred * p_active + w_affinity * norm_aff + w_lipinski * lip_rate) / total_w
    return np.round(scores, 4)


class DrugScreeningQUBO:
    """
    Fixed-Budget Candidate Selection QUBO and Ising Hamiltonian Generator.
    
    Mathematical Formulation:
        Decision variables: x_i in {0, 1}
        Objective: Maximize sum(s_i * x_i) <=> Minimize -sum(s_i * x_i)
        Subject to: sum(x_i) = K
        
        Penalty formulation:
            E(x) = -sum(s_i * x_i) + A * (sum(x_i) - K)^2
            
        Ising Transformation (x_i = (I - Z_i)/2):
            H_C = sum_i h_i Z_i + sum_{i < j} J_{ij} Z_i Z_j + offset * I
    """
    
    def __init__(
        self,
        scores: np.ndarray,
        k: int,
        penalty_multiplier: float = 2.0,
        candidate_ids: Optional[List[str]] = None
    ):
        self.scores = np.asarray(scores, dtype=float)
        self.num_candidates = len(self.scores)
        self.k = int(k)
        
        if self.k < 1 or self.k > self.num_candidates:
            raise ValueError(f"Selection budget K={self.k} must be in [1, {self.num_candidates}].")
            
        # Choose penalty A sufficiently large: A >= penalty_multiplier * max(s_i)
        max_score = float(np.max(self.scores)) if self.num_candidates > 0 else 1.0
        self.penalty_A = max(1.5, penalty_multiplier * max_score)
        
        self.candidate_ids = (
            candidate_ids if candidate_ids is not None
            else [f"CAND_{i}" for i in range(self.num_candidates)]
        )
        
        self._build_qubo_matrix()
        self._build_ising_hamiltonian()
        
    def _build_qubo_matrix(self):
        """
        Build upper-triangular QUBO matrix Q such that:
            E(x) = x^T Q x + constant_offset
        """
        n = self.num_candidates
        A = self.penalty_A
        K = self.k
        
        self.Q = np.zeros((n, n), dtype=float)
        
        # Diagonal terms: Q_ii = -s_i + A * (1 - 2*K)
        for i in range(n):
            self.Q[i, i] = -self.scores[i] + A * (1.0 - 2.0 * K)
            
        # Off-diagonal terms (upper triangular): Q_ij = 2*A for i < j
        for i in range(n):
            for j in range(i + 1, n):
                self.Q[i, j] = 2.0 * A
                
        self.constant_offset = A * (K ** 2)

    def _build_ising_hamiltonian(self):
        """
        Derive exact Pauli-Z longitudinal fields h_i, Ising couplings J_ij,
        and identity energy shift offset:
            h_i = s_i / 2 + A / 2 * (2K - N)
            J_ij = A / 2
        """
        n = self.num_candidates
        A = self.penalty_A
        K = self.k
        
        # 1. Single-qubit Pauli-Z coefficients h_i
        self.h = np.zeros(n, dtype=float)
        for i in range(n):
            self.h[i] = (self.scores[i] / 2.0) + (A / 2.0) * (2.0 * K - n)
            
        # 2. Two-qubit ZZ coupling matrix J_ij (upper triangular)
        self.J = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                self.J[i, j] = A / 2.0
                
        # 3. Hamiltonian identity offset
        # offset = A*K^2 - 0.5*sum(s_i) + 0.5*n*A*(1 - 2K) + 0.25*n*(n-1)*A
        self.hamiltonian_offset = (
            A * (K ** 2)
            - 0.5 * np.sum(self.scores)
            + 0.5 * n * A * (1.0 - 2.0 * K)
            + 0.25 * n * (n - 1) * A
        )

    def evaluate_bitstring(self, bitstring: str) -> Dict[str, Any]:
        """
        Evaluate objective value, constraint satisfaction, and penalty for a binary bitstring.
        
        Args:
            bitstring: String of '0' and '1' of length N (e.g. "0110")
            
        Returns:
            Dictionary with energy, raw score, constraint satisfaction, feasibility, and selected indices.
        """
        if len(bitstring) != self.num_candidates:
            raise ValueError(f"Bitstring length {len(bitstring)} does not match N={self.num_candidates}")
            
        x = np.array([int(b) for b in bitstring], dtype=int)
        
        selected_indices = np.where(x == 1)[0].tolist()
        num_selected = len(selected_indices)
        is_feasible = (num_selected == self.k)
        
        total_score = float(np.sum(self.scores[selected_indices]))
        penalty_cost = float(self.penalty_A * ((num_selected - self.k) ** 2))
        qubo_energy = -total_score + penalty_cost
        
        selected_ids = [self.candidate_ids[i] for i in selected_indices]
        
        return {
            "bitstring": bitstring,
            "selected_indices": selected_indices,
            "selected_ids": selected_ids,
            "num_selected": num_selected,
            "k_target": self.k,
            "is_feasible": is_feasible,
            "total_score": round(total_score, 4),
            "penalty_cost": round(penalty_cost, 4),
            "energy": round(qubo_energy, 4)
        }

    def repair_bitstring(self, bitstring: str) -> Tuple[str, Dict[str, Any]]:
        """
        Greedy repair procedure for an infeasible bitstring.
        If too many candidates selected (> K): remove candidates with lowest scores.
        If too few candidates selected (< K): add unselected candidates with highest scores.
        
        Returns:
            Tuple of (repaired_bitstring: str, evaluation: Dict)
        """
        x = np.array([int(b) for b in bitstring], dtype=int)
        current_k = np.sum(x)
        
        if current_k == self.k:
            return bitstring, self.evaluate_bitstring(bitstring)
            
        indices_selected = list(np.where(x == 1)[0])
        indices_unselected = list(np.where(x == 0)[0])
        
        if current_k > self.k:
            # Sort selected by score ascending (lowest score dropped first)
            indices_selected.sort(key=lambda idx: self.scores[idx])
            drop_count = current_k - self.k
            for idx in indices_selected[:drop_count]:
                x[idx] = 0
        else:
            # Sort unselected by score descending (highest score added first)
            indices_unselected.sort(key=lambda idx: self.scores[idx], reverse=True)
            add_count = self.k - current_k
            for idx in indices_unselected[:add_count]:
                x[idx] = 1
                
        repaired_str = "".join(str(b) for b in x)
        return repaired_str, self.evaluate_bitstring(repaired_str)
