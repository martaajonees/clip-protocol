import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.privadjust.count_mean.cms_client_mean import CMSClient, run_cms_client_mean

@pytest.fixture
def sample_data():
    df = pd.DataFrame({'value': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})
    k, m = 3, 5
    return CMSClient(k, m, df), df

def test_initialization(sample_data):
    cms_client, df = sample_data
    assert cms_client.k == 3
    assert cms_client.m == 5
    assert len(cms_client.dataset) == len(df)
    assert len(cms_client.domain) == len(df['value'].unique())
    assert cms_client.N == len(df)
    assert cms_client.M.shape == (cms_client.k, cms_client.m)

def test_client_method(sample_data):
    cms_client, _ = sample_data
    element = 2
    sketch_vector, hash_index = cms_client.client(element)

    assert sketch_vector.shape[0] == cms_client.m
    assert np.all(sketch_vector == -1) or np.any(sketch_vector == 1)
    assert 0 <= hash_index < cms_client.k

def test_update_sketch_matrix(sample_data):
    cms_client, _ = sample_data
    initial_matrix = cms_client.M.copy()
    cms_client.update_sketch_matrix(2)
    assert not np.array_equal(cms_client.M, initial_matrix)

def test_estimate_client(sample_data):
    cms_client, _ = sample_data
    cms_client.update_sketch_matrix(2)
    estimated_frequency = cms_client.estimate_client(2)
    assert estimated_frequency > 0