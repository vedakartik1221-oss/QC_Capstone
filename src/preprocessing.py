"""
Data Preprocessing and Molecular Featurization Pipeline
Handles feature generation (Morgan fingerprints + descriptors),
train/val/test splitting, and leakage-free feature scaling.
"""

from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging

from src.molecular_features import calculate_descriptors, generate_morgan_fingerprint

logger = logging.getLogger(__name__)

NUMERICAL_DESCRIPTORS = ["MW", "LogP", "HBD", "HBA", "RotB", "TPSA", "LipinskiPassRate"]


def extract_features_from_dataframe(
    df: pd.DataFrame,
    smiles_col: str = "mol",
    morgan_radius: int = 2,
    morgan_n_bits: int = 512
) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
    """
    Extract Morgan fingerprints and physicochemical descriptors from a DataFrame.
    
    Args:
        df: DataFrame containing molecular structures
        smiles_col: Column with SMILES strings
        morgan_radius: Radius for Morgan fingerprint (ECFP4)
        morgan_n_bits: Length of Morgan fingerprint bit vector
        
    Returns:
        Tuple of (feature_matrix: np.ndarray, feature_names: List[str], enriched_df: pd.DataFrame)
    """
    fp_list = []
    desc_list = []
    valid_indices = []
    
    for idx, smiles in enumerate(df[smiles_col]):
        fp = generate_morgan_fingerprint(str(smiles), radius=morgan_radius, n_bits=morgan_n_bits)
        desc = calculate_descriptors(str(smiles))
        
        if fp is not None and desc is not None:
            fp_list.append(fp)
            desc_values = [desc.get(k, 0.0) for k in NUMERICAL_DESCRIPTORS]
            desc_list.append(desc_values)
            valid_indices.append(idx)
        else:
            logger.warning(f"Could not extract features for row {idx}: {smiles}")
            
    fp_array = np.array(fp_list, dtype=np.float32)
    desc_array = np.array(desc_list, dtype=np.float32)
    
    combined_features = np.hstack([fp_array, desc_array])
    
    feature_names = [f"FP_Bit_{i}" for i in range(morgan_n_bits)] + NUMERICAL_DESCRIPTORS
    
    # Enrich dataframe with calculated descriptors
    desc_df = pd.DataFrame(desc_list, columns=NUMERICAL_DESCRIPTORS, index=df.index[valid_indices])
    enriched_df = df.iloc[valid_indices].copy()
    for col in NUMERICAL_DESCRIPTORS:
        enriched_df[f"calc_{col}"] = desc_df[col]
        
    return combined_features, feature_names, enriched_df


def prepare_datasets(
    df: pd.DataFrame,
    smiles_col: str = "mol",
    target_col: str = "Class",
    split_col: Optional[str] = "Model",
    split_strategy: str = "stratified",
    test_size: float = 0.2,
    random_state: int = 42,
    morgan_radius: int = 2,
    morgan_n_bits: int = 512
) -> Dict[str, Any]:
    """
    Perform feature extraction and data splitting without data leakage.
    Scales numerical descriptors using StandardScaler fitted strictly on training data.
    
    Returns dictionary with X_train, y_train, X_test, y_test, scaler, feature_names, etc.
    """
    X_raw, feature_names, enriched_df = extract_features_from_dataframe(
        df, smiles_col=smiles_col, morgan_radius=morgan_radius, morgan_n_bits=morgan_n_bits
    )
    y_raw = enriched_df[target_col].to_numpy(dtype=np.int64)
    
    # Check split strategy
    if split_strategy == "benchmark" and split_col and split_col in enriched_df.columns:
        train_mask = enriched_df[split_col].str.lower() == "train"
        test_mask = enriched_df[split_col].str.lower().isin(["test", "valid"])
        
        if train_mask.sum() > 0 and test_mask.sum() > 0:
            train_idx = np.where(train_mask)[0]
            test_idx = np.where(test_mask)[0]
        else:
            train_idx, test_idx = train_test_split(
                np.arange(len(enriched_df)), test_size=test_size, stratify=y_raw, random_state=random_state
            )
    else:
        train_idx, test_idx = train_test_split(
            np.arange(len(enriched_df)), test_size=test_size, stratify=y_raw, random_state=random_state
        )
        
    X_train_raw = X_raw[train_idx]
    y_train = y_raw[train_idx]
    X_test_raw = X_raw[test_idx]
    y_test = y_raw[test_idx]
    
    # Separate fingerprints from continuous descriptors
    n_fp = morgan_n_bits
    train_fps = X_train_raw[:, :n_fp]
    train_desc = X_train_raw[:, n_fp:]
    
    test_fps = X_test_raw[:, :n_fp]
    test_desc = X_test_raw[:, n_fp:]
    
    # Fit scaler strictly on training descriptors
    scaler = StandardScaler()
    train_desc_scaled = scaler.fit_transform(train_desc)
    test_desc_scaled = scaler.transform(test_desc)
    
    X_train = np.hstack([train_fps, train_desc_scaled])
    X_test = np.hstack([test_fps, test_desc_scaled])
    
    df_train = enriched_df.iloc[train_idx].reset_index(drop=True)
    df_test = enriched_df.iloc[test_idx].reset_index(drop=True)
    
    return {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "df_train": df_train,
        "df_test": df_test,
        "scaler": scaler,
        "feature_names": feature_names,
        "morgan_n_bits": morgan_n_bits,
        "morgan_radius": morgan_radius,
        "descriptor_names": NUMERICAL_DESCRIPTORS
    }


def featurize_single_smiles(
    smiles: str,
    scaler: StandardScaler,
    morgan_radius: int = 2,
    morgan_n_bits: int = 512
) -> Optional[Tuple[np.ndarray, Dict[str, Any]]]:
    """
    Featurize a single SMILES string using a fitted scaler for live model inference.
    
    Returns:
        Tuple of (feature_vector: np.ndarray [1, n_features], descriptor_dict: Dict) or None
    """
    fp = generate_morgan_fingerprint(smiles, radius=morgan_radius, n_bits=morgan_n_bits)
    desc = calculate_descriptors(smiles)
    if fp is None or desc is None:
        return None
        
    desc_vals = np.array([[desc.get(k, 0.0) for k in NUMERICAL_DESCRIPTORS]], dtype=np.float32)
    desc_scaled = scaler.transform(desc_vals)
    fp_2d = fp.reshape(1, -1).astype(np.float32)
    
    feature_vector = np.hstack([fp_2d, desc_scaled])
    return feature_vector, desc
