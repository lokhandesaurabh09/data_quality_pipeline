import pandas as pd
import pytest
from src.ingest import load_raw_data

@pytest.mark.parametrize(
    "input_data,file_ext",
    [
        (pd.DataFrame({'col_int': [1, 2], 'col_str': ['a', 'b']}), ".csv"),
        (pd.DataFrame({'metric': [10.5, 20.1, 30.2]}), ".csv"),
        (pd.DataFrame({f"feat_{i}": range(5) for i in range(10)}), ".csv"),
    ]
)

def test_load_raw_data_generalized(tmp_path, input_data, file_ext):
    file_path = tmp_path / f"test_dataset{file_ext}"
    input_data.to_csv(file_path, index=False)

    loaded_df = load_raw_data(str(file_path))

    assert not loaded_df.empty
    assert len(loaded_df) == len(input_data)
    assert len(loaded_df.columns) == len(input_data.columns)

    pd.testing.assert_frame_equal(loaded_df, input_data, check_dtype=False)

def test_load_raw_data_file_not_found():
    non_existent_path = "data/raw/non_existent_file_xyz.csv"

    with pytest.raises(FileNotFoundError):
        load_raw_data(non_existent_path)

def test_load_raw_data_empty_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")

    with pytest.raises(pd.errors.EmptyDataError):
        load_raw_data(str(file_path))

def test_load_raw_data_preserves_column_order(tmp_path):
    expected_cols = ['feat_alpha', 'target_beta', 'category_gamma']
    data = pd.DataFrame({
        'feat_alpha': [1, 2],
        'target_beta': [10.5, 20.1],
        'category_gamma': ['x', 'y']
    })

    file_path = tmp_path / "order_test.csv"
    data.to_csv(file_path, index=False)

    loaded_df = load_raw_data(str(file_path))

    assert list(loaded_df.columns) == expected_cols

def test_load_raw_data_single_row(tmp_path):
    data = pd.DataFrame({'id': [1], 'value': [42.0]})
    file_path = tmp_path / "single.csv"
    data.to_csv(file_path, index=False)

    loaded_df = load_raw_data(str(file_path))

    assert len(loaded_df) == 1

def test_load_raw_data_preserves_nulls(tmp_path):
    data = pd.DataFrame({'id': [1, 2], 'value': [100.0, None]})
    file_path = tmp_path / "nulls.csv"
    data.to_csv(file_path, index=False)

    loaded_df = load_raw_data(str(file_path))

    assert loaded_df['value'].isnull().sum() == 1


                                