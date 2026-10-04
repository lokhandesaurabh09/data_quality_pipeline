import os
import json
from datetime import datetime
from prefect import flow, task
from prefect.logging import get_run_logger

from src.ingest import load_raw_data
from src.validate import validate_data
from src.clean import clean_data
from src.drift_detector import detect_drift
from src.database import save_to_database

def load_config(config_path: str = "config.json") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found at '{config_path}'")
    with open(config_path, 'r') as f:
        return json.load(f)

# ── Tasks ────────────────────────────────────────────────

@task(name="Ingest Raw Data", retries=3, retry_delay_seconds=5)
def ingest_task(path: str):
    logger = get_run_logger()
    logger.info(f"Ingesting raw data from: {path}")
    return load_raw_data(path)

@task(name="Validate Data", retries=1, retry_delay_seconds=3)
def validate_task(df, rules: dict):
    logger = get_run_logger()
    logger.info("Running data quality validation...")
    return validate_data(df, rules)

@task(name="Clean Data", retries=1, retry_delay_seconds=3)
def clean_task(df, rules: dict):
    logger = get_run_logger()
    logger.info("Running data cleaning...")
    return clean_data(df, rules)

@task(name="Detect Drift", retries=1, retry_delay_seconds=3)
def drift_task(baseline_df, cleaned_df, params: dict):
    logger = get_run_logger()
    logger.info("Running drift detection...")
    return detect_drift(
        baseline_df,
        cleaned_df,
        threshold=params["threshold"],
        z_threshold=params.get("z_threshold", 1.96),
        exclude_cols=params.get("exclude_cols", [])
    )

@task(name="Save to Database", retries=2, retry_delay_seconds=5)
def save_task(df, table_name: str, db_path: str):
    logger = get_run_logger()
    logger.info(f"Saving to database table: {table_name}")
    return save_to_database(df, table_name=table_name, db_path=db_path)

@task(name="Generate Audit Report")
def report_task(pipeline_summary: dict, reports_dir: str, timestamp_str: str):
    logger = get_run_logger()
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, f"pipeline_report_{timestamp_str}.json")
    with open(report_path, 'w') as f:
        json.dump(pipeline_summary, f, indent=4)
    logger.info(f"Audit report saved to: {report_path}")
    return report_path

# ── Flow ─────────────────────────────────────────────────

@flow(name="QDrift Pipeline", log_prints=True)
def run_pipeline(config_path: str = "config.json"):
    logger = get_run_logger()
    logger.info("=" * 50)
    logger.info("Starting QDrift Prefect Pipeline")
    logger.info("=" * 50)

    config = load_config(config_path)
    paths = config["paths"]
    drift_params = config["drift_parameters"]
    validation_rules = config.get("validation_rules", {})
    cleaning_rules = config.get("cleaning_rules", {})

    run_time = datetime.now()
    timestamp_str = run_time.strftime('%Y%m%d_%H%M%S')

    pipeline_summary = {
        "run_timestamp": run_time.isoformat(),
        "status": "UNKNOWN",
        "error": None,
        "metrics": {}
    }

    try:
        # 1. Ingest
        raw_df = ingest_task(paths["raw_data_path"])
        pipeline_summary["metrics"]["raw_rows"] = len(raw_df)
        pipeline_summary["metrics"]["raw_columns"] = len(raw_df.columns)

        # 2. Validate
        validate_task(raw_df, validation_rules)
        pipeline_summary["metrics"]["validation_status"] = "PASSED"

        # 3. Clean
        cleaned_df = clean_task(raw_df, cleaning_rules)
        pipeline_summary["metrics"]["cleaned_rows"] = len(cleaned_df)
        pipeline_summary["metrics"]["duplicates_removed"] = len(raw_df) - len(cleaned_df)

        # 4. Baseline + Drift
        baseline_df = ingest_task(paths["baseline_data_path"])
        drift_report = drift_task(baseline_df, cleaned_df, drift_params)
        pipeline_summary["metrics"]["drift_report"] = drift_report

        # 5. Save
        save_task(
            cleaned_df,
            table_name=paths["table_name"],
            db_path=paths["db_connection_string"]
        )

        pipeline_summary["status"] = "SUCCESS"
        logger.info("QDrift Pipeline completed successfully!")

    except Exception as e:
        pipeline_summary["status"] = "FAILED"
        pipeline_summary["error"] = str(e)
        logger.error(f"Pipeline FAILED: {e}")
        raise

    finally:
        report_task(
            pipeline_summary,
            paths.get("reports_dir", "reports"),
            timestamp_str
        )

if __name__ == "__main__":
    run_pipeline()