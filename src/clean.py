import pandas as pd
import numpy as np
from src.logger import setup_logger

logger = setup_logger("clean")

def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Starting data cleaning process....")
    df = df.copy()

    if 'reviews_per_month' in df.columns:
        median_val = df['reviews_per_month'].median()
        df['reviews_per_month'] = df['reviews_per_month'].fillna(median_val)
        logger.info(f"Filled missing values in 'reviews_per_month' with median: {round(median_val, 2)}")

    text_cols = ['name', 'host_name', 'last_review']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
            logger.info(f"Filled missing values in text column '{col}' with 'Unknown'")

    initial_count = len(df)
    df = df.drop_duplicates()
    duplicated_removed = initial_count - len(df)
    logger.info(f"Cleaning complete! Removed {duplicated_removed} duplicate rows")

    return df

if __name__ == "__main__":
    from ingest import load_raw_data
    raw_df = load_raw_data("data/raw/AB_NYC_2019.csv")
    cleaned_df = clean_data(raw_df)
    print("Cleaned shape: ", cleaned_df.shape)