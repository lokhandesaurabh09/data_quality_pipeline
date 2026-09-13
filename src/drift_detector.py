import pandas as pd
import numpy as np

def detect_drift(baseline_df: pd.DataFrame, current_df: pd.DataFrame, threshold: float = 0.15) -> dict:
    print("Running data drift detection analysis....")
    drift_report = {}

    numeric_cols = baseline_df.select_dtypes(include=[np.number]).columns

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
                print(f" -> [DRIFT ALERT] Column '{col}' shifted by {drift_report[col]['pct_change_percent']}%!")
            else:
                print(f" -> Column '{col}' is stable.")

    drift_report["summary"] = {
        "overall_drift_status": overall_drift_detected,
        "threshold_used": threshold
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