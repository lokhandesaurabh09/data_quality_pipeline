# QDrift — Automated Data Quality & Drift Detection Pipeline

A modular, config-driven, production-aware batch data engineering pipeline built in Python to automate raw data ingestion, validation, hygiene cleaning, statistical drift detection, SQL database persistence, structured logging, and JSON audit reporting.

---

## What the Project Does

QDrift automates the ingestion and processing of raw datasets by executing a strict, sequential pipeline flow:

```
Ingest → Validate → Clean → Drift Detection → Save → Audit Report
```

1. **Ingestion** — Safely loads raw CSV datasets with file existence checks and structured error propagation
2. **Validation** — Inspects raw data for structural issues: empty datasets, missing required columns, infinite values, and high null percentages — before any transformation occurs
3. **Cleaning** — Config-driven imputation (median for numerics, configurable fill value for categoricals), whitespace normalization, and duplicate removal
4. **Drift Detection** — Compares the processed dataset against a historical baseline using dual statistical methods: mean percentage shift and two-sample Z-score test, with smart auto-exclusion of high-cardinality identifier columns
5. **Database Persistence** — Appends clean data into SQLite via SQLAlchemy with per-run `batch_id` and `ingestion_timestamp` for full historical versioning
6. **Observability** — Structured logging with severity levels across all modules, plus auto-generated JSON audit reports on every run — including failures

---

## Project Structure

```
data_quality_pipeline/
│
├── data/
│   ├── raw/                        # Raw input datasets
│   └── processed/                  # Historical baseline reference files
│
├── logs/                           # Structured pipeline log files
│
├── reports/                        # Auto-generated JSON execution audit reports
│
├── src/
│   ├── __init__.py
│   ├── ingest.py                   # Safe raw data loader with error propagation
│   ├── validate.py                 # Config-driven data quality validation layer
│   ├── clean.py                    # Imputation, deduplication, normalization
│   ├── drift_detector.py           # Dual-method statistical drift analysis
│   ├── database.py                 # SQLAlchemy append-mode persistence layer
│   └── logger.py                   # Centralized structured logging setup
│
├── tests/
│   ├── test_clean.py               # 8 unit tests for cleaning logic
│   ├── test_ingest.py              # 8 unit tests for ingestion logic
│   ├── test_validate.py            # 10 unit tests for validation logic
│   └── test_drift_detector.py      # 10 unit tests for drift detection logic
│
├── config.json                     # Centralized pipeline configuration
├── main.py                         # Master pipeline orchestrator
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| ORM / Database | SQLAlchemy, SQLite |
| Logging | Python `logging` module |
| Reporting | Built-in `json`, `datetime`, `os` |
| Testing | pytest |
| Orchestration | Custom Python orchestrator (`main.py`) |

---

## Configuration

All pipeline parameters are externalized in `config.json` — no hardcoded values anywhere in the codebase:

```json
{
    "paths": {
        "raw_data_path": "data/raw/your_dataset.csv",
        "baseline_data_path": "data/processed/baseline.csv",
        "db_connection_string": "sqlite:///pipeline_storage.db",
        "table_name": "cleaned_dataset",
        "reports_dir": "reports",
        "logs_dir": "logs"
    },
    "cleaning_rules": {
        "drop_duplicates": true,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    },
    "drift_parameters": {
        "threshold": 0.15,
        "z_threshold": 1.96,
        "exclude_cols": []
    },
    "validation_rules": {
        "required_columns": [],
        "max_null_percentage": 0.30,
        "check_infinite_values": true,
        "fail_on_empty": true
    }
}
```

> **Note:** `exclude_cols` and `required_columns` are intentionally left empty. The pipeline is built for general-purpose use — `exclude_cols` are auto-detected at runtime via smart high-cardinality inspection, and `required_columns` can be populated for dataset-specific schema enforcement.

---

## How to Run

### 1. Clone & Setup Environment

```bash
git clone https://github.com/lokhandesaurabh09/data_quality_pipeline.git
cd data_quality_pipeline
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your Dataset

Drop your CSV into `data/raw/` and create a baseline sample:

```python
import pandas as pd
df = pd.read_csv("data/raw/your_dataset.csv")
df.sample(frac=0.2, random_state=42).to_csv("data/processed/baseline.csv", index=False)
```

### 5. Update `config.json`

```json
"raw_data_path": "data/raw/your_dataset.csv"
```

That's the only change needed for a new dataset.

### 6. Run the Pipeline

```bash
python main.py
```

---

## Sample Output

```
2026-09-27 12:04:45 | INFO    | main_orchestrator | Starting Automated Data Pipeline Run
2026-09-27 12:04:45 | INFO    | ingest            | Successfully loaded dataset with 48895 rows and 16 columns.
2026-09-27 12:04:45 | INFO    | validate          | Data quality validation completed successfully!
2026-09-27 12:04:45 | INFO    | clean             | Duplicate Removal: Removed 0 duplicate rows.
2026-09-27 12:04:45 | INFO    | drift_detector    | Smart Auto-Exclude: Column 'id' identified as high-cardinality (Unique ratio: 100.0%). Skipping drift check.
2026-09-27 12:04:45 | INFO    | drift_detector    | Smart Auto-Exclude: Column 'host_id' identified as high-cardinality (Unique ratio: 86.29%). Skipping drift check.
2026-09-27 12:04:45 | WARNING | drift_detector    | Column 'number_of_reviews' drifted! Shift: 48.61%! | Z-Score: 30.7 (Threshold: 1.96)
2026-09-27 12:04:45 | INFO    | database          | Successfully appended 48895 rows with Batch ID: 20260927_120445.
2026-09-27 12:04:46 | INFO    | main_orchestrator | Pipeline execution finished successfully!
2026-09-27 12:04:46 | INFO    | main_orchestrator | Summary audit report saved to: reports\pipeline_report_20260927_120445.json
```

---

## Drift Detection — How It Works

QDrift uses **two independent statistical methods** per numeric column:

| Method | Formula | Catches |
|---|---|---|
| Percentage Change | `abs(current_mean - baseline_mean) / abs(baseline_mean)` | Large distributional shifts |
| Two-Sample Z-Score | `abs(c_mean - b_mean) / sqrt(b_std²/n_b + c_std²/n_c)` | Statistically significant shifts even when % change is small |

A column is flagged if **either** method exceeds its threshold.

**Smart Auto-Exclusion** automatically removes identifier columns from drift analysis using two rules:
- Uniqueness ratio > 95% — high-cardinality columns like UUIDs
- Column name contains `_id`, `id_`, `_key`, `_uuid` — structural key pattern

This means the detector works correctly on **any dataset without manual configuration**.

---

## Audit Report — Sample Structure

Every pipeline run generates a timestamped JSON report:

```json
{
    "run_timestamp": "2026-09-27T12:04:45.123456",
    "status": "SUCCESS",
    "error": null,
    "metrics": {
        "raw_rows": 48895,
        "raw_columns": 16,
        "cleaned_rows": 48895,
        "duplicates_removed": 0,
        "validation_status": "PASSED",
        "drift_report": {
            "number_of_reviews": {
                "baseline_mean": 45.29,
                "current_mean": 23.27,
                "pct_change_percent": 48.61,
                "z_score": 30.7,
                "drift_detected": true,
                "drift_trigger": "both"
            },
            "summary": {
                "overall_drift_status": true,
                "threshold_used": 0.15,
                "z_threshold_used": 1.96,
                "excluded_columns": ["id", "name", "host_id"],
                "drift_method": "percentage_change + two_sample_z_test"
            }
        }
    }
}
```

> Reports are always generated — even when the pipeline fails — ensuring full auditability.

---

## Running the Test Suite

```bash
pytest tests/ -v
```

**Expected output:**

```
tests/test_clean.py          ........    8 passed
tests/test_drift_detector.py ..........  10 passed
tests/test_ingest.py         ........    8 passed
tests/test_validate.py       ..........  10 passed

36 passed in 0.49s
```

### Test Coverage

| Module | Tests | What's Covered |
|---|---|---|
| `clean.py` | 8 | Deduplication, median/mean imputation, text fill, empty df, no mutation |
| `ingest.py` | 8 | File not found, empty file, column order, null preservation, parametrized shapes |
| `validate.py` | 10 | Empty df, missing columns, null threshold, infinite values, parametrized shapes |
| `drift_detector.py` | 10 | No drift, significant drift, auto-exclusion, threshold sensitivity, summary integrity |

---

## Using With Your Own Dataset

This pipeline is built to be **dataset-agnostic**. To use it with any CSV dataset:

1. Drop your file into `data/raw/`
2. Generate a baseline: `df.sample(frac=0.2).to_csv("data/processed/baseline.csv", index=False)`
3. Update `raw_data_path` in `config.json`
4. Run `python main.py`

The pipeline will automatically:
- Detect and exclude identifier columns from drift analysis
- Impute nulls using your configured strategy
- Version every run with a unique `batch_id`
- Generate a full audit report

---

## V2 Improvements Over V1

| Feature | V1 | V2 |
|---|---|---|
| Database mode | `if_exists='replace'` — wipes data | Append mode with `batch_id` versioning |
| Logging | `print()` statements | Structured `logging` with severity levels |
| Drift detection | Mean % change only | Dual method: % change + Z-score |
| Identifier handling | False alarms on `id`, `host_id` | Smart auto-exclusion |
| Configuration | Hardcoded paths and values | Fully config-driven via `config.json` |
| Error handling | Crashes silently | `try/except/finally` — always writes report |
| Validation | None | Dedicated `validate.py` layer |
| Pipeline order | Ingest → Clean → Drift → Save | Ingest → **Validate** → Clean → Drift → Save |
| Test suite | None | 36 unit tests — all passing |

---

## Roadmap — V3

- [ ] Prefect orchestration — scheduling, retries, visual dashboard
- [ ] Multi-format ingestion — JSON, Parquet, Excel alongside CSV
- [ ] PSI (Population Stability Index) as third drift method
- [ ] Categorical column drift detection
- [ ] Slack / webhook alerting on drift or failure
- [ ] CLI interface via `argparse`
- [ ] Config auto-generator for new datasets

---

## Known Limitations

- **CSV only** — current ingestion supports CSV format only (Parquet, JSON, Excel planned for V3)
- **Local SQLite** — suitable for development; production deployments would use PostgreSQL or a cloud warehouse
- **No scheduling** — pipeline is triggered manually; automated scheduling via Prefect is on the V3 roadmap
- **Batch only** — designed for batch processing, not real-time streaming pipelines

---
