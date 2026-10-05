import os
import json
from datetime import datetime

from src.logger import setup_logger
from src.ingest import load_raw_data
from src.clean import clean_data
from src.validate import validate_data
from src.drift_detector import detect_drift
from src.database import save_to_database
from src.alerts import alert_pipeline_success, alert_drift_detected, alert_pipeline_failure

logger = setup_logger("main_orchestrator")


def load_config(config_path: str = "config.json") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at '{config_path}'")
    with open(config_path, 'r') as f:
        return json.load(f)


def run_pipeline():
    logger.info("=" * 50)
    logger.info("Starting Automated Data Pipeline Run")
    logger.info("=" * 50)

    reports_dir = "reports"
    run_time = datetime.now()
    timestamp_str = run_time.strftime('%Y%m%d_%H%M%S')

    pipeline_summary = {
        "run_timestamp": run_time.isoformat(),
        "status": "UNKNOWN",
        "error": None,
        "metrics": {}
    }

    # Load config outside try — needed in finally block
    try:
        config = load_config()
        paths = config["paths"]
        drift_params = config["drift_parameters"]
        validation_rules = config.get("validation_rules", {})
        cleaning_rules = config.get("cleaning_rules", {})
        alerting = config.get("alerting", {})
        webhook_url = alerting.get("webhook_url", "")
        alerting_enabled = alerting.get("enabled", False) and bool(webhook_url)
        reports_dir = paths.get("reports_dir", "reports")
        logger.info("Successfully loaded pipeline configuration from 'config.json'.")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return

    try:
        # 1. Ingest
        raw_df = load_raw_data(paths["raw_data_path"])
        pipeline_summary["metrics"]["raw_rows"] = len(raw_df)
        pipeline_summary["metrics"]["raw_columns"] = len(raw_df.columns)

        # 2. Validate
        validate_data(raw_df, validation_rules)
        pipeline_summary["metrics"]["validation_status"] = "PASSED"

        # 3. Clean
        cleaned_df = clean_data(raw_df, cleaning_rules)
        pipeline_summary["metrics"]["cleaned_rows"] = len(cleaned_df)
        pipeline_summary["metrics"]["duplicates_removed"] = len(raw_df) - len(cleaned_df)

        # 4. Drift Detection
        baseline_df = load_raw_data(paths["baseline_data_path"])
        drift_report = detect_drift(
            baseline_df,
            cleaned_df,
            threshold=drift_params["threshold"],
            z_threshold=drift_params.get("z_threshold", 1.96),
            exclude_cols=drift_params.get("exclude_cols", [])
        )
        pipeline_summary["metrics"]["drift_report"] = drift_report

        # 5. Alert on drift if detected
        if alerting_enabled and drift_report["summary"]["overall_drift_status"]:
            drifted_cols = [
                col for col, val in drift_report.items()
                if col != "summary" and val.get("drift_detected")
            ]
            alert_drift_detected(webhook_url, drifted_cols, timestamp_str)

        # 6. Save to Database
        save_to_database(
            cleaned_df,
            table_name=paths["table_name"],
            db_path=paths["db_connection_string"]
        )

        pipeline_summary["status"] = "SUCCESS"
        logger.info("Pipeline execution finished successfully!")

        # 7. Alert on success
        if alerting_enabled:
            alert_pipeline_success(webhook_url, timestamp_str, len(cleaned_df))

    except FileNotFoundError as e:
        pipeline_summary["status"] = "FAILED"
        pipeline_summary["error"] = str(e)
        logger.error(f"[CRITICAL ERROR] File not found: {e}")
        if alerting_enabled:
            alert_pipeline_failure(webhook_url, str(e), timestamp_str)

    except Exception as e:
        pipeline_summary["status"] = "FAILED"
        pipeline_summary["error"] = str(e)
        logger.error(f"[CRITICAL ERROR] Pipeline failed unexpectedly: {e}")
        if alerting_enabled:
            alert_pipeline_failure(webhook_url, str(e), timestamp_str)

    finally:
        os.makedirs(reports_dir, exist_ok=True)
        report_filename = os.path.join(reports_dir, f"pipeline_report_{timestamp_str}.json")
        with open(report_filename, 'w') as f:
            json.dump(pipeline_summary, f, indent=4)
        logger.info(f"Summary audit report saved to: {report_filename}")
        logger.info("=" * 50)


if __name__ == "__main__":
    run_pipeline()