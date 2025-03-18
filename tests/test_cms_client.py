import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch

from src.count_mean.cms_client_mean import CMSClient, run_cms_client_mean

class TestCMSClient(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset
        self.df = pd.DataFrame({
            'value': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
        })
        self.k = 3  # number of hash functions
        self.m = 5  # size of the sketch

        # Initialize the CMSClient object
        self.cms_client = CMSClient(self.k, self.m, self.df)

    def test_initialization(self):
        # Verify the initialization of the CMSClient object
        self.assertEqual(self.cms_client.k, self.k)
        self.assertEqual(self.cms_client.m, self.m)
        self.assertEqual(len(self.cms_client.dataset), len(self.df))
        self.assertEqual(len(self.cms_client.domain), len(self.df['value'].unique()))
        self.assertEqual(self.cms_client.N, len(self.df))
        self.assertEqual(self.cms_client.M.shape, (self.k, self.m))

    def test_client_method(self):
        # Verify that the client method returns the sketch vector and the hash index
        element = 2
        sketch_vector, hash_index = self.cms_client.client(element)

        self.assertEqual(sketch_vector.shape[0], self.m)
        self.assertTrue(np.all(sketch_vector == -1) or np.any(sketch_vector == 1))  # Vector con 1 o -1
        self.assertGreaterEqual(hash_index, 0)
        self.assertLess(hash_index, self.k)

    def test_update_sketch_matrix(self):
        #Verify that the count matrix is updated correctly
        initial_matrix = self.cms_client.M.copy()
        self.cms_client.update_sketch_matrix(2)
        self.assertFalse(np.array_equal(self.cms_client.M, initial_matrix))

    def test_estimate_client(self):
        # Verify that the frequency estimation works
        self.cms_client.update_sketch_matrix(2)
        estimated_frequency = self.cms_client.estimate_client(2)
        self.assertGreater(estimated_frequency, 0)

    @patch('cms_client.Progress')  # Mock the Progress class
    def test_server_simulator(self, MockProgress):
        # Simulate the server-side process
        MockProgress.return_value.__enter__.return_value.add_task.return_value = None
        estimated_frequencies = self.cms_client.server_simulator()

        self.assertGreater(len(estimated_frequencies), 0)
        self.assertTrue(all(isinstance(v, float) for v in estimated_frequencies.values()))

    def test_run_cms_client_mean(self):
        # Verify that the CMS client is executed
        result = run_cms_client_mean(self.k, self.m, self.df)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(result.shape[1], 2)  # Two columns: Element and Frequency

if __name__ == '__main__':
    unittest.main()