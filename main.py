import os
import json
from datetime import datetime
from src.ingest import load_raw_data
from src.clean import clean_data
from src.drift_detector import detect_drift
from src.database import save_to_database

def run_pipeline():
    print("==================================================")
    print("Starting Automated Data Pipeline Run")
    print("==================================================")

    start_time = datetime.now().isoformat()

    raw_path = "data/raw/AB_NYC_2019.csv"
    baseline_path = "data/processed/baseline.csv"

    raw_df = load_raw_data(raw_path)
    initial_rows = len(raw_df)

    cleaned_df = clean_data(raw_df)
    final_rows = len(cleaned_df)
    duplicates_dropped = initial_rows - final_rows

    baseline_df = load_raw_data(baseline_path)
    drift_report = detect_drift(baseline_df, cleaned_df, threshold=0.15)

    save_to_database(cleaned_df)

    os.makedirs("reports", exist_ok=True)
    report_filename = f"reports/pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    pipeline_summary = {
        "execution_timestamp": start_time,
        "input_file":raw_path,
        "initial_raw_count": initial_rows,
        "final_row_count": final_rows,
        "duplicates_removed": duplicates_dropped,
        "drift_analysis": drift_report,
        "status": "SUCCESS"
    }

    with open(report_filename, "w") as f:
        json.dump(pipeline_summary, f, indent = 4)

    print(f"Summary report successfully generated and saved to: {report_filename}")
    print("==================================================")
    print("Pipeline completed successfully")
    print("==================================================")

if __name__ == "__main__":
    run_pipeline()