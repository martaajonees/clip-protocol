import pytest
import pandas as pd
from src.scripts.parameter_fitting import PrivacyUtilityOptimizer

@pytest.fixture
def sample_data():
    data = {'value': ['A', 'B', 'A', 'C', 'B', 'A']}
    return pd.DataFrame(data)

@pytest.fixture
def optimizer(sample_data):
    return PrivacyUtilityOptimizer(sample_data, k=2, m=3, algorithm='1')

def test_get_real_frequency(optimizer):
    expected_freq = pd.DataFrame({'Element': ['A', 'B', 'C'], 'Frequency': [3, 2, 1]})
    real_freq = optimizer.get_real_frequency()
    pd.testing.assert_frame_equal(real_freq, expected_freq)

def test_run_command(optimizer):
    result, data_table, error_table, privatized_data = optimizer.run_command(0.1)
    
    assert isinstance(result, str)
    assert isinstance(data_table, pd.DataFrame)
    assert isinstance(error_table, pd.DataFrame)
    assert isinstance(privatized_data, pd.DataFrame)

def test_optimize_e_with_optuna(optimizer):
    best_e, privatized_data, error_table, result, data_table = optimizer.optimize_e_with_optuna(0.1, 2, '2', 10)
    
    assert isinstance(best_e, float)
    assert isinstance(privatized_data, pd.DataFrame)
    assert isinstance(error_table, pd.DataFrame)
    assert isinstance(result, str)
    assert isinstance(data_table, pd.DataFrame)

def test_frequencies(optimizer):
    estimated_freq, real_freq = optimizer.frequencies()
    
    assert isinstance(estimated_freq, pd.DataFrame)
    assert isinstance(real_freq, pd.DataFrame)

def test_run(optimizer, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '1')
    e, result, privatized_data = optimizer.run()
    
    assert isinstance(e, float)
    assert isinstance(result, str)
    assert isinstance(privatized_data, pd.DataFrame)