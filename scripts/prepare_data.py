"""
Script: prepare_data.py
Downloads, validates, cleans, and prepares the MoleculeNet BACE dataset.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import download_dataset, validate_and_clean_data, create_sample_dataset, load_config
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    config = load_config()
    data_cfg = config["data"]
    
    logger.info("=== Stage 3: Dataset Preparation and Validation ===")
    
    # 1. Download
    raw_path = download_dataset(data_cfg["bace_url"], data_cfg["raw_file"])
    raw_df = pd.read_csv(raw_path)
    logger.info(f"Loaded raw dataset with {len(raw_df)} rows and {len(raw_df.columns)} columns.")
    
    # 2. Validate and Clean
    cleaned_df, report = validate_and_clean_data(
        raw_df,
        smiles_col=data_cfg["smiles_col"],
        id_col=data_cfg["id_col"],
        target_col=data_cfg["target_col"],
        affinity_col=data_cfg["affinity_col"]
    )
    
    # 3. Save Processed
    processed_path = Path(data_cfg["processed_file"])
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(processed_path, index=False)
    logger.info(f"Saved processed dataset to {processed_path}")
    
    # 4. Generate Sample Dataset
    sample_path = Path(data_cfg["sample_file"])
    sample_df = create_sample_dataset(cleaned_df, sample_size=data_cfg.get("sample_size", 25), output_path=str(sample_path))
    logger.info(f"Sample dataset verified at {sample_path} with {len(sample_df)} records.")
    
    print("\n--- Data Validation Report ---")
    for k, v in report.items():
        print(f"  {k}: {v}")
    print("------------------------------\n")


if __name__ == "__main__":
    main()
