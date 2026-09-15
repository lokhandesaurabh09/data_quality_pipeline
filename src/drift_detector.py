import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("drift_detector")

def detect_drift(baseline_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.15, exclude_cols: list = None) -> dict:
    logger.info("Running data drift detection analysis....")

    if exclude_cols is None:
        exclude_cols = ['id', 'host_id']

    drift_report = {}
    numeric_cols = baseline_df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

    overall_drift_detected = False

    for col in numeric_cols:
        if col in current_df.columns:
            baseline_mean = baseline_df[col].mean()
            current_mean = current_df[col].mean()

            if baseline_mean == 0:
                pct_change = 0.0
            else:
                pct_change = abs(current_mean - baseline_mean) / abs(baseline_mean)

            is_drift = bool(pct_change > threshold)
            if is_drift:
                overall_drift_detected = True

            drift_report[col] = {
                "baseline_mean": round(float(baseline_mean), 2),
                "current_mean": round(float(current_mean), 2),
                "pct_change_percent": round(float(pct_change * 100), 2),
                "drift_detected": is_drift
            }

            if is_drift:
                logger.warning(f"Column '{col}' drifted by {drift_report[col]['pct_change_percent']}%! (Threshold: {threshold * 100}%)")
            else:
                logger.info(f"Column '{col}' is stable.")

    drift_report["summary"] = {
        "overall_drift_status": bool(overall_drift_detected),
        "threshold_used": float(threshold),
        "excluded_columns": exclude_cols
    }
    return drift_report

if __name__ == "__main__":
    from ingest import load_raw_data
    from clean import clean_data

    baseline = load_raw_data("data/processed/baseline.csv")
    raw_current = load_raw_data("data/raw/AB_NYC_2019.csv")
    current = clean_data(raw_current)

    report = detect_drift(baseline, current)
    print("\nDrift Detection Complete!")