import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("validate")

def validate_data(df: pd.DataFrame, rules: dict) -> bool:

    logger.info("Starting data quality validation checks....")
    is_valid = True

    if df.empty:
        logger.error("Validation Failed: The dataset is completely empty.")
        if rules.get("fail_on_empty", True):
            raise ValueError("Dataset is empty.")
        return False

    logger.info(f"Dataset Shape Check Passed: {len(df)} rows, {len(df.columns)} columns.")

    required_cols = rules.get("required_columns", [])
    if required_cols:
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Validation Failed: Missing required columns: {missing_cols}")
            is_valid = False
        else:
            logger.info("Schema Check Passed: All required columns present.")

    if rules.get("check_infinite_values", True):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            inf_counts = np.isinf(df[numeric_cols]).sum()
            inf_cols = inf_counts[inf_counts > 0]
            if not inf_cols.empty:
                logger.warning(f"Validation Warning: Found infinite values in columns: {inf_cols.to_dict()}")

    max_null_pct = rules.get("max_null_percentage", 0.30)
    total_rows = len(df)
    if total_rows > 0:
        null_ratios = df.isnull().mean()
        high_null_cols = null_ratios[null_ratios > max_null_pct]
        if not high_null_cols.empty:
            for col, pct in high_null_cols.items():
                logger.warning(f"Validation Warning: Column '{col}' has {round(pct * 100 , 2)}% null values (Threshold: {max_null_pct * 100}%).")

    if is_valid:
        logger.info("Data quality validation completed successfully!")
    else:
        raise ValueError("Data quality validation failed due to critical schema or structural errors.")

    return is_valid