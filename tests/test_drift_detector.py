import pandas as pd
import numpy as np
import pytest
from src.drift_detector import detect_drift

@pytest.fixture
def baseline_data():
    np.random.seed(42)
    return pd.DataFrame({
        'numeric_feature': np.random.randint(1, 20, size=100),
        'categorical_feature': ['A', 'B'] * 50
    })

def test_drift_detector_no_drift(baseline_data):
    np.random.seed(42)
    current_data = pd.DataFrame({
        'numeric_feature': np.random.normal(1, 20, size=100),
        'categorical_feature': ['A', 'B'] * 50
    })
    drift_report = detect_drift(baseline_data, current_data, threshold=3.0, z_threshold=999)
    assert isinstance(drift_report, dict)
    assert 'numeric_feature' in drift_report
    assert drift_report['numeric_feature']['drift_detected'] is False

def test_drift_detector_flags_significant_drift(baseline_data):
    current_data = pd.DataFrame({
        'numeric_feature': np.random.randint(80, 100, size=100),
        'categorical_feature': ['A', 'B'] * 50
    })

    drift_report = detect_drift(baseline_data, current_data, threshold=0.15)
    assert 'numeric_feature' in drift_report
    assert drift_report['numeric_feature']['drift_detected'] is True

def test_drift_detector_ignores_non_numeric(baseline_data):
    current_data = pd.DataFrame({
        'numeric_feature': np.random.randint(1, 20, size=100),
        'categorical_feature': ['X', 'Y'] * 50
    })
    drift_report = detect_drift(baseline_data, current_data, threshold=3.0)
    assert drift_report is not None
    assert 'categorical_feature' not in drift_report

def test_drift_detector_empty_current_dataframe(baseline_data):
    current_data = pd.DataFrame()
    drift_report = detect_drift(baseline_data, current_data)
    assert 'summary' in drift_report
    assert drift_report['summary']['overall_drift_status'] is False

def test_drift_report_always_has_summary(baseline_data):
    current_data = baseline_data.copy()
    drift_report = detect_drift(baseline_data, current_data)
    assert 'summary' in drift_report
    assert 'overall_drift_status' in drift_report['summary']
    assert 'threshold_used' in drift_report['summary']
    assert 'drift_method' in drift_report['summary']
    assert 'excluded_columns' in drift_report['summary']

def test_drift_detector_auto_excludes_high_cardinality():
    baseline = pd.DataFrame({
        'unique_id': range(1000),
        'feature_a': np.random.randint(1, 20, size=1000)
    })
    current = pd.DataFrame({
        'unique_id': range(1000, 2000),
        'feature_a': np.random.normal(1, 20, 1000)
    })
    drift_report = detect_drift(baseline, current)
    assert 'unique_id' not in drift_report
    assert 'feature_a' in drift_report

def test_drift_trigger_field_accuracy(baseline_data):
    current_data = pd.DataFrame({
        'numeric_feature': np.random.randint(80, 100, size=100),
        'categorical_feature': ['A', 'B'] * 50
    })
    drift_report = detect_drift(baseline_data, current_data)
    assert 'numeric_feature' in drift_report
    assert drift_report['numeric_feature']['drift_trigger'] in [
        'both', 'pct_change', 'z_score', 'none'
    ]
    assert drift_report['numeric_feature']['drift_trigger'] != 'none'

@pytest.mark.parametrize("threshold,expected_drift", [
    (0.01, True),
    (0.50, False),
    (0.15, True),
])
def test_drift_threshold_sensitivity(threshold, expected_drift):
    np.random.seed(42)
    baseline = pd.DataFrame({
        'feature': np.random.randint(9, 12, size=500)
    })
    current = pd.DataFrame({
        'feature': np.random.randint(14, 17, size=500)
    })
    drift_report = detect_drift(
        baseline, current,
        threshold=threshold,
        z_threshold=999
    )
    assert 'feature' in drift_report
    assert drift_report['feature']['drift_detected'] is expected_drift