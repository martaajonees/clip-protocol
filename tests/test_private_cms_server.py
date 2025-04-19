import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.clip_protocol.count_mean.private_cms_server import privateCMSServer

@pytest.fixture
def sample_server():
    df = pd.DataFrame({'value': ['a', 'b', 'c', 'd', 'e']})
    k, m, epsilon = 3, 5, 1.0
    H = [lambda x: (ord(x) - 97) % m] * k  
    privatized_data = [
        (np.array([1, -1, -1, -1, -1]), 0),
        (np.array([-1, 1, -1, -1, -1]), 1),
        (np.array([-1, -1, 1, -1, -1]), 2),
    ]
    return privateCMSServer(epsilon, k, m, df, H), privatized_data

def test_update_sketch_matrix(sample_server):
    server, _ = sample_server
    v = np.array([1, -1, 1, -1, 1])
    j = 0
    original_matrix = server.M.copy()
    server.update_sketch_matrix(v, j)
    assert not np.array_equal(server.M, original_matrix)

def test_estimate_server(sample_server):
    server, _ = sample_server
    estimated_frequency = server.estimate_server('a')
    assert isinstance(estimated_frequency, float)

def test_query_server(sample_server):
    server, _ = sample_server
    assert isinstance(server.query_server('a'), float)
    assert server.query_server('z') == "Element not in the domain"

def test_execute_server(sample_server):
    server, privatized_data = sample_server
    f_estimated = server.execute_server(privatized_data)
    assert isinstance(f_estimated, dict)
    assert all(isinstance(val, float) for val in f_estimated.values())
