import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.privadjust.count_mean.private_cms_client import privateCMSClient, run_private_cms_client

@pytest.fixture
def sample_data():
    df = pd.DataFrame({'value': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})
    epsilon, k, m = 0.5, 3, 5
    return privateCMSClient(epsilon, k, m, df), df

def test_initialization(sample_data):
    private_cms, df = sample_data
    assert private_cms.k == 3
    assert private_cms.m == 5
    assert len(private_cms.dataset) == len(df)
    assert len(private_cms.domain) == len(df['value'].unique())
    assert private_cms.N == len(df)
    assert private_cms.M.shape == (private_cms.k, private_cms.m)

def test_bernoulli_vector(sample_data):
    private_cms, _ = sample_data
    b = private_cms.bernoulli_vector()
    assert np.all(np.isin(b, [-1, 1]))

def test_client_method(sample_data):
    private_cms, _ = sample_data
    element = 2
    privatized_vector, hash_index = private_cms.client(element)

    assert privatized_vector.shape[0] == private_cms.m
    assert np.any(privatized_vector == 1)
    assert 0 <= hash_index < private_cms.k

def test_update_sketch_matrix(sample_data):
    private_cms, _ = sample_data
    initial_matrix = private_cms.M.copy()
    v = np.full(private_cms.m, 1)
    private_cms.update_sketch_matrix(v, 1)
    assert not np.array_equal(private_cms.M, initial_matrix)

