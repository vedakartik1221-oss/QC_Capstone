"""
Tests for Data Loader and Validation Module
"""

import pytest
import pandas as pd
from pathlib import Path
from src.data_loader import validate_and_clean_data, create_sample_dataset, load_dataset


def test_validate_and_clean_data_handles_invalid_and_duplicates():
    # Synthetic test DataFrame with deliberate dirty data
    dirty_data = pd.DataFrame({
        "mol": [
            "CC(=O)Oc1ccccc1C(=O)O",       # Valid Aspirin
            "INVALID_SMILES_ABC",           # Invalid
            "CC(=O)Oc1ccccc1C(=O)O",       # Duplicate
            None,                           # Null SMILES
            "CC",                           # Valid Ethane
        ],
        "CID": ["M1", "M2", "M3", "M4", "M5"],
        "Class": [1, 1, 1, 0, 0],
        "pIC50": [6.5, 4.0, 6.5, None, 5.0]
    })
    
    cleaned, report = validate_and_clean_data(dirty_data)
    
    assert report["initial_count"] == 5
    assert report["missing_smiles_or_target"] == 1
    assert report["invalid_smiles_count"] == 1
    assert report["duplicate_smiles_count"] == 1
    assert report["final_valid_count"] == 2
    assert len(cleaned) == 2
    assert "CanonicalSMILES" in cleaned.columns


def test_sample_dataset_creation_and_balance(tmp_path):
    df = pd.DataFrame({
        "mol": ["CC", "CCC", "CCCC", "CO", "CCO", "CCCO"],
        "CID": [f"ID_{i}" for i in range(6)],
        "Class": [1, 1, 1, 0, 0, 0],
        "pIC50": [6.0, 7.0, 8.0, 4.0, 5.0, 4.5]
    })
    out_file = tmp_path / "sample.csv"
    sample_df = create_sample_dataset(df, sample_size=4, output_path=str(out_file), random_state=42)
    
    assert out_file.exists()
    assert len(sample_df) == 4
    # Check balance
    assert (sample_df["Class"] == 1).sum() == 2
    assert (sample_df["Class"] == 0).sum() == 2


def test_load_sample_dataset_from_disk():
    df, report = load_dataset(use_sample=True)
    assert len(df) == 25
    assert report["active_count"] > 0
    assert report["inactive_count"] > 0
