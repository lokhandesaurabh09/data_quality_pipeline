import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os 
from src.logger import setup_logger

logger = setup_logger("database")

def get_database_engine(db_path: str = "sqlite:///pipeline_storage.db"):
    return create_engine(db_path)

def save_to_database(df: pd.DataFrame, table_name : str = "cleaned_airbnb_data", db_path: str = "sqlite:///pipeline_storage.db"):

    logger.info(f"Saving cleaned data to SQL database (Append Mode + Versioning), table: '{table_name}'....")

    run_time = datetime.now()
    df = df.copy()
    df['ingestion_timestamp'] = run_time
    df['batch_id'] = run_time.strftime('%Y%m%d_%H%M%S')

    engine = get_database_engine(db_path)

    df.to_sql(table_name, con=engine, if_exists='append', index=False)

    logger.info(f"Successfully appended {len(df)} rows into table '{table_name}' with Batch ID: {df['batch_id'].iloc[0]}.")

if __name__ == "__main__":
    test_df = pd.DataFrame({'id': [1,2], 'price':[100, 200]})
    save_to_database(test_df)