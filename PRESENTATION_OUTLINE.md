# 10-Slide Capstone Presentation Outline

**Project Title**: Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates  
**Audience**: Senior Quantum Computing Faculty, Computational Chemists, and Industry Evaluators  

---

### Slide 1: Title, Team, and Executive Summary
- **Title**: Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates
- **Core Theme**: A hybrid quantum-classical pipeline combining predictive molecular machine learning with the Quantum Approximate Optimization Algorithm (QAOA) for combinatorial drug lead prioritization.
- **Key Deliverables**: Real MoleculeNet BACE dataset, RDKit featurization, Random Forest classifier (ROC-AUC 0.8794), genuine QAOA on Qiskit Aer, classical baselines, 21 passing automated tests, and interactive Streamlit UI.
- **Presenter Note**: "Today we present a complete, fully implemented, runnable, and empirically verified hybrid quantum-classical drug screening platform targeting BACE-1 for Alzheimer's disease."

---

### Slide 2: The Biological Challenge: BACE-1 & Alzheimer's Disease
- **Target**: Human Beta-Secretase 1 (BACE-1), an aspartic protease.
- **Mechanism**: Cleaves Amyloid Precursor Protein (APP) at the $\beta$-site, producing neurotoxic Amyloid-$\beta$ ($A\beta_{42}$) peptides that form senile plaques in Alzheimer's.
- **Medicinal Chemistry Constraints**: Inhibitors must exhibit high binding potency ($\text{IC}_{50} < 1\,\mu\text{M}$) while satisfying Lipinski's Rule of 5 to ensure blood-brain barrier permeability.
- **Presenter Note**: "Drug discovery against BACE-1 has suffered high clinical failure rates because molecules either lack potency or fail drug-likeness rules. Our system incorporates both biological potency and Lipinski drug-likeness into candidate scoring."

---

### Slide 3: The Combinatorial Screening Bottleneck
- **The Dilemma**: High-throughput virtual screening generates thousands of prospective hits. However, expensive wet-lab assays permit advancing only $K$ candidates ($K \ll N$) to synthesis and crystallography.
- **The Optimization Goal**: Maximize total candidate utility $\sum s_i x_i$ under a fixed budget constraint $\sum x_i = K$.
- **Why Quantum?**: While linear selection is classically simple, real-world drug selection introduces pairwise interaction penalties (chemical scaffold redundancy, cross-reactivity), transforming the selection into an NP-hard non-convex QUBO.
- **Presenter Note**: "We formulate candidate selection as a fixed-budget QUBO problem, bridging computational chemistry with quantum combinatorial optimization."

---

### Slide 4: Data Pipeline & Molecular Featurization
- **Dataset**: MoleculeNet BACE benchmark (1,513 experimentally validated compounds; 691 Active, 822 Inactive).
- **RDKit Featurization**:
  - Morgan Fingerprints (ECFP4, 512 bits) capturing local chemical substructures.
  - 7 Physicochemical Descriptors: Molecular Weight (MW), LogP, H-Bond Donors (HBD), H-Bond Acceptors (HBA), Rotatable Bonds (RotB), TPSA, and Lipinski compliance score.
- **Leakage Prevention**: StandardScaler fitted exclusively on training split; canonical SMILES verification eliminates corrupted records.
- **Presenter Note**: "We maintain 100% data integrity: zero synthetic or fabricated labels. Preprocessing is strictly isolated to prevent test set data leakage."

---

### Slide 5: Predictive Modeling: Random Forest Activity Classifier
- **Model**: Balanced Random Forest Classifier (150 estimators).
- **Partitioning**: 80% Train (1,210 molecules), 20% Held-Out Test (303 molecules).
- **Empirical Test Metrics**:
  - **ROC-AUC**: **0.8794**
  - **Accuracy**: **78.55%**
  - **Precision**: **75.89%** | **Recall**: **77.54%** | **F1-Score**: **0.7670**
  - **Confusion Matrix**: 131 True Negatives, 107 True Positives, 34 False Positives, 31 False Negatives.
- **Presenter Note**: "The model demonstrates strong discriminative ability. The predicted active probability $P(\text{active})$ serves as the primary component of our multi-objective candidate utility score."

---

### Slide 6: Mathematical Formulation: QUBO & Ising Mapping
- **QUBO Objective**:
  $$E(x) = -\sum_{i=1}^N s_i x_i + A\left(\sum_{i=1}^N x_i - K\right)^2$$
  Expanded with $x_i^2 = x_i$:
  $$E(x) = \sum_{i=1}^N [-s_i + A(1 - 2K)] x_i + \sum_{i < j} 2A \, x_i x_j + A K^2$$
- **Analytical Ising Mapping** ($x_i = \frac{I - Z_i}{2}$):
  $$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j + C \cdot I$$
  where $h_i = \frac{s_i}{2} + \frac{A}{2}(2K - N)$ and $J_{ij} = \frac{A}{2}$.
- **Verification**: Mathematically validated to produce identical energy values to the QUBO objective across all $2^N$ basis states.
- **Presenter Note**: "We derived the exact analytical coefficients for longitudinal magnetic fields $h_i$ and Ising couplings $J_{ij}$, ensuring zero penalty mismatch."

---

### Slide 7: QAOA Variational Quantum Algorithm
- **Quantum Circuit Architecture**:
  1. Initialization: $|+\rangle^{\otimes N} = H^{\otimes N}|0\rangle^{\otimes N}$ (equal superposition).
  2. Cost Unitary: $e^{-i \gamma H_C}$ implemented via single-qubit $R_Z(2 \gamma h_i)$ and two-qubit $R_{ZZ}(2 \gamma J_{ij})$ gates.
  3. Mixer Unitary: $e^{-i \beta H_B} = \prod_i R_X(2 \beta)$ (transverse field mixer).
  4. Alternating depth $p$ layers.
- **Classical Optimizer**: COBYLA algorithm variationally tuning $(\boldsymbol{\gamma}, \boldsymbol{\beta})$ to minimize energy expectation.
- **Simulator**: Local Qiskit Aer simulator with 1024 measurement shots.
- **Presenter Note**: "Our implementation executes genuine quantum circuits in Qiskit 2.5 with explicit gate decompositions—never a classical placeholder."

---

### Slide 8: Empirical Results & Classical Benchmarking
- **Instance**: $N = 8$ candidate molecules, budget $K = 3$, QAOA depth $p = 1$, 1024 shots.
- **Comparative Findings**:
  - **QAOA (Aer Sim)**: Objective $E = \mathbf{-1.7179}$, Score $= \mathbf{1.7179}$, Feasible: **Yes**, Gap $= \mathbf{0.0000}$, Overlap $= \mathbf{100.0\%}$, Time $= 0.5585\,\text{s}$.
  - **Top-K Greedy**: Objective $E = \mathbf{-1.7179}$, Score $= \mathbf{1.7179}$, Feasible: **Yes**, Gap $= \mathbf{0.0000}$, Overlap $= \mathbf{100.0\%}$, Time $= 0.0015\,\text{s}$.
  - **Exact QUBO**: Objective $E = \mathbf{-1.7179}$, Score $= \mathbf{1.7179}$, Feasible: **Yes**, Gap $= \mathbf{0.0000}$, Overlap $= \mathbf{100.0\%}$, Time $= 0.0052\,\text{s}$.
- **Feasible Shot Rate**: **45.7%** (468 of 1024 shots directly sampled valid 3-candidate states).
- **Presenter Note**: "QAOA found the exact global optimum, matching both classical baselines with zero optimality gap and 100% candidate overlap."

---

### Slide 9: Full-Stack Web Application (Streamlit)
- **6 Integrated Pages**:
  1. **Dashboard**: High-level system KPIs, target biology, and architecture flow.
  2. **Dataset Explorer**: Searchable table, filterable by active/inactive, with RDKit 2D chemical structure rendering.
  3. **Activity Prediction**: Interactive inference for custom user SMILES with Lipinski Rule of 5 evaluations and disclaimers.
  4. **Quantum Screening**: Interactive controls for $N, K, p$, shots, and weights; live QAOA execution and convergence curves.
  5. **Classical vs Quantum**: Direct side-by-side benchmarking, optimality gaps, and execution time comparison.
  6. **Results & Reports**: Exportable CSV of screened leads and downloadable full JSON reports.
- **Presenter Note**: "Every UI button connects to functional backend code. Users can inspect 2D molecular structures, tune quantum depth, and export prioritized leads to CSV."

---

### Slide 10: Scientific Honesty, Limitations, and Road Ahead
- **Scientific Honesty**:
  - Computational screening generates prioritized research hypotheses, not verified pharmacological drugs.
  - QAOA on classical simulators does not claim a practical speedup over classical heuristics on simple cardinality constraints.
- **NISQ Considerations**: Physical QPU execution requires error mitigation and low-depth circuits to prevent gate fidelity decay.
- **Next Steps**:
  - Extend QUBO with pairwise pharmacophore diversity penalties ($Q_{ij} \ne \text{const}$) to prevent selecting chemically redundant analogs.
  - Implement subspace-preserving XY-mixers to ensure 100% feasibility by construction.
  - Cloud execution on physical IBM Quantum QPUs via Qiskit Runtime.
- **Presenter Note**: "By grounding quantum computing in real biological datasets, rigorous mathematics, and transparent benchmarking, this capstone establishes a reproducible foundation for hybrid quantum drug discovery."
