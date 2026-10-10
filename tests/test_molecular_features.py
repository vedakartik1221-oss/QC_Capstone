"""
Tests for Molecular Feature Extraction Module
"""

import pytest
import numpy as np
from src.molecular_features import (
    validate_smiles,
    calculate_descriptors,
    generate_morgan_fingerprint,
    get_molecule_svg
)


def test_validate_valid_smiles():
    is_valid, canonical = validate_smiles("CC(=O)Oc1ccccc1C(=O)O")
    assert is_valid is True
    assert canonical == "CC(=O)Oc1ccccc1C(=O)O"


def test_validate_invalid_smiles():
    is_valid, canonical = validate_smiles("INVALID_SMILES_STRING_123")
    assert is_valid is False
    assert canonical is None


def test_validate_empty_smiles():
    is_valid, canonical = validate_smiles("")
    assert is_valid is False
    assert canonical is None


def test_calculate_descriptors_aspirin():
    desc = calculate_descriptors("CC(=O)Oc1ccccc1C(=O)O")
    assert desc is not None
    assert desc["MW"] > 170.0 and desc["MW"] < 190.0
    assert desc["HBD"] == 1
    assert desc["HBA"] == 3
    assert desc["RotB"] == 2
    assert desc["LipinskiViolations"] == 0
    assert desc["LipinskiPassRate"] == 1.0


def test_calculate_descriptors_invalid():
    desc = calculate_descriptors("NOT_A_MOLECULE")
    assert desc is None


def test_generate_morgan_fingerprint():
    fp = generate_morgan_fingerprint("CC(=O)Oc1ccccc1C(=O)O", radius=2, n_bits=512)
    assert fp is not None
    assert isinstance(fp, np.ndarray)
    assert fp.shape == (512,)
    assert fp.sum() > 0
    assert np.all(np.isin(fp, [0, 1]))


def test_generate_morgan_fingerprint_invalid():
    fp = generate_morgan_fingerprint("INVALID")
    assert fp is None


def test_get_molecule_svg():
    svg = get_molecule_svg("CC(=O)Oc1ccccc1C(=O)O")
    assert svg is not None
    assert "<svg" in svg
    assert "</svg>" in svg


def test_get_molecule_svg_invalid():
    svg = get_molecule_svg("NOT_A_SMILES")
    assert svg is None
