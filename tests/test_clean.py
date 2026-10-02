import pandas as pd
import pytest
from src.clean import clean_data

def test_clean_removes_duplicates():
    data = {
        'id': [1, 2, 2, 3],
        'name': ['A', 'B', 'B', 'C'],
        'price': [100, 200, 200, 300]
    }

    df = pd.DataFrame(data)

    rules = {
        "drop_duplicates": True,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }

    cleaned_df = clean_data(df, rules)

    assert len(cleaned_df) == 3
    assert len(cleaned_df[cleaned_df['id'] == 2]) == 1

def test_clean_numeric_imputation():
    data = {
        'id': [1, 2, 3],
        'reviews_per_month': [1.0, None, 3.0]
    }
    df = pd.DataFrame(data)

    rules = {
        "drop_duplicates": False,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }

    cleaned_df = clean_data(df, rules)

    assert cleaned_df['reviews_per_month'].isnull().sum() == 0
    assert cleaned_df.loc[cleaned_df['id'] == 2, 'reviews_per_month'].values[0] == 2.0

def test_clean_text_imputation():
    data = {
        'id': [1, 2],
        'name': ['Listing A', None]
    }
    df = pd.DataFrame(data)

    rules = {
        "drop_duplicates": False,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }

    cleaned_df = clean_data(df, rules)

    assert cleaned_df['name'].isnull().sum() == 0
    assert cleaned_df.loc[cleaned_df['id'] == 2, 'name'].values[0] == 'Unknown'

def test_clean_numeric_imputation_mean():
    data = {
        'id': [1, 2, 3],
        'price': [100.0, None, 300.0]
    }
    df = pd.DataFrame(data)
    rules = {
        "drop_duplicates": False,
        "numeric_imputation_strategy": "mean",
        "categorical_fill_value": "Unknown"
    }
    cleaned_df = clean_data(df, rules)
    assert cleaned_df['price'].isnull().sum() == 0
    assert cleaned_df.loc[cleaned_df['id'] == 2, 'price'].values[0] == 200.0

def test_clean_empty_dataframe():
    df = pd.DataFrame()
    rules = {
        "drop_duplicates": True,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }
    cleaned_df = clean_data(df, rules)
    assert cleaned_df.empty

def test_clean_no_changes_needed():
    data = {
        'id': [1, 2, 3],
        'price': [100.0, 200.0, 300.0],
        'name': ['A', 'B', 'C']
    }
    df = pd.DataFrame(data)
    rules = {
        "drop_duplicates": True,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }
    cleaned_df = clean_data(df, rules)
    assert len(cleaned_df) == 3
    assert cleaned_df.isnull().sum().sum() == 0

def test_clean_duplicates_not_removed_when_disabled():
    data = {
        'id': [1, 1, 2],
        'price': [100.0, 100.0, 200.0]
    }
    df = pd.DataFrame(data)
    rules = {
        "drop_duplicates": False,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }
    cleaned_df = clean_data(df, rules)
    assert len(cleaned_df) == 3

def test_clean_does_not_mutate_original():
    data = {
        'id' : [1, 2],
        'price': [100.0, None]
    }
    df = pd.DataFrame(data)
    original_null_count = df['price'].isnull().sum()
    rules = {
        "drop_duplicates": False,
        "numeric_imputation_strategy": "median",
        "categorical_fill_value": "Unknown"
    }
    clean_data(df, rules)
    assert df['price'].isnull().sum() == original_null_count