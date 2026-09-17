import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("drift_detector")

def detect_drift(baseline_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.15, z_threshold: float = 1.96, exclude_cols: list = None) -> dict:
    logger.info("Running data drift detection analysis....")

    if exclude_cols is None:
        exclude_cols = ['id', 'host_id']

    drift_report = {}
    numeric_cols = baseline_df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

    overall_drift_detected = False

    for col in numeric_cols:
        if col in current_df.columns:
            b_series = baseline_df[col].dropna()
            c_series = current_df[col].dropna()

            b_mean, b_std, b_count = b_series.mean(), b_series.std(), len(b_series)
            c_mean, c_std, c_count = c_series.mean(), c_series.std(), len(c_series)

            if b_mean == 0:
                pct_change = 0.0
            else:
                pct_change = abs(c_mean - b_mean) / abs(b_mean)

            denom = np.sqrt(((b_std ** 2) / max(b_count, 1)) + ((c_std ** 2) / max(c_count, 1)))
            if denom == 0:
                z_score = 0.0
            else:
                z_score = abs(c_mean - b_mean) / denom

            is_pct_drift = pct_change > threshold
            is_z_drift = z_score > z_threshold
            is_drift = bool(is_pct_drift or is_z_drift)

            if is_drift:
                overall_drift_detected = True

            drift_report[col] = {
                "baseline_mean": round(float(b_mean), 2),
                "current_mean": round(float(c_mean), 2),
                "pct_change_percent": round(float(pct_change * 100), 2),
                "z_score": round(float(z_score), 2),
                "drift_detected": is_drift,
                "drift_trigger":(
                    "both" if is_pct_drift and is_z_drift else
                    "pct_change" if is_pct_drift else
                    "z_score" if is_z_drift else
                    "none"
                )
            }

            if is_drift:
                logger.warning(
                    f"Column '{col}' drifted! " 
                    f"Shift: {drift_report[col]['pct_change_percent']}%! (Threshold: {threshold * 100}%) | "
                    f"Z-Score: {drift_report[col]['z_score']} (Threshold: {z_threshold})"
                    )
            else:
                logger.info(f"Column '{col}' is stable.")

    drift_report["summary"] = {
        "overall_drift_status": bool(overall_drift_detected),
        "threshold_used": float(threshold),
        "z_threshold_used": float(z_threshold),
        "excluded_columns": exclude_cols,
        "drift_method": "percentage_change + two_sample_z_test"
    }
    return drift_report

if __name__ == "__main__":
    from src.ingest import load_raw_data
    from src.clean import clean_data

    baseline = load_raw_data("data/processed/baseline.csv")
    raw_current = load_raw_data("data/raw/AB_NYC_2019.csv")
    current = clean_data(raw_current)

    report = detect_drift(baseline, current)
    print("\nDrift Detection Complete!")