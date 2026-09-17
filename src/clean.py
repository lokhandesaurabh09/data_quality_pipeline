import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("clean")

def clean_data(df: pd.DataFrame, rules: dict = None) -> pd.DataFrame:

    logger.info("Starting data cleaning process....")
    df = df.copy()
    initial_row_count = len(df)

    if rules is None:
        rules = {
            "drop_duplicates": True,
            "numeric_imputation_strategy": "median",
            "categorical_fill_value": "Unknown"
        }

    if rules.get("drop_duplicates", True):
        df = df.drop_duplicates()
        duplicates_removed = initial_row_count - len(df)
        logger.info(f"Duplicate Removal: Removed {duplicates_removed} duplicate rows.")

    numeric_cols = df.select_dtypes(include=[np.number]).columns
    strategy = rules.get("numeric_imputation_strategy", "median")

    for col in numeric_cols:
        if df[col].isnull().any():
            if strategy == "mean":
                fill_val = df[col].mean()
            else:
                fill_val = df[col].median()

            df[col] = df[col].fillna(fill_val)
            logger.info(f"Imputed missing values in numeric column '{col}' using {strategy}: {round(fill_val, 4)}")

    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns
    fill_text = rules.get("categorical_fill_value", "Unknown")

    for col in categorical_cols:
        if df[col].isnull().any():
            df[col] = df[col].fillna(fill_text)
            logger.info(f"Filled missing values in text column '{col}' with '{fill_text}'.")

    logger.info(f"Data Cleaning complete! Final dataset shape: {df.shape}")
    return df

