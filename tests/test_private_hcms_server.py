import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch

from src.utils.utils import generate_hash_functions
from src.hadamard_count_mean.private_hcms_server import privateHCMSServer

class TestPrivateHCMSServer(unittest.TestCase):
    """
    Test cases for the private HCMS server implementation.
    """
    @patch('pandas.read_excel')
    def setUp(self):
        """
        Set up the initial data and parameters for the tests.
        """
        # Sample dataset for testing
        data = {'value': [1, 2, 3, 4, 5]}
        self.df = pd.DataFrame(data)

        # Set test parameters
        self.epsilon = 0.5
        self.k = 3  # Number of hash functions
        self.m = 5  # Number of columns in the sketch matrix
        
        # Generate hash functions
        primes = list(range(10**6, 10**7))  # Just an example of primes for the test
        p = primes[0]  # Use the first prime
        self.hashes = generate_hash_functions(self.k, p, 3, self.m)

        # Initialize the server
        self.server = privateHCMSServer(self.epsilon, self.k, self.m, self.df, self.hashes)

    def test_update_sketch_matrix(self):
        """
        Test the update of the sketch matrix.
        """
        w = 1.0
        j = 1
        l = 2
        initial_value = self.server.M[j, l]
        
        # Update the sketch matrix
        self.server.update_sketch_matrix(w, j, l)
        
        # Ensure the matrix has been updated correctly
        self.assertNotEqual(self.server.M[j, l], initial_value, "Sketch matrix was not updated correctly.")

    def test_estimate_server(self):
        """
        Test the frequency estimation function on the server.
        """
        element = 3
        estimated_frequency = self.server.estimate_server(element)
        
        # Check that the estimated frequency is a float
        self.assertIsInstance(estimated_frequency, float, "Estimated frequency should be a float.")

    @patch("builtins.input", side_effect=["1", "exit"])  # Mock input for interactive queries
    def test_query_server(self, mock_input):
        """
        Test the query server function for element frequency.
        """
        element = 1
        result = self.server.query_server(element)
        
        # Test that the correct estimated frequency is returned
        self.assertIsInstance(result, float, "Query result should be a float representing frequency.")

    def test_execute_server(self):
        """
        Test the full execution of the server process with privatized data.
        """
        privatized_data = [(1.0, 0, 1), (0.5, 1, 2), (-1.0, 2, 3)]  # Example privatized data
        
        f_estimated = self.server.execute_server(privatized_data)
        
        # Ensure the estimated frequencies are calculated correctly
        self.assertIsInstance(f_estimated, dict, "Expected the result to be a dictionary of estimated frequencies.")
        self.assertGreater(len(f_estimated), 0, "Estimated frequencies dictionary should not be empty.")

if __name__ == "__main__":
    unittest.main()
