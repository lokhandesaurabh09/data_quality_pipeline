import pandas as pd
import os
from src.logger import setup_logger

logger = setup_logger("ingest")

def load_raw_data(file_path : str) -> pd.DataFrame:

    logger.info(f"Loading raw dataset from '{file_path}'....")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: '{file_path}'")

    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded dataset with {len(df)} rows and {len(df.columns)} columns.")
        return df
    
    except Exception as e:
        logger.error(f"Failed to load dataset from '{file_path}': {e}")
        raise e

if __name__ ==  "__main__":

    test_path = "data/raw/AB_NYC_2019.csv"
    load_raw_data(test_path)
