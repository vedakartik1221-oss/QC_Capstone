"""
Evaluation and Metrics Reporting Module
Collates dataset summaries, ML classification performance,
QAOA screening metrics, and exports structured JSON/CSV reports.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def generate_full_evaluation_report(
    data_report: Dict[str, Any],
    model_metrics: Dict[str, Any],
    comparison_results: Optional[Dict[str, Any]] = None,
    output_path: str = "results/evaluation_summary.json"
) -> Dict[str, Any]:
    """
    Assemble complete project evaluation report combining data validation,
    ML performance, and quantum screening benchmarks.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    full_report = {
        "dataset_summary": data_report,
        "machine_learning_metrics": model_metrics,
        "quantum_screening_benchmarks": comparison_results,
        "scientific_disclaimer": (
            "This report documents computational screening results. In silico predictions "
            "and QAOA candidate rankings are prioritized hypotheses for laboratory testing, "
            "not verified proof of pharmacological activity or clinical efficacy."
        )
    }
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)
        
    logger.info(f"Saved full evaluation summary report to {out_file}")
    return full_report


def export_screening_candidates_csv(
    df_candidates: pd.DataFrame,
    selected_indices: list,
    output_path: str = "results/selected_candidates.csv"
) -> pd.DataFrame:
    """
    Export the screened and selected candidate molecules with properties to CSV.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    df_export = df_candidates.copy()
    df_export["QAOA_Selected"] = [1 if i in selected_indices else 0 for i in range(len(df_candidates))]
    
    # Sort with selected candidates on top
    df_export = df_export.sort_values(by=["QAOA_Selected", "composite_score"], ascending=[False, False])
    df_export.to_csv(out_file, index=False)
    logger.info(f"Exported selected candidate dataset to {out_file}")
    return df_export
