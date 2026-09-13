import pandas as pd
import os

def load_raw_data(file_path : str) -> pd.DataFrame:

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: The file at '{file_path}' was not found. Please check your path.")

    try:
        df = pd.read_csv(file_path)
        print(f"Successfully loaded dataset from '{file_path}' with {df.shape[0]} rows and {df.shape[1]} columns.")
        return df
    
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        raise e

if __name__ ==  "__main__":

    test_path = "data/raw/AB_NYC_2019.csv"
    load_raw_data(test_path)
