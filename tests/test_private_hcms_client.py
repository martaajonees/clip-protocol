import numpy as np
import pandas as pd
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from src.privadjust.hadamard_count_mean.private_hcms_client import privateHCMSClient

@pytest.fixture
def client():
    df = pd.DataFrame({
        'value': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    })
    epsilon = 0.5
    k = 3
    m = 4
    return privateHCMSClient(epsilon, k, m, df)


def test_initialization(client):
    """ Test that the privateHCMSClient is initialized correctly. """
    assert client.epsilon == 0.5
    assert client.k == 3
    assert client.m == 4
    assert len(client.dataset) == 10
    assert len(client.domain) == 5
    assert client.M.shape == (3, 4)
    assert len(client.client_matrix) == 0

def test_update_sketch_matrix(client):
    """ Test the update of the sketch matrix. """
    w = 0.5
    j = 0
    l = 1
    initial_value = client.M[j, l]
    
    # Update sketch matrix
    client.update_sketch_matrix(w, j, l)

    assert client.M[j, l] != initial_value


def test_estimate_client(client):
    """ Test the frequency estimation method. """
    d = 1
    estimated_frequency = client.estimate_client(d)

    assert isinstance(estimated_frequency, float)


def test_execute_client(client):
    """ Test the client execution, ensuring data is processed and privatized correctly. """
    privatized_data = client.execute_client()

    assert len(privatized_data) == 10


def test_server_simulator(client):
    """ Test the server-side process of updating the sketch matrix and estimating frequencies. """
    privatized_data = client.execute_client()

    f_estimated, hashes = client.server_simulator(privatized_data)

    assert len(f_estimated) > 0
    assert len(hashes) == 3