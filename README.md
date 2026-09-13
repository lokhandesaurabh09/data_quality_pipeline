# Automated Data Quality & Drift Detection Pipeline

An end-to-end, modular batch data engineering pipeline built in Python to automate raw data ingestion, hygiene cleaning, statistical data drift analysis, SQL database persistence, and structured JSON audit reporting.

---

## What the Project Does
This pipeline automates the ingestion and processing of raw datasets (demonstrated using the Airbnb NYC 2019 dataset) by executing a sequential workflow:
1. **Ingestion:** Loads and validates raw CSV data structures[cite: 6].
2. **Data Cleaning & Hygiene:** Normalizes column names, dynamically strips string whitespaces, handles missing value imputation (median for numerics, `"Unknown"` for text categories), and drops duplicate rows[cite: 5].
3. **Statistical Drift Detection:** Compares the processed dataset against a historical baseline file using mean percentage shift analysis to flag anomalies or data distribution shifts.
4. **Relational Database Persistence:** Commits the clean, structured data into a local relational database using SQLAlchemy.
5. **Observability & Audit Logging:** Generates a machine-readable JSON execution summary report archive detailing row counts, cleaning metrics, and drift alerts.

---

## Project Structure

```text
data_quality_pipeline/
│
├── data/
│   ├── raw/                 # Raw input datasets (e.g., AB_NYC_2019.csv)
│   └── processed/           # Historical baseline reference files (e.g., baseline.csv)
│
├── reports/                 # Generated JSON execution audit reports
│
├── src/                     # Core pipeline modules
│   ├── __init__.py
│   ├── clean.py             # Data hygiene & missing value imputation logic
│   ├── database.py          # SQLAlchemy engine & SQLite persistence logic
│   ├── drift_detector.py    # Statistical mean-shift drift analysis module
│   └── ingest.py            # Safe raw data loader module
│
├── .gitignore               # Git exclusion rules (ignores venv, dbs, raw data, logs)
├── main.py                  # Master pipeline orchestrator script
├── requirements.txt         # Project Python dependencies
└── README.md                # Project documentation

## Tech Stack & DependenciesLanguage: 
1.Python (v3.10+)  
2.Data Manipulation & Analysis: Pandas, NumPy  3.Database & ORM: SQLAlchemy, SQLite  4.Orchestration & Reporting: Custom Python script (main.py), built-in json, os, and datetime modules  

## How to Run It:
1. Clone the Repository & Setup Environment
Open your terminal and run:

git clone [https://github.com/lokhandesaurabh09/data_quality_pipeline.git](https://github.com/lokhandesaurabh09/data_quality_pipeline.git)
cd data_quality_pipeline

python -m venv venv

2. Activate Virtual Environment:
Windows (PowerShell):
.\venv\Scripts\Activate.ps1

Mac/Linux:
source venv/bin/activate

3. Install Dependencies:
pip install -r requirements.txt

4. Execute the Pipeline:
Run the master orchestrator script from your project root:

> python main.py

## Known Limitations of v1

While fully functional as a prototype, v1 contains intentional architectural boundaries planned for improvement in v2:

1. Full-Refresh Database Storage (if_exists='replace'): The database overwrites previous tables on every run rather than appending batches or maintaining historical version control[1].

2. Basic Logging (print() statements): Execution logs rely on terminal prints instead of Python's structured logging module with severity levels and rotating log files.

3. Simple Drift Metrics: Drift detection uses mean percentage change rather than advanced statistical distributions like Population Stability Index (PSI) or Kolmogorov-Smirnov (KS) tests. 

4. Surrogate Key Drift False-Positives: Unique identifier columns (like id and host_id) are currently evaluated by the numerical drift detector, triggering false-positive alerts[4].

5. Synchronous Execution / Manual Orchestration: Coordinated via a linear Python script (main.py) rather than a fault-tolerant enterprise scheduler like Apache Airflow or Prefect[2].