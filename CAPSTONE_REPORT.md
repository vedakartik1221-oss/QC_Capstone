# Capstone Project Technical Report

**Project Title**: Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates  
**Domain**: Quantum Computing, Computational Chemistry, Machine Learning, Full-Stack Engineering  
**Benchmark Target**: Human $\beta$-Secretase 1 (BACE-1) Inhibitors (Alzheimer's Disease)  
**Implementation**: Python 3.11, Qiskit 2.5, RDKit, Scikit-Learn, Streamlit  

---

## Abstract
Drug discovery pipelines screen vast chemical spaces comprising millions of compounds to identify hits with therapeutic efficacy. Because downstream in vitro crystallography, assay development, and in vivo pharmacological characterization are prohibitively expensive, selecting a fixed budget of $K$ candidate molecules from an initial pool of $N$ candidates represents a critical combinatorial decision problem. In this work, we present a complete, runnable, and empirically validated computational drug-screening platform. We employ the public MoleculeNet BACE benchmark dataset (1,513 experimentally characterized compounds) to train a Random Forest biological activity classifier using RDKit-derived Morgan fingerprints (ECFP4) and Lipinski physicochemical descriptors. The resulting trained model achieves a test set ROC-AUC of **0.8794** and classification accuracy of **78.55%** on held-out test data without data leakage. 

We formulate the fixed-budget candidate selection problem as a Quadratic Unconstrained Binary Optimization (QUBO) problem with quadratic cardinality penalties and analytically derive the exact Ising Spin Cost Hamiltonian. We execute the Quantum Approximate Optimization Algorithm (QAOA) on the Qiskit Aer simulator across parameterized variational depth $p$. Empirical benchmarking against classical baselines demonstrates that QAOA achieves **100% solution optimality** ($\Delta E = 0.0000$) on an 8-qubit candidate instance with a feasible measurement sampling rate of **45.7%** (468/1024 shots). We provide an interactive Streamlit web dashboard, reproducible automated pytest suite (21 passing tests), exportable artifacts, and rigorous scientific discussions regarding NISQ feasibility, runtime complexity, and biochemical validation boundaries.

---

## 1. Problem Statement & Biological Background

### 1.1 The Computational Drug Discovery Bottleneck
The pharmaceutical lead discovery process is constrained by high attrition rates and extreme financial costs:
1. Virtual screening flags thousands of potential binders.
2. Wet-lab experimental throughput allows advancing only a small budget $K$ ($K \ll N$) of compounds into binding affinity assays and cytotoxicity profiling.
3. Simple single-metric ranking neglects multi-objective trade-offs between binding potency, molecular weight, lipophilicity (LogP), and synthetic accessibility.

### 1.2 Target Biology: Beta-Secretase 1 (BACE-1)
Human $\beta$-secretase 1 is an aspartyl protease that executes the initial and rate-limiting cleavage of Amyloid Precursor Protein (APP) at the N-terminal end of the amyloid-$\beta$ domain:
$$\text{APP} \xrightarrow{\text{BACE-1}} \text{sAPP}\beta + \text{C99} \xrightarrow{\gamma\text{-secretase}} \text{A}\beta_{40/42}$$
Accumulation of insoluble $\text{A}\beta_{42}$ peptides drives amyloid plaque formation, neuroinflammation, synaptic dysfunction, and cognitive decline in **Alzheimer's Disease**. Identifying small-molecule inhibitors with sub-micromolar potency that cross the blood-brain barrier (requiring strict adherence to Lipinski's Rule of 5) is a paramount medicinal chemistry goal.

---

## 2. Project Objectives

1. **Empirical Data Pipeline**: Clean, validate, and featurize real experimental data from the MoleculeNet BACE benchmark without synthesizing or fabricating labels.
2. **Machine Learning Predictive Modeling**: Train a Random Forest classifier to predict BACE-1 activity ($y \in \{0, 1\}$) from chemical fingerprints and descriptors, evaluating calibration and discrimination.
3. **Multi-Objective Composite Scoring**: Combine predicted activity probabilities with experimental affinities and Lipinski rule compliance into a well-calibrated score $s_i \in [0, 1]$.
4. **Rigorous QUBO & Ising Formulation**: Mathematically encode candidate selection under cardinality constraint $\sum x_i = K$ into a quadratic penalty objective and map it to an Ising Cost Hamiltonian.
5. **Genuine QAOA Implementation**: Construct, optimize, and sample variational quantum circuits on the Qiskit Aer simulator without replacing quantum execution with classical shortcuts.
6. **Classical Benchmarking**: Directly compare QAOA against a Greedy Top-K heuristic and an Exact Brute-Force enumeration solver.
7. **Interactive User Interface**: Deliver a 6-page responsive Streamlit application for end-to-end data exploration, 2D structure viewing, live prediction, quantum screening, and report export.

---

## 3. Mathematical & Theoretical Framework

### 3.1 Composite Candidate Scoring
For each candidate molecule $i$, the composite utility score $s_i$ is defined as:
$$s_i = w_{\text{pred}} P(\text{active})_i + w_{\text{affinity}} \widetilde{\text{pIC}_{50,i}} + w_{\text{lipinski}} \text{LipinskiPassRate}_i$$
where:
- $P(\text{active})_i \in [0, 1]$ is the Random Forest estimated probability of inhibition.
- $\widetilde{\text{pIC}_{50,i}} = \frac{\text{pIC}_{50,i} - \min(\text{pIC}_{50})}{\max(\text{pIC}_{50}) - \min(\text{pIC}_{50})} \in [0, 1]$ is the normalized experimental binding affinity.
- $\text{LipinskiPassRate}_i \in [0, 1]$ is the fraction of Lipinski's Rule of 5 criteria satisfied (MW $\le 500$, LogP $\le 5$, HBD $\le 5$, HBA $\le 10$, RotB $\le 10$).
- Standard weights: $w_{\text{pred}} = 0.60, w_{\text{affinity}} = 0.25, w_{\text{lipinski}} = 0.15$.

### 3.2 Fixed-Budget QUBO Formulation
We define binary decision variables $x_i \in \{0, 1\}$, where $x_i = 1$ denotes selection.
The constrained optimization problem is:
$$\max_{x} \sum_{i=1}^N s_i x_i \quad \text{subject to} \quad \sum_{i=1}^N x_i = K$$
Equivalently:
$$\min_{x} -\sum_{i=1}^N s_i x_i \quad \text{subject to} \quad \sum_{i=1}^N x_i = K$$

We penalize cardinality violations quadratically with multiplier $A$:
$$E(x) = -\sum_{i=1}^N s_i x_i + A \left( \sum_{i=1}^N x_i - K \right)^2$$
Expanding the quadratic term:
$$\left( \sum_{i=1}^N x_i - K \right)^2 = \sum_{i=1}^N x_i^2 + 2\sum_{i < j} x_i x_j - 2K\sum_{i=1}^N x_i + K^2$$
Using the idempotent property of binary variables $x_i^2 = x_i$:
$$E(x) = \sum_{i=1}^N \Big[ -s_i + A(1 - 2K) \Big] x_i + \sum_{i < j} 2A \, x_i x_j + A K^2$$

### 3.3 Analytical Mapping to the Ising Hamiltonian
To execute on quantum hardware, binary variables $x_i$ are mapped to Pauli-Z spin operators $Z_i \in \{+1, -1\}$ via:
$$x_i = \frac{I - Z_i}{2}$$
Substituting into the linear and quadratic terms:
$$x_i = \frac{1}{2} I - \frac{1}{2} Z_i$$
$$x_i x_j = \frac{1}{4} \Big( I - Z_i - Z_j + Z_i Z_j \Big)$$

Regrouping terms yields the Cost Hamiltonian:
$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j + C \cdot I$$
where:
1. **Longitudinal Magnetic Fields**:
   $$h_i = \frac{s_i}{2} + \frac{A}{2}(2K - N)$$
2. **Ising Pairwise Couplings**:
   $$J_{ij} = \frac{A}{2} \quad \forall \; i < j$$
3. **Energy Constant**:
   $$C = A K^2 - \frac{1}{2}\sum_{i=1}^N s_i + \frac{N A (1 - 2K)}{2} + \frac{N(N-1)A}{4}$$

Every basis state $|x\rangle$ has an eigenvalue $\langle x | H_C | x \rangle$ exactly equal to the QUBO energy $E(x)$.

### 3.4 QAOA Circuit Architecture
1. **Initial State**: Uniform superposition across all $2^N$ states:
   $$|\psi_0\rangle = H^{\otimes N} |0\rangle^{\otimes N}$$
2. **Alternating Unitaries ($p$ layers)**:
   $$|\psi(\boldsymbol{\gamma}, \boldsymbol{\beta})\rangle = \prod_{l=1}^p \left( e^{-i \beta_l H_B} e^{-i \gamma_l H_C} \right) |\psi_0\rangle$$
   - **Cost Unitary** $e^{-i \gamma_l H_C}$: Single-qubit rotations $R_Z(2 \gamma_l h_i)$ and two-qubit rotations $R_{ZZ}(2 \gamma_l J_{ij})$.
   - **Mixer Unitary** $e^{-i \beta_l H_B}$: Transverse magnetic field rotations $\prod_i R_X(2 \beta_l)$ where $H_B = \sum_{i=1}^N X_i$.
3. **Classical Optimization Loop**: COBYLA optimizer updates $(\boldsymbol{\gamma}, \boldsymbol{\beta})$ to minimize:
   $$\langle H_C \rangle = \langle \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) | H_C | \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle$$
4. **Measurement**: Circuit sampled on `AerSimulator` ($M=1024$ shots) to yield bitstring distribution $P(x)$.

---

## 4. System Flowchart & Pseudocode

### 4.1 System Flowchart
```
[Raw BACE Data (SMILES, Labels)]
              |
              v
[RDKit Preprocessing & Validation] ---> (Removes corrupt SMILES, Canonicalizes)
              |
              v
[Feature Extraction] ---> (ECFP4 Fingerprints: 512 bits + 7 Descriptors)
              |
              v
[Stratified 80/20 Train/Test Split] ---> (StandardScaler fitted strictly on Train)
              |
              v
[Random Forest Training] ---> (Evaluates ROC-AUC, Accuracy, F1 on Test Set)
              |
              v
[Candidate Pool & Composite Scoring] ---> (Calculates s_i = 0.6*P + 0.25*Aff + 0.15*Lip)
              |
              v
[QUBO & Ising Hamiltonian Derivation] ---> (h_i, J_ij, C_offset)
              |
              +------------------------------------+
              |                                    |
              v                                    v
     [QAOA Circuit Execution]            [Classical Baselines]
  (Hadamard -> Cost/Mixer Layers)      (1. Greedy Top-K Sorting)
              |                        (2. Exact 2^N Enumeration)
              v                                    |
     [AerSimulator Sampling]                       |
              |                                    |
              +------------------+-----------------+
                                 |
                                 v
                 [Comparative Benchmarking & Evaluation]
                 - Optimality Gap (Delta E = E - E_exact)
                 - Candidate Overlap Percentage
                 - Feasible Sample Rate
                                 |
                                 v
                     [Streamlit Web Dashboard]
```

### 4.2 Algorithm Pseudocode
```
Algorithm 1: Quantum Drug Screening Pipeline
Input: Molecular Dataset D, Subset Size N, Selection Budget K, Depth p, Shots M
Output: Selected Candidate Molecules, Optimality Gap, Feasible Rate

1: D_clean <- ValidateAndSanitize(D)
2: X_train, y_train, X_test, y_test <- ExtractFeaturesAndSplit(D_clean)
3: Model <- TrainRandomForest(X_train, y_train)
4: Candidates <- SelectReproducibleSubset(D_clean, N)
5: for each mol_i in Candidates do
6:     p_i <- Model.PredictProba(mol_i)
7:     s_i <- ComputeCompositeScore(p_i, mol_i.pIC50, mol_i.Lipinski)
8: end for
9: A <- 2.0 * max(s)
10: Compute h_i, J_ij, and Offset using equations in Section 3.3
11: Initialize gamma, beta in [0, pi]
12: (gamma*, beta*) <- ClassicalOptimizer(min <psi(gamma, beta)| H_C |psi(gamma, beta)>)
13: Counts <- AerSimulator.Run(QAOA_Circuit(gamma*, beta*), shots=M)
14: x_qaoa <- SelectBestFeasibleBitstring(Counts)
15: x_exact <- ArgMin_{x in {0, 1}^N, sum x = K} E(x)
16: Gap <- E(x_qaoa) - E(x_exact)
17: return x_qaoa, Gap, FeasibleRate(Counts)
```

---

## 5. Implementation Architecture

The repository is structured with clean modular separation:
- `src/data_loader.py`: Dataset download with caching, sanitation, deduplication, and balanced sample creation.
- `src/molecular_features.py`: RDKit Lipinski descriptors, Morgan fingerprints (ECFP4), valence validation, and 2D SVG depiction.
- `src/preprocessing.py`: Leakage-free train/test splitting and descriptor scaling.
- `src/activity_model.py`: Random Forest classification, calibration evaluation, inference, and serialization.
- `src/qubo_formulation.py`: Analytical QUBO matrix construction, Ising Hamiltonian coefficients, and greedy bitstring repair.
- `src/qaoa_optimizer.py`: Parameterized Qiskit `QuantumCircuit` construction ($R_Z, R_{ZZ}, R_X$), COBYLA optimization, and AerSimulator measurement sampling.
- `src/classical_baseline.py`: Greedy Top-K and exact brute-force enumeration solvers.
- `src/visualization.py`: Plotly interactive figures (ROC curves, confusion matrices, convergence curves, measurement distributions).
- `app.py`: Full multi-page Streamlit web application.
- `tests/`: 21 automated unit and integration tests executed with pytest.

---

## 6. Empirical Results & Performance Evaluation

All results reported below were generated through **actual script and test executions** on the repository.

### 6.1 Biological Activity Classification Metrics
- **Dataset**: MoleculeNet BACE (1,513 valid chemical records).
- **Split Strategy**: 80% Train (1,210 molecules), 20% Held-Out Test (303 molecules).
- **Model**: Random Forest Classifier ($N_{\text{trees}} = 150$, balanced class weights).

| Evaluation Metric | Measured Value | Interpretation |
| :--- | :--- | :--- |
| **Test Accuracy** | **78.55%** (238 / 303) | High generalizability across diverse chemical scaffolds |
| **ROC-AUC** | **0.8794** | Strong discriminative ability between inhibitors and non-binders |
| **Precision** | **0.7589** | 75.9% of predicted actives are verified true experimental inhibitors |
| **Recall (Sensitivity)**| **0.7754** | Captures 77.5% of all active inhibitors in the test partition |
| **F1-Score** | **0.7670** | Harmonious balance between precision and sensitivity |

**Test Confusion Matrix**:
```
                      Predicted Inactive (0)    Predicted Active (1)
True Inactive (0):            131 (TN)                   34 (FP)
True Active (1):               31 (FN)                  107 (TP)
```

### 6.2 Quantum Screening Benchmark ($N = 8, K = 3, p = 1, M = 1024$)
Candidate subset evaluated from the held-out test set with composite scores $s \in [0.217, 0.923]$:

| Method | QUBO Energy $E(x)$ | Total Score Sum | Feasible ($\sum x = 3$) | Optimality Gap $\Delta E$ | Overlap with Exact | Runtime |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **QAOA (Qiskit Aer)** | **-1.7179** | **1.7179** | **Yes** | **0.0000** | **100.0%** | **0.5585s** |
| **Top-K Greedy** | **-1.7179** | **1.7179** | **Yes** | **0.0000** | **100.0%** | **0.0015s** |
| **Exact QUBO (Enumeration)**| **-1.7179** | **1.7179** | **Yes** | **0.0000** | **100.0%** | **0.0052s** |

- **QAOA Sampling Feasibility Rate**: **45.7%** (468 of 1024 measurement shots sampled valid 3-candidate combinations).
- **Chosen Optimal Bitstring**: `10100010`
- **Selected Molecules**:
  1. `MOL_BACE_1111` ($s = 0.423$)
  2. `MOL_BACE_558` ($s = 0.923$)
  3. `MOL_BACE_1121` ($s = 0.372$)
- **Runtime Breakdown for QAOA**:
  - Classical parameter optimization (COBYLA): **0.5360s**
  - Simulator quantum sampling ($1024$ shots): **0.0225s**
  - Total: **0.5585s**

---

## 7. Computational Complexity & NISQ Hardware Analysis

### 7.1 Classical vs Quantum Complexity Comparison
- **Top-K Baseline**: Requires sorting array of size $N$, running in $O(N \log N)$ time and $O(N)$ memory. It is computationally optimal for purely linear utility functions.
- **Exact QUBO Enumeration**: Requires evaluating all $2^N$ bitstrings across the Boolean hypercube. For small instances ($N \le 20$), runtimes are under 1 second. For $N = 100$, $2^{100} \approx 1.27 \times 10^{30}$ states renders classical brute force physically impossible.
- **QAOA on Classical Simulators**: Simulating an $N$-qubit statevector requires storing $2^N$ complex amplitudes ($2^N \times 16$ bytes). An $N=30$ qubit simulation requires $\approx 16\,\text{GB}$ of RAM, while $N=40$ requires $\approx 16\,\text{TB}$, causing exponential memory scaling on classical computers.
- **QAOA on Fault-Tolerant Quantum Hardware (QPU)**: Circuit depth scales as $O(p \cdot N^2)$ for all-to-all connectivity. State preparation and measurement take $O(M)$ time regardless of Hilbert space dimension $2^N$.

### 7.2 NISQ Limitations & Feasibility
On contemporary Noisy Intermediate-Scale Quantum (NISQ) devices, two-qubit gate fidelities (typically $99.0\% - 99.8\%$) and decoherence times ($T_1, T_2 \approx 100\,\mu\text{s}$) impose strict limits on circuit depth $p$. For unconstrained linear objectives, QAOA cannot beat classical greedy sorting. However, when complex **pairwise non-linear chemical interactions** (e.g., pharmacophore synergy, target cross-reactivity, structural scaffold diversity constraints) are introduced into the QUBO matrix $Q_{ij} \ne \text{const}$, the objective landscape becomes NP-hard and non-convex, providing the exact regime where quantum heuristic sampling is theorized to offer quadratic or super-polynomial advantages.

---

## 8. Scientific Limitations & Ethical Considerations

1. **In Silico Hypothesis vs Wet-Lab Reality**: Neither machine learning predictions nor QAOA optimization prove biochemical binding affinity, non-toxicity, bioavailability, or clinical efficacy. Computational screening provides prioritized hypotheses for laboratory validation.
2. **Target Specificity**: The model is trained specifically on human BACE-1. Predictions cannot be extrapolated to other aspartyl proteases (e.g., Cathepsin D, Renin) without retraining.
3. **Absence of Synthetic Speedup Claims**: Simulator execution times are classical simulation times; they do not represent physical quantum processor runtimes.

---

## 9. Conclusion & Future Directions

This project successfully demonstrates the construction, verification, and benchmarking of a runnable quantum-classical drug screening system. By combining RDKit featurization, high-performance Random Forest classification (ROC-AUC = 0.8794), and genuine Qiskit QAOA execution, we have verified that combinatorial subset selection under cardinality constraints can be mapped to an Ising Hamiltonian and solved variationally on a quantum simulator.

**Future Extensions**:
1. Integration of pharmacophore diversity penalties into the off-diagonal $Q_{ij}$ terms to actively penalize selecting structurally redundant molecules.
2. Implementation of XY-mixer Hamiltonians to preserve the $\sum x_i = K$ subspace natively, achieving 100% feasible sampling by design.
3. Execution on physical cloud-based QPUs (e.g., IBM Quantum Eagle or Heron architectures) through Qiskit Runtime Primitives.
