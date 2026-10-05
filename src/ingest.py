import os
import pandas as pd
from src.logger import setup_logger

logger = setup_logger("ingest")

# Supported formats map — easy to extend later
SUPPORTED_FORMATS = {
    '.csv': 'CSV',
    '.parquet': 'Parquet',
    '.json': 'JSON',
    '.xls': 'Excel',
    '.xlsx': 'Excel'
}

def load_raw_data(file_path: str) -> pd.DataFrame:
    """
    Safely loads raw datasets of various formats (CSV, Parquet, JSON, Excel)
    with file existence checks and structured error propagation.
    Supported: .csv, .parquet, .json, .xls, .xlsx
    """

    # Guard — empty path
    if not file_path:
        logger.error("File path is empty or not provided.")
        raise ValueError("File path cannot be empty.")

    # Guard — file existence
    if not os.path.exists(file_path):
        logger.error(f"File not found at path: '{file_path}'")
        raise FileNotFoundError(f"File not found at path: '{file_path}'")

    # Extract and validate extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported file format: '{ext}'")
        raise ValueError(
            f"Unsupported format '{ext}'. "
            f"Supported: {', '.join(SUPPORTED_FORMATS.keys())}"
        )

    logger.info(f"Loading raw data from '{file_path}' (Format: {SUPPORTED_FORMATS[ext]})...")

    try:
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext == '.parquet':
            df = pd.read_parquet(file_path)
        elif ext == '.json':
            df = pd.read_json(file_path)
        elif ext in ['.xls', '.xlsx']:
            try:
                df = pd.read_excel(file_path)
            except ImportError:
                logger.error("Excel support requires 'openpyxl'. Run: pip install openpyxl")
                raise

    except pd.errors.EmptyDataError:
        logger.error(f"File is empty (no data): '{file_path}'")
        raise

    except Exception as e:
        logger.error(f"Failed to parse '{file_path}': {e}")
        raise

    # Post-load empty check — catches formats that don't raise on empty
    if df.empty:
        logger.warning(f"Loaded dataset from '{file_path}' is empty — no rows found.")
    else:
        logger.info(
            f"Successfully loaded {SUPPORTED_FORMATS[ext]} dataset: "
            f"{len(df)} rows, {len(df.columns)} columns."
        )

    return df


if __name__ == "__main__":
    load_raw_data("data/raw/AB_NYC_2019.csv")