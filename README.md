# Quantum Computing-Based Drug Screening System to Identify Promising Drug Candidates

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Qiskit 2.5](https://img.shields.io/badge/Qiskit-2.5-613399.svg)](https://qiskit.org/)
[![RDKit](https://img.shields.io/badge/RDKit-2024+-green.svg)](https://www.rdkit.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.64-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A hybrid quantum-classical computational drug discovery platform that integrates predictive molecular machine learning with the **Quantum Approximate Optimization Algorithm (QAOA)** to solve fixed-budget combinatorial candidate screening for **Beta-Secretase 1 (BACE-1)** inhibitors.

---

## 📌 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement & Biological Context](#2-problem-statement--biological-context)
3. [Architecture & Workflow](#3-architecture--workflow)
4. [Dataset Provenance & Schema](#4-dataset-provenance--schema)
5. [Mathematical Formulation: QUBO & Ising Mapping](#5-mathematical-formulation-qubo--ising-mapping)
6. [QAOA Quantum Circuit & Implementation](#6-qaoa-quantum-circuit--implementation)
7. [Classical Baselines & Benchmarking](#7-classical-baselines--benchmarking)
8. [Computational Complexity Analysis](#8-computational-complexity-analysis)
9. [Installation & Windows Setup](#9-installation--windows-setup)
10. [Reproduction Guide](#10-reproduction-guide)
11. [Running Automated Tests](#11-running-automated-tests)
12. [Streamlit Web Application](#12-streamlit-web-application)
13. [Measured Empirical Results](#13-measured-empirical-results)
14. [Scientific Limitations & Ethical Disclaimers](#14-scientific-limitations--ethical-disclaimers)

---

## 1. Project Overview

Computational high-throughput screening evaluates millions of chemical structures to prioritize leads for in vitro assays. However, wet-lab synthesis and biological testing are constrained by resource and budget limitations. Selecting an optimal subset of $K$ drug candidates from a larger library of $N$ candidates is a combinatorial optimization challenge.

This capstone system:
1. Featurizes molecular structures using **RDKit** (Morgan fingerprints and Lipinski physicochemical descriptors).
2. Predicts target biological activity using a **Random Forest classifier** trained on benchmark **MoleculeNet BACE** data.
3. Combines activity probabilities, experimental binding affinities ($\text{pIC}_{50}$), and Lipinski Rule of 5 compliance into composite screening scores $s_i$.
4. Formulates fixed-budget candidate selection as a **Quadratic Unconstrained Binary Optimization (QUBO)** problem with a quadratic cardinality penalty.
5. Maps the QUBO into an **Ising Spin Hamiltonian** ($H_C$) and solves it variationally using **QAOA** on a local **Qiskit Aer** quantum simulator.
6. Evaluates QAOA against a greedy **Top-K ranking** baseline and an **Exact Classical QUBO** solver (brute-force enumeration).
7. Provides an interactive **Streamlit web application** for real-time exploratory screening, 2D molecular depiction, and metrics visualization.

---

## 2. Problem Statement & Biological Context

### Biological Target: Human Beta-Secretase 1 (BACE-1)
- **Role in Neurodegeneration**: BACE-1 is a membrane-bound aspartic protease responsible for the initial rate-limiting proteolytic cleavage of Amyloid Precursor Protein (APP). This generates $\text{A}\beta_{40}$ and $\text{A}\beta_{42}$ peptides that aggregate into neurotoxic senile plaques in **Alzheimer's Disease (AD)**.
- **Drug Discovery Objective**: Identify small-molecule inhibitors that effectively block BACE-1 catalytic activity while satisfying drug-likeness criteria (blood-brain barrier penetration, molecular weight $\le 500$, low rotatable bond counts).
- **Combinatorial Budget Bottleneck**: From a synthesized library of $N$ candidates, a research laboratory can typically advance only $K \ll N$ compounds to expensive crystallography and animal assays. Picking the subset that maximizes expected utility without violating selection constraints is an NP-hard subset selection problem.

---

## 3. Architecture & Workflow

```
+-------------------------------------------------------------+
|                     MoleculeNet BACE Dataset                |
|                    (1,513 Valid Compounds)                  |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  RDKit Feature Engineering                  |
|    - Morgan Fingerprints (ECFP4, 512 bits)                  |
|    - Descriptors: MW, LogP, HBD, HBA, RotB, TPSA           |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|         Leakage-Free Train/Test Split (80% / 20%)           |
|         StandardScaler fitted ONLY on Training Data         |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|           Random Forest Activity Prediction Model           |
|            ROC-AUC: 0.8794  |  Test Accuracy: 78.55%        |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                  Composite Scoring Function                 |
|   s_i = 0.60*P(active) + 0.25*Norm(pIC50) + 0.15*Lipinski   |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|             Fixed-Budget QUBO & Ising Mapping               |
|            E(x) = -sum(s_i x_i) + A * (sum(x_i) - K)^2      |
|             H_C = sum h_i Z_i + sum J_ij Z_i Z_j + Offset   |
+-------------------------------------------------------------+
             /                                   \
            v                                     v
+-----------------------+             +-----------------------+
|      QAOA Solver      |             |  Classical Baselines  |
|  - Parameterized Circuit |             |  1. Top-K Greedy      |
|  - Qiskit Aer Sim     |             |  2. Exact Brute Force |
|  - COBYLA Optimizer   |             +-----------------------+
+-----------------------+                         |
            \                                     /
             v                                   v
+-------------------------------------------------------------+
|                Benchmarking & Comparative Report            |
|         Optimality Gap, Solution Overlap, Feasible Rate     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|             Streamlit UI & Exportable Artifacts             |
+-------------------------------------------------------------+
```

---

## 4. Dataset Provenance & Schema

- **Source**: MoleculeNet benchmark suite (Subramanian et al., *MoleculeNet: A Benchmark for Molecular Machine Learning*, Chem. Sci., 2018).
- **Download URL**: `https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/bace.csv`
- **Total Valid Records**: 1,513 compounds (691 Active [45.7%], 822 Inactive [54.3%]).
- **Key Columns**:
  - `mol`: Standardized SMILES chemical structure.
  - `CID`: Compound Identifier.
  - `Class`: Experimental binary biological activity (1 = active inhibitor $\text{IC}_{50} \le 1\,\mu\text{M}$; 0 = inactive).
  - `pIC50`: $-\log_{10}(\text{IC}_{50}\text{ in M})$ experimental quantitative binding affinity.
  - Calculated physicochemical descriptors: `MW`, `AlogP`, `HBA`, `HBD`, `RB`, `PSA`.

---

## 5. Mathematical Formulation: QUBO & Ising Mapping

### 5.1 Optimization Objective
Let binary variable $x_i \in \{0, 1\}$ denote whether candidate molecule $i$ is selected ($x_i=1$) or excluded ($x_i=0$).
Let $s_i \in [0, 1]$ be the composite score:
$$s_i = w_{\text{pred}} \cdot P(\text{active})_i + w_{\text{affinity}} \cdot \widetilde{\text{pIC}_{50,i}} + w_{\text{lipinski}} \cdot \text{LipinskiPassRate}_i$$
where weights sum to 1.0 ($w_{\text{pred}}=0.60, w_{\text{affinity}}=0.25, w_{\text{lipinski}}=0.15$).

We seek to select exactly $K$ candidates to maximize total utility:
$$\max \sum_{i=1}^N s_i x_i \iff \min -\sum_{i=1}^N s_i x_i \quad \text{subject to} \quad \sum_{i=1}^N x_i = K$$

### 5.2 Penalty Embedding into QUBO
To formulate an unconstrained optimization problem, the cardinality constraint is penalized quadratically:
$$E(x) = -\sum_{i=1}^N s_i x_i + A \cdot \left(\sum_{i=1}^N x_i - K\right)^2$$
where penalty multiplier $A \ge 1.5 \cdot \max(s_i)$ guarantees that selecting an invalid number of candidates costs more than any possible score gain.

Expanding the squared penalty:
$$\left(\sum_{i=1}^N x_i - K\right)^2 = \sum_{i=1}^N x_i^2 + 2\sum_{i < j} x_i x_j - 2K\sum_{i=1}^N x_i + K^2$$
Using the idempotent binary identity $x_i^2 = x_i$:
$$E(x) = \sum_{i=1}^N \Big[ -s_i + A(1 - 2K) \Big] x_i + \sum_{i < j} 2A \, x_i x_j + A K^2$$

### 5.3 Analytical Mapping to Ising Spin Hamiltonian
Using the standard Pauli-Z mapping $x_i = \frac{I - Z_i}{2}$ where $Z_i \in \{+1, -1\}$:
$$x_i x_j = \frac{1}{4} (I - Z_i - Z_j + Z_i Z_j)$$

Substituting into $E(x)$ gives the Cost Hamiltonian:
$$H_C = \sum_{i=1}^N h_i Z_i + \sum_{i < j} J_{ij} Z_i Z_j + C \cdot I$$
where:
1. **Longitudinal Magnetic Fields**:
   $$h_i = \frac{s_i}{2} + \frac{A}{2}(2K - N)$$
2. **Ising Pairwise Couplings**:
   $$J_{ij} = \frac{A}{2} \quad \forall \; i < j$$
3. **Identity Energy Constant**:
   $$C = A K^2 - \frac{1}{2}\sum_{i=1}^N s_i + \frac{NA(1 - 2K)}{2} + \frac{N(N-1)A}{4}$$

Every computational basis state $|x\rangle$ has an eigenvalue $\langle x | H_C | x \rangle$ exactly equal to the QUBO cost $E(x)$.

---

## 6. QAOA Quantum Circuit & Implementation

### Circuit Architecture
1. **Initialization**: Prepare uniform superposition state $|+\rangle^{\otimes N}$ using Hadamard gates:
   $$|\psi_0\rangle = H^{\otimes N} |0\rangle^{\otimes N} = \frac{1}{\sqrt{2^N}} \sum_{x \in \{0, 1\}^N} |x\rangle$$
2. **Alternating Unitaries ($p$ layers)**:
   - **Cost Unitary**: $U(C, \gamma_l) = e^{-i \gamma_l H_C}$:
     - Single-qubit rotation $R_Z(2 \gamma_l h_i)$ on each qubit $i$.
     - Two-qubit Ising coupling $R_{ZZ}(2 \gamma_l J_{ij})$ on each interacting pair $(i, j)$.
   - **Mixer Unitary**: $U(B, \beta_l) = e^{-i \beta_l H_B} = \prod_{i=1}^N R_X(2 \beta_l)$ with transverse field mixer $H_B = \sum_{i=1}^N X_i$.
3. **Parameter Optimization**:
   The variational angles $(\boldsymbol{\gamma}, \boldsymbol{\beta})$ are optimized by classical optimizer (COBYLA) to minimize expected cost:
   $$\min_{\boldsymbol{\gamma}, \boldsymbol{\beta}} \langle \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) | H_C | \psi(\boldsymbol{\gamma}, \boldsymbol{\beta}) \rangle$$
4. **Measurement Sampling & Bitstring Decoding**:
   The circuit is measured with $M = 1024$ shots on `qiskit_aer.AerSimulator`. The bitstrings are evaluated for objective energy, score sum, and feasibility $\sum x_i == K$.

---

## 7. Classical Baselines & Benchmarking

To ensure rigorous scientific honesty, QAOA is evaluated against two classical methods on identical subsets, scores, and constraints:
1. **Greedy Top-K Baseline**:
   Sorts candidate scores $s_i$ descending and selects the top $K$ compounds. Time complexity $O(N \log N)$.
2. **Exact Classical QUBO Solver (Enumeration)**:
   Evaluates all $2^N$ bitstrings across the hypercube to determine the global optimum $E_{\text{Exact}}^*$. Time complexity $O(2^N)$.

**Optimality Gap**:
$$\Delta E = E_{\text{Method}} - E_{\text{Exact}}^* \ge 0$$
where $\Delta E = 0$ denotes exact global optimality.

---

## 8. Computational Complexity Analysis

| Method | Classical Time Complexity | Quantum / Simulator Time | Space / Memory Complexity | Feasibility Guarantee |
| :--- | :--- | :--- | :--- | :--- |
| **Top-K Greedy** | $O(N \log N)$ | N/A | $O(N)$ | Always Feasible |
| **Exact QUBO** | $O(2^N)$ | N/A | $O(1)$ | Always Feasible |
| **QAOA (Classical Sim)** | $O(N_{\text{iter}} \cdot 2^N)$ | Simulated statevector | $O(2^N)$ statevector amplitudes | Probabilistic (repaired if needed) |
| **QAOA (Fault-Tolerant QPU)** | $O(N_{\text{iter}} \cdot N_{\text{shots}})$ | $O(p \cdot N^2)$ circuit depth | $O(N)$ physical qubits | Probabilistic (sampling distribution) |

---

## 9. Installation & Windows Setup

### Prerequisites
- Windows 10/11 (64-bit)
- Python 3.11.x (tested on Python 3.11.9)
- Git (optional)

### Setup Instructions (PowerShell or Command Prompt)
```powershell
# Navigate to project directory
cd "c:\Users\G VEDA KARTIK\OneDrive\Desktop\QC"

# Verify Python version
python --version

# Install dependencies
pip install -r requirements.txt
```

---

## 10. Reproduction Guide

### Stage 1: Data Preparation
Downloads the BACE benchmark, sanitizes chemical SMILES, and creates `data/sample/sample_bace.csv`:
```powershell
python scripts/prepare_data.py
```

### Stage 2: Train Activity Prediction Model
Featurizes molecules, trains Random Forest classifier on 1,210 training molecules, evaluates on 303 test molecules, and saves model artifacts:
```powershell
python scripts/train_model.py
```

### Stage 3: Run Quantum Screening & Classical Benchmarks
Executes the QAOA circuit on Qiskit Aer simulator and compares against classical baselines:
```powershell
python scripts/run_screening.py
```

### Stage 4: Launch Interactive Web Application
```powershell
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## 11. Running Automated Tests

Run the full pytest suite (21 automated unit and integration tests):
```powershell
python -m pytest -v tests/
```

### Test Suite Structure
- `tests/test_data_loader.py`: Validation, missing SMILES handling, duplicate removal, balanced sampling.
- `tests/test_molecular_features.py`: RDKit validation, Lipinski descriptor calculation, Morgan fingerprints, SVG generation.
- `tests/test_qubo.py`: Hand-calculated invariants, Ising Hamiltonian eigenvalue consistency, greedy repair logic.
- `tests/test_qaoa.py`: Parameterized circuit building, COBYLA optimization, AerSimulator sampling.
- `tests/test_classical_baseline.py`: Greedy Top-K, Exact QUBO brute-force enumeration, comparison metrics.
- `tests/test_pipeline.py`: Full end-to-end integration test from raw data to benchmark table.

---

## 12. Streamlit Web Application

The interactive web dashboard includes 6 fully functional pages:
1. **Dashboard**: High-level metrics, BACE-1 target overview, architecture diagram, and biological disclaimers.
2. **Dataset Explorer**: Searchable and filterable molecular table, 2D chemical structure rendering via RDKit SVG, and descriptor inspector.
3. **Activity Prediction**: Real-time biological activity prediction for arbitrary custom SMILES with Lipinski Rule of 5 evaluations and disclaimers.
4. **Quantum Screening**: Interactive controls for candidate subset size $N$, budget $K$, QAOA depth $p$, measurement shots, and random seed. Live execution on Qiskit Aer simulator with convergence curves and measurement probability distributions.
5. **Classical vs Quantum**: Direct benchmarking of QAOA against Top-K and Exact QUBO, showing objective values, optimality gaps, and candidate set overlap.
6. **Results & Reports**: Exportable CSV of screened candidates, interactive model evaluation curves (ROC, Confusion Matrix), and downloadable full JSON report.

---

## 13. Measured Empirical Results

All metrics reported below were obtained from **actual execution** on this repository:

### 13.1 Biological Activity Classifier (Random Forest)
- **Dataset**: MoleculeNet BACE (1,513 valid molecules)
- **Train / Test Split**: 80% Train (1,210 samples), 20% Test (303 samples)
- **Test Accuracy**: **78.55%** (238 / 303 correct)
- **Test ROC-AUC**: **0.8794**
- **Test F1-Score**: **0.7670**
- **Precision**: **0.7589**
- **Recall**: **0.7754**
- **Confusion Matrix**:
  ```
  [[131 (TN),  34 (FP)],
   [ 31 (FN), 107 (TP)]]
  ```

### 13.2 Quantum Screening Benchmark ($N = 8, K = 3, p = 1, \text{Shots} = 1024$)
- **Candidate Pool**: 8 test set molecules with composite scores $s \in [0.217, 0.923]$
- **Optimization Results**:
  | Method | QUBO Energy $E(x)$ | Score Sum $\sum s_i x_i$ | Cardinality Feasible | Optimality Gap $\Delta E$ | Overlap with Exact | Runtime |
  | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
  | **QAOA (Aer Sim)** | **-1.7179** | **1.7179** | **Yes** ($\sum x_i = 3$) | **0.0000** | **100.0%** | **0.5585s** |
  | **Top-K Greedy** | **-1.7179** | **1.7179** | **Yes** ($\sum x_i = 3$) | **0.0000** | **100.0%** | **0.0015s** |
  | **Exact Classical QUBO** | **-1.7179** | **1.7179** | **Yes** ($\sum x_i = 3$) | **0.0000** | **100.0%** | **0.0052s** |
- **QAOA Feasible Sampling Rate**: **45.7%** (468 of 1024 shots satisfied the exact cardinality constraint without repair).
- **Selected Candidates**: `['MOL_BACE_1111', 'MOL_BACE_558', 'MOL_BACE_1121']` (Bitstring `10100010`).

---

## 14. Scientific Limitations & Ethical Disclaimers

> [!WARNING]
> **CRITICAL SCIENTIFIC DISCLAIMER**
> 1. **Not Proof of Drug Efficacy**: Quantum optimization solves a mathematical subset selection problem under formulated utility weights. It does NOT prove drug safety, target binding specificity, pharmacokinetics, or clinical efficacy.
> 2. **Target Specificity**: The activity prediction model is trained specifically on human BACE-1 in vitro assays and does NOT generalize to other enzymes, receptors, or diseases without retraining.
> 3. **No Quantum Speedup Claim**: On existing Noisy Intermediate-Scale Quantum (NISQ) devices and simulators, QAOA does not outperform classical polynomial-time heuristics for simple cardinality constraints. Theoretical quantum advantages require non-convex interaction landscapes and fault-tolerant hardware.
> 4. **Mandatory Wet-Lab Validation**: In silico screening outputs represent prioritized research hypotheses that must undergo rigorous in vitro biochemical assays before any therapeutic conclusions can be drawn.

---

## 15. Repository Structure
```
QC/
├── app.py                      # Multi-page interactive Streamlit UI
├── requirements.txt            # Pinned reproducible dependencies
├── conftest.py                 # Pytest root configuration
├── README.md                   # Comprehensive documentation
├── CAPSTONE_REPORT.md          # Full academic capstone project report
├── PRESENTATION_OUTLINE.md     # 10-slide capstone presentation outline
├── config/
│   └── config.yaml             # Central pipeline & algorithm settings
├── data/
│   ├── README.md               # Dataset provenance & schema
│   ├── bace.csv                # Downloaded MoleculeNet BACE data
│   ├── processed_bace.csv      # Validated & cleaned dataset
│   └── sample/
│       └── sample_bace.csv     # 25-molecule balanced sample
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Data downloading, validation, sampling
│   ├── molecular_features.py   # RDKit descriptors, Morgan FPs, 2D SVG
│   ├── preprocessing.py        # Leakage-free scaling & splitting
│   ├── activity_model.py       # Random Forest classifier
│   ├── qubo_formulation.py     # Fixed-budget QUBO & Ising mapping
│   ├── qaoa_optimizer.py       # Parameterized QAOA circuit on Aer
│   ├── classical_baseline.py   # Top-K & Exact QUBO solvers
│   ├── evaluation.py           # Metrics aggregation & CSV export
│   └── visualization.py        # Interactive Plotly figures
├── scripts/
│   ├── prepare_data.py         # Data preparation script
│   ├── train_model.py          # Model training script
│   └── run_screening.py        # Screening benchmark script
├── models/
│   ├── activity_rf_model.joblib
│   └── model_metadata.joblib
├── results/
│   ├── model_evaluation.json   # Real measured ML metrics
│   ├── test_predictions.csv    # Test set predictions
│   ├── screening_results.json  # Real QAOA vs baseline benchmark
│   ├── selected_candidates.csv # Exported candidate table
│   └── evaluation_summary.json # Aggregated JSON summary
└── tests/
    ├── test_data_loader.py
    ├── test_molecular_features.py
    ├── test_qubo.py
    ├── test_qaoa.py
    ├── test_classical_baseline.py
    └── test_pipeline.py
```
