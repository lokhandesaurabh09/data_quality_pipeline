import pandas as pd
import numpy as np

def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    print("Starting data cleaning process....")
    initial_row_count = len(df)

    df = df.rename(columns = lambda x: x.strip())

    object_cols = df.select_dtypes(include = ['object']).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(['nan', 'None', ''], np.nan)

    numeric_cols = df.select_dtypes(include = [np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            print(f" -> Filled missing values in numeric columns '{col}' with median: {median_val}")

    for col in object_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna("Unknown")
            print(f" -> Filled missing values in text column '{col}' with 'Unknown'")

    df = df.drop_duplicates()
    duplicates_removed = initial_row_count - len(df)

    assert len(df) > 0, "Data Quality Error: The dataset is completely empty after cleaning!!"

    print(f"Cleaning complete! Removed! Removed {duplicates_removed} duplicateds.")
    return df

if __name__ == "__main__":

    from ingest import load_raw_data
    raw_df = load_raw_data("data/raw/AB_NYC_2019.csv")
    cleaned_df = clean_data(raw_df)
    print("Cleaned shape: ", cleaned_df.shape)