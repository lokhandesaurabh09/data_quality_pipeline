import pandas as pd
import numpy as np
import pytest
from src.validate import validate_data

@pytest.fixture
def base_rules():
    return{
        "required_columns": [],
        "max_null_percentage": 0.30,
        "check_infinite_values": True,
        "fail_on_empty": True
    }

def test_validate_success(base_rules):
    data = pd.DataFrame({
        'col_a': [1, 2, 3],
        'col_b': ['x', 'y', 'z']
    })
    result = validate_data(data, base_rules)
    assert result is True

def test_validate_empty_dataframe(base_rules):
    data = pd.DataFrame()
    with pytest.raises(ValueError):
        validate_data(data, base_rules)

def test_validate_empty_dataframe_no_fail():
    data = pd.DataFrame()
    rules = {
        "required_columns": [],
        "max_null_percentage": 0.30,
        "check_infinite_values": True,
        "fail_on_empty": False
    }
    result = validate_data(data, rules)
    assert result is False

def test_validate_missing_required_columns():
    data = pd.DataFrame({
        'col_a': [1, 2, 3]
    })

    rules = {
        "required_columns": ["col_a", "col_b"],
        "max_null_percentage": 0.30,
        "check_infinite_values": True,
        "fail_on_empty": True
    }

    with pytest.raises(ValueError):
        validate_data(data, rules)

def test_validate_required_columns_present():
    data = pd.DataFrame({
        'feature_x': [1, 2, 3],
        'feature_y': [4, 5, 6],
        'feature_z': ['a', 'b', 'c']
    })

    rules = {
        "required_columns": ["feature_x", "feature_y", "feature_z"],
        "max_null_percentage": 0.30,
        "check_infinite_values": True,
        "fail_on_empty": True
    }
    result = validate_data(data, rules)
    assert result is True

def test_validate_high_null_percentage_warns():
    data = pd.DataFrame({
        'col_a': [1, None, None, None, None],
        'col_b': [1, 2, 3, 4, 5]
    })
    rules = {
        "required_columns": [],
        "max_null_percentage": 0.30,
        "check_infinite_values": True,
        "fail_on_empty": True
    }
    result = validate_data(data, rules)
    assert result is True

def test_validate_infinite_values_detected():
    data = pd.DataFrame({
        'col_a': [1.0, np.inf, 3.0],
        'col_b': [4.0, 5.0, -np.inf]
    })
    rules = {
        "required_columns": [],
        "max_null_percentage": 0.30,
        "check_infinite_values": True,
        "fail_on_empty": True
    }
    result = validate_data(data, rules)
    assert result is True

@pytest.mark.parametrize("rows,cols", [
    (1, 1),
    (10, 5),
    (1000, 20),
])

def test_validate_various_shapes(rows, cols):
    data = pd.DataFrame({
        f"feature_{i}": range(rows)
        for i in range(cols)
    })
    rules = {
        "required_columns": [],
        "max_null_percentage":  0.30,
        "check_infinite_values": True,
        "fail_on_empty": True
    }
    result = validate_data(data, rules)
    assert result is True

