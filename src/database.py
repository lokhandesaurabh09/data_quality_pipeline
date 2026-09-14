import pandas as pd
from sqlalchemy import create_engine

def save_to_database(df: pd.DataFrame, db_name: str = "pipeline_storage.db", table_name : str = "cleaned_airbnb_data"):

    print(f"Saving cleaned data to SQL database ('{db_name}'), table: '{table_name}'....")

    engine = create_engine(f"sqlite:///{db_name}")

    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

    print(f"Successfully loaded {len(df)} rows into the SQL database table '{table_name}'.")

if __name__ == "__main__":
    from ingest import load_raw_data
    from clean import clean_data

    raw_df = load_raw_data("data/raw/AB_NYC_2019.csv")
    cleaned_df = clean_data(raw_df)
    save_to_database(cleaned_df)