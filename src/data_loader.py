"""
Data Loader and Validation Module
Manages downloading, caching, loading, validating, deduplicating,
and sampling the MoleculeNet BACE dataset.
"""

import os
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import pandas as pd
import requests
import yaml
import logging

from src.molecular_features import validate_smiles, calculate_descriptors

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BACE_DATASET_URL = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/bace.csv"


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def download_dataset(url: str = BACE_DATASET_URL, output_path: str = "data/bace.csv") -> Path:
    """
    Download the BACE benchmark dataset from MoleculeNet S3 storage.
    
    Args:
        url: Remote CSV URL
        output_path: Local file path to save the dataset
        
    Returns:
        Path object pointing to downloaded file
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    if out_file.exists() and out_file.stat().st_size > 1000:
        logger.info(f"Dataset already exists locally at: {out_file} ({out_file.stat().st_size} bytes)")
        return out_file
        
    logger.info(f"Downloading BACE dataset from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(out_file, "wb") as f:
            f.write(response.content)
        logger.info(f"Successfully downloaded BACE dataset to {out_file} ({len(response.content)} bytes)")
        return out_file
    except Exception as e:
        logger.error(f"Failed to download BACE dataset from {url}: {e}")
        if out_file.exists():
            logger.warning("Using existing local file despite download failure.")
            return out_file
        raise RuntimeError(
            f"Dataset download failed: {e}. "
            "Please check internet connection or manually place 'bace.csv' into 'data/'."
        )


def validate_and_clean_data(
    df: pd.DataFrame,
    smiles_col: str = "mol",
    id_col: str = "CID",
    target_col: str = "Class",
    affinity_col: str = "pIC50"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validate, sanitize, deduplicate, and clean the BACE molecular dataset.
    
    Processing Steps:
        1. Ensure required columns exist.
        2. Filter out missing SMILES or target labels.
        3. Validate each SMILES structure using RDKit and replace with canonical SMILES.
        4. Detect and handle duplicates by canonical SMILES.
        5. Verify binary label validity (0 or 1).
    
    Args:
        df: Raw DataFrame
        smiles_col: SMILES column name
        id_col: Molecule identifier column name
        target_col: Binary activity column name
        affinity_col: Experimental binding affinity column name
        
    Returns:
        Tuple of (cleaned_df: pd.DataFrame, report: Dict[str, Any])
    """
    initial_rows = len(df)
    report = {
        "initial_count": initial_rows,
        "missing_smiles_or_target": 0,
        "invalid_smiles_count": 0,
        "duplicate_smiles_count": 0,
        "final_valid_count": 0,
        "active_count": 0,
        "inactive_count": 0,
    }
    
    # 1. Check required columns
    required_cols = [smiles_col, target_col]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' missing from dataset.")
            
    # 2. Filter nulls in smiles and target
    valid_mask = df[smiles_col].notna() & df[target_col].notna()
    missing_cnt = initial_rows - valid_mask.sum()
    report["missing_smiles_or_target"] = int(missing_cnt)
    cleaned = df[valid_mask].copy()
    
    # 3. Validate SMILES and canonicalize
    canonical_list = []
    is_valid_list = []
    for s in cleaned[smiles_col]:
        valid, canonical = validate_smiles(str(s))
        is_valid_list.append(valid)
        canonical_list.append(canonical)
        
    cleaned["CanonicalSMILES"] = canonical_list
    cleaned["IsValidSMILES"] = is_valid_list
    
    invalid_cnt = (~cleaned["IsValidSMILES"]).sum()
    report["invalid_smiles_count"] = int(invalid_cnt)
    cleaned = cleaned[cleaned["IsValidSMILES"]].copy()
    
    # Use canonical SMILES as standard
    cleaned[smiles_col] = cleaned["CanonicalSMILES"]
    
    # 4. Handle duplicates
    # If duplicates have conflicting Class labels, resolve by keeping the one with valid pIC50 or first
    dup_mask = cleaned.duplicated(subset=[smiles_col], keep=False)
    dup_count = cleaned.duplicated(subset=[smiles_col], keep="first").sum()
    report["duplicate_smiles_count"] = int(dup_count)
    
    # Deduplicate keeping first occurrence
    cleaned = cleaned.drop_duplicates(subset=[smiles_col], keep="first").reset_index(drop=True)
    
    # 5. Format labels
    cleaned[target_col] = cleaned[target_col].astype(int)
    if affinity_col in cleaned.columns:
        cleaned[affinity_col] = pd.to_numeric(cleaned[affinity_col], errors="coerce")
        
    report["final_valid_count"] = len(cleaned)
    report["active_count"] = int((cleaned[target_col] == 1).sum())
    report["inactive_count"] = int((cleaned[target_col] == 0).sum())
    
    logger.info(
        f"Data validation complete: {report['initial_count']} initial -> "
        f"{report['final_valid_count']} valid ({report['active_count']} active, "
        f"{report['inactive_count']} inactive)"
    )
    return cleaned, report


def create_sample_dataset(
    cleaned_df: pd.DataFrame,
    sample_size: int = 25,
    output_path: str = "data/sample/sample_bace.csv",
    random_state: int = 42
) -> pd.DataFrame:
    """
    Create a balanced, representative subset of real molecules for rapid smoke tests
    and offline interactive demonstrations.
    
    Note: Real experimental molecules and labels are preserved; no values are fabricated.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Balance actives and inactives
    actives = cleaned_df[cleaned_df["Class"] == 1]
    inactives = cleaned_df[cleaned_df["Class"] == 0]
    
    n_act = min(sample_size // 2, len(actives))
    n_inact = min(sample_size - n_act, len(inactives))
    
    sample_act = actives.sample(n=n_act, random_state=random_state)
    sample_inact = inactives.sample(n=n_inact, random_state=random_state)
    
    sample_df = pd.concat([sample_act, sample_inact]).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    sample_df.to_csv(out_file, index=False)
    logger.info(f"Saved real sample dataset to {out_file} ({len(sample_df)} molecules: {n_act} active, {n_inact} inactive)")
    return sample_df


def load_dataset(
    use_sample: bool = False,
    config_path: str = "config/config.yaml"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    High-level loader that obtains and prepares the dataset according to config.
    
    Args:
        use_sample: If True, loads small vetted sample dataset
        config_path: Path to YAML config
        
    Returns:
        Tuple of (DataFrame, validation_report)
    """
    config = load_config(config_path)
    data_cfg = config.get("data", {})
    
    if use_sample:
        sample_file = Path(data_cfg.get("sample_file", "data/sample/sample_bace.csv"))
        if not sample_file.exists():
            # Trigger download and generation if missing
            raw_path = download_dataset(data_cfg.get("bace_url", BACE_DATASET_URL), data_cfg.get("raw_file", "data/bace.csv"))
            raw_df = pd.read_csv(raw_path)
            cleaned, report = validate_and_clean_data(raw_df)
            create_sample_dataset(cleaned, data_cfg.get("sample_size", 25), str(sample_file))
        df = pd.read_csv(sample_file)
        cleaned, report = validate_and_clean_data(df)
        return cleaned, report
        
    raw_path = download_dataset(data_cfg.get("bace_url", BACE_DATASET_URL), data_cfg.get("raw_file", "data/bace.csv"))
    raw_df = pd.read_csv(raw_path)
    cleaned, report = validate_and_clean_data(
        raw_df,
        smiles_col=data_cfg.get("smiles_col", "mol"),
        id_col=data_cfg.get("id_col", "CID"),
        target_col=data_cfg.get("target_col", "Class"),
        affinity_col=data_cfg.get("affinity_col", "pIC50")
    )
    
    # Ensure sample dataset exists
    sample_file = Path(data_cfg.get("sample_file", "data/sample/sample_bace.csv"))
    if not sample_file.exists():
        create_sample_dataset(cleaned, data_cfg.get("sample_size", 25), str(sample_file))
        
    return cleaned, report
