import os
import json
from datetime import datetime

from src.logger import setup_logger
from src.ingest import load_raw_data
from src.clean import clean_data
from src.drift_detector import detect_drift
from src.database import save_to_database

logger = setup_logger("main_orchestrator")

def run_pipeline():
    logger.info("=" * 50)
    logger.info("Starting Automated Data Pipeline Run")
    logger.info("=" * 50)

    raw_path = "data/raw/AB_NYC_2019.csv"
    baseline_path = "data/processed/baseline.csv"

    run_time = datetime.now()
    timestamp_str = run_time.strftime('%Y%m%d_%H%M%S')


    pipeline_summary = {
        "run_timestamp": run_time.isoformat(),
        "status": "UNKNOWN",
        "error": None,
        "metrics": {}
    }

    try:
        raw_df = load_raw_data(raw_path)
        pipeline_summary["metrics"]["raw_rows"] = len(raw_df)
        pipeline_summary["metrics"]["raw_columns"] = len(raw_df.columns)

        cleaned_df = clean_data(raw_df)
        pipeline_summary["metrics"]["cleaned_rows"] = len(cleaned_df)
        pipeline_summary["metrics"]["duplicates_removed"] = (len(raw_df) - len(cleaned_df))

        baseline_df = load_raw_data(baseline_path)
        drift_report = detect_drift(baseline_df, cleaned_df)
        pipeline_summary["metrics"]["drift_report"] = drift_report

        save_to_database(cleaned_df)

        pipeline_summary["status"] = "SUCCESS"
        logger.info("Pipeline execution finished successfully!")

    except FileNotFoundError as e:
        pipeline_summary["status"] = "FAILED"
        pipeline_summary["error"] = str(e)
        logger.error(f"\n[CRITICAL ERROR] File not found: {e}")

    except Exception as e:
        pipeline_summary["status"] = "FAILED"
        pipeline_summary["error"] = str(e)
        logger.error(f"\n[CRITICAL ERROR] Pipeline failed unexpectedly: {e}")

    finally:
        os.makedirs("reports", exist_ok=True)
        report_filename = f"reports/pipeline_report_{timestamp_str}.json"
        with open(report_filename, 'w') as f:
            json.dump(pipeline_summary, f, indent = 4)
        logger.info(f"Summary audit report saved to: {report_filename}")
        logger.info("=" * 50)

if __name__ == "__main__":
    run_pipeline()