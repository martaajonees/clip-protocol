import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch

from src.count_mean.private_cms_client import privateCMSClient, run_private_cms_client

class TestPrivateCMSClient(unittest.TestCase):

    @patch('pandas.read_excel')
    def setUp(self):
        # Create a sample dataset
        self.df = pd.DataFrame({
            'value': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
        })
        self.epsilon = 0.5  # Privacy parameter
        self.k = 3  # Number of hash functions
        self.m = 5  # Size of the sketch

        # Initialize the privateCMSClient object
        self.private_cms_client = privateCMSClient(self.epsilon, self.k, self.m, self.df)

    
    def test_initialization(self):
        # Verify the initialization of the privateCMSClient object
        self.assertEqual(self.private_cms_client.k, self.k)
        self.assertEqual(self.private_cms_client.m, self.m)
        self.assertEqual(len(self.private_cms_client.dataset), len(self.df))
        self.assertEqual(len(self.private_cms_client.domain), len(self.df['value'].unique()))
        self.assertEqual(self.private_cms_client.N, len(self.df))
        self.assertEqual(self.private_cms_client.M.shape, (self.k, self.m))

    def test_bernoulli_vector(self):
        # Verify the output of the bernoulli_vector function
        b = self.private_cms_client.bernoulli_vector()
        self.assertTrue(np.all(np.isin(b, [-1, 1])))

    def test_client_method(self):
        # Verify that the client method returns the privatized sketch vector and the hash index
        element = 2
        privatized_vector, hash_index = self.private_cms_client.client(element)

        self.assertEqual(privatized_vector.shape[0], self.m)
        self.assertTrue(np.any(privatized_vector == 1))  # Should have at least one 1
        self.assertGreaterEqual(hash_index, 0)
        self.assertLess(hash_index, self.k)

    def test_update_sketch_matrix(self):
        # Verify that the count matrix is updated correctly
        initial_matrix = self.private_cms_client.M.copy()
        v = np.full(self.m, 1)
        j = 1
        self.private_cms_client.update_sketch_matrix(v, j)
        self.assertFalse(np.array_equal(self.private_cms_client.M, initial_matrix))

    def test_estimate_client(self):
        # Verify that the frequency estimation works
        self.private_cms_client.update_sketch_matrix(np.full(self.m, 1), 1)
        estimated_frequency = self.private_cms_client.estimate_client(2)
        self.assertGreater(estimated_frequency, 0)

    @patch('private_cms_client.Progress')  # Mock the Progress class
    def test_execute_client(self, MockProgress):
        # Simulate the client-side process
        MockProgress.return_value.__enter__.return_value.add_task.return_value = None
        privatized_data = self.private_cms_client.execute_client()

        self.assertGreater(len(privatized_data), 0)
        self.assertEqual(len(privatized_data), len(self.df))

    @patch('private_cms_client.Progress') 
    def test_server_simulator(self, MockProgress):
        # Simulate the server-side process
        MockProgress.return_value.__enter__.return_value.add_task.return_value = None
        privatized_data = self.private_cms_client.execute_client()
        estimated_frequencies, _ = self.private_cms_client.server_simulator(privatized_data)

        self.assertGreater(len(estimated_frequencies), 0)
        self.assertTrue(all(isinstance(v, float) for v in estimated_frequencies.values()))

    @patch('pandas.read_excel')
    def test_run_private_cms_client(self):
        # Verify the output of the run_private_cms_client function
        H, data_table, error_table, privatized_data, df_estimated = run_private_cms_client(self.k, self.m, self.epsilon, self.df)

        self.assertIsInstance(data_table, pd.DataFrame)
        self.assertIsInstance(df_estimated, pd.DataFrame)
        self.assertGreater(df_estimated.shape[0], 0)  # At least one row in the result
        self.assertEqual(data_table.shape[1], 2)  # Two columns in the data table

if __name__ == '__main__':
    unittest.main()
