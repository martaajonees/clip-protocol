import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch

from src.utils.utils import generate_error_table
from src.hadamard_count_mean.private_hcms_client import privateHCMSClient

class TestPrivateHCMSClient(unittest.TestCase):
    @patch('pandas.read_excel')
    def setUp(self):
        """ 
        Setup for the tests. It initializes the basic parameters needed for the client.
        """
        # Example dataframe with some data
        self.df = pd.DataFrame({
            'value': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
        })
        self.epsilon = 0.5
        self.k = 3
        self.m = 4
        
        # Initialize the privateHCMSClient object with the given parameters
        self.client = privateHCMSClient(self.epsilon, self.k, self.m, self.df)

    def test_initialization(self):
        """ 
        Test that the privateHCMSClient is initialized correctly.
        """
        self.assertEqual(self.client.epsilon, self.epsilon)  # Check if epsilon is correctly set
        self.assertEqual(self.client.k, self.k)  # Check if k is correctly set
        self.assertEqual(self.client.m, self.m)  # Check if m is correctly set
        self.assertEqual(len(self.client.dataset), 10)  # Ensure dataset has 10 elements
        self.assertEqual(len(self.client.domain), 5)  # Ensure there are 5 unique elements in the dataset
        self.assertEqual(self.client.M.shape, (self.k, self.m))  # Ensure the matrix M has the correct shape
        self.assertEqual(self.client.client_matrix, [])  # Ensure the client_matrix is initially empty

    @patch('your_module.generate_hash_functions')  # Mock the hash function generator
    def test_client_method(self, mock_generate_hash_functions):
        """
        Test the client privatization method.
        """
        mock_generate_hash_functions.return_value = [lambda x: x % self.m] * self.k  # Mock hash function

        privatized_value, j, l = self.client.client(1)

        # Ensure privatized_value is a number
        self.assertIsInstance(privatized_value, float)
        self.assertEqual(j, 0)  # Check that the index of the hash function is 0
        self.assertEqual(l, 0)  # Check that the index of the matrix is 0
        self.assertEqual(len(self.client.client_matrix), 1)  # Ensure client_matrix contains 1 element after the call

    def test_update_sketch_matrix(self):
        """
        Test the update of the sketch matrix.
        """
        w = 0.5
        j = 0
        l = 1
        initial_value = self.client.M[j, l]
        
        # Update sketch matrix
        self.client.update_sketch_matrix(w, j, l)

        # Ensure the matrix has been updated
        self.assertNotEqual(self.client.M[j, l], initial_value)  # The value should have changed

    def test_traspose_M(self):
        """
        Test that the matrix M is correctly transposed.
        """
        initial_M = self.client.M.copy()

        # Perform the transpose operation
        self.client.traspose_M()

        # Ensure that M has been correctly transposed
        self.assertTrue(np.array_equal(self.client.M, np.transpose(initial_M)))

    def test_estimate_client(self):
        """
        Test the frequency estimation method.
        """
        d = 1
        estimated_frequency = self.client.estimate_client(d)

        # Ensure that the estimated frequency is a float
        self.assertIsInstance(estimated_frequency, float)

    @patch('your_module.Progress')  # Mock the Progress class for testing
    def test_execute_client(self, MockProgress):
        """
        Test the client execution, ensuring data is processed and privatized correctly.
        """
        mock_progress = MockProgress.return_value
        mock_task = mock_progress.add_task.return_value

        # Execute client-side operation
        privatized_data = self.client.execute_client()

        # Ensure the mock progress is being used
        self.assertTrue(mock_progress.add_task.called)
        self.assertEqual(len(privatized_data), 10)  # Ensure the privatized data has 10 elements

    @patch('your_module.Progress')  # Mock the Progress class for testing
    def test_server_simulator(self, MockProgress):
        """
        Test the server-side process of updating the sketch matrix and estimating frequencies.
        """
        privatized_data = self.client.execute_client()  # Simulate client-side execution

        mock_progress = MockProgress.return_value
        mock_task = mock_progress.add_task.return_value

        # Simulate the server-side operation
        f_estimated, hashes = self.client.server_simulator(privatized_data)

        # Ensure progress is being tracked
        self.assertTrue(mock_progress.add_task.called)
        self.assertGreater(len(f_estimated), 0)  # Ensure some frequencies were estimated
        self.assertEqual(len(hashes), self.k)  # Ensure the correct number of hash functions were used

if __name__ == '__main__':
    unittest.main()
