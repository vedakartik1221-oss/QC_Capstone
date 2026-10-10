# Dataset Documentation: MoleculeNet BACE Benchmark

## 1. Dataset Overview
The **BACE dataset** is a widely recognized benchmark dataset from the **MoleculeNet** suite (Subramanian et al., Stanford University / DeepChem). It provides quantitative binding affinity data ($\text{pIC}_{50}$) and qualitative binary classification labels (`Class`) for human $\beta$-secretase 1 (**BACE-1**) inhibitors. 

BACE-1 is an aspartic protease involved in the cleavage of amyloid precursor protein (APP) into amyloid-beta peptides, a primary hallmark of **Alzheimer's Disease** pathogenesis. Finding potent, drug-like, brain-penetrant BACE-1 inhibitors is a major pharmaceutical research objective.

## 2. Source and License
- **Origin**: MoleculeNet / DeepChem repository, originally compiled by Subramanian et al., *MoleculeNet: A Benchmark for Molecular Machine Learning*, Chem. Sci., 2018, 9, 513-530.
- **Direct Download URL**: `https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/bace.csv`
- **License**: MIT / Creative Commons (Public scientific benchmark dataset).

## 3. Schema and Column Definitions
- `mol`: Canonical/Standardized SMILES string representing the molecular 2D chemical structure.
- `CID`: Compound Identifier (PubChem / ChEMBL / Paper identifier).
- `Class`: Binary biological activity label:
  - `1`: **Active** inhibitor ($\text{IC}_{50} \le 1\,\mu\text{M}$ or $\text{pIC}_{50} \ge 6.0$).
  - `0`: **Inactive** / weakly active compound ($\text{IC}_{50} > 1\,\mu\text{M}$).
- `Model`: Benchmark partition flag (`Train`, `Valid`, `Test`), corresponding to experimental scaffold/temporal splitting.
- `pIC50`: $-\log_{10}(\text{IC}_{50}\text{ in Molar})$, experimental quantitative binding affinity. Higher values indicate higher binding potency.
- Additional calculated physicochemical properties (`MW`, `AlogP`, `HBA`, `HBD`, `RB`, `PSA`, etc.) included in the raw MoleculeNet table.

## 4. Scientific Interpretation and Usage Rules
1. **Experimental Ground Truth vs Predictions**:
   - `Class` and `pIC50` are experimentally observed laboratory measurements.
   - Predictions output by machine learning are probabilistic estimations $\hat{y} \in [0, 1]$, not experimental confirmations.
   - Quantum optimization scores $s_i$ are composite screening utility metrics, not proofs of clinical safety or efficacy.
2. **Quality Control & Preprocessing**:
   - All SMILES are parsed and validated using RDKit (`Chem.MolFromSmiles`).
   - Molecules failing valence or sanitation checks are discarded with warning logs.
   - Duplicates with conflicting labels are analyzed and resolved.
   - A standardized sample dataset (`data/sample/sample_bace.csv`) is preserved for instantaneous smoke tests and offline execution.
