import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch

from src.utils.utils import generate_hash_functions
from src.hadamard_count_mean.private_hcms_server import privateHCMSServer

@pytest.fixture
def server():
    """
    Set up the initial data and parameters for the tests.
    """
    # Sample dataset for testing
    data = {'value': [1, 2, 3, 4, 5]}
    df = pd.DataFrame(data)

    # Set test parameters
    epsilon = 0.5
    k = 3  # Number of hash functions
    m = 5  # Number of columns in the sketch matrix

    # Generate hash functions
    primes = list(range(10**6, 10**7))  # Just an example of primes for the test
    p = primes[0]  # Use the first prime
    hashes = generate_hash_functions(k, p, 3, m)

    # Initialize the server
    return privateHCMSServer(epsilon, k, m, df, hashes)


def test_update_sketch_matrix(server):
    """
    Test the update of the sketch matrix.
    """
    w = 1.0
    j = 1
    l = 2
    initial_value = server.M[j, l]
    
    # Update the sketch matrix
    server.update_sketch_matrix(w, j, l)
    
    # Ensure the matrix has been updated correctly
    assert server.M[j, l] != initial_value, "Sketch matrix was not updated correctly."


def test_estimate_server(server):
    """
    Test the frequency estimation function on the server.
    """
    element = 3
    estimated_frequency = server.estimate_server(element)
    
    # Check that the estimated frequency is a float
    assert isinstance(estimated_frequency, float), "Estimated frequency should be a float."


def test_query_server(server):
    """
    Test the query server function for element frequency.
    """
    element = 1
    result = server.query_server(element)
    
    # Test that the correct estimated frequency is returned
    assert isinstance(result, float), "Query result should be a float representing frequency."


def test_execute_server(server):
    """
    Test the full execution of the server process with privatized data.
    """
    privatized_data = [(1.0, 0, 1), (0.5, 1, 2), (-1.0, 2, 3)]  # Example privatized data
    
    f_estimated = server.execute_server(privatized_data)
    
    # Ensure the estimated frequencies are calculated correctly
    assert isinstance(f_estimated, dict), "Expected the result to be a dictionary of estimated frequencies."
    assert len(f_estimated) > 0, "Estimated frequencies dictionary should not be empty."