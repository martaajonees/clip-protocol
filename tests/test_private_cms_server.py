import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch

from src.count_mean.private_cms_server import privateCMSServer

class TestPrivateCMSServer(unittest.TestCase):

    def setUp(self):
        
        self.df = pd.DataFrame({
            'value': ['a', 'b', 'c', 'd', 'e']
        })
        self.k = 3  # Number of hash functions
        self.m = 5  # Size of the sketch
        self.epsilon = 1.0  # Privacy parameter
        self.H = [lambda x: (ord(x) - 97) % self.m] * self.k  
        self.privatized_data = [
            (np.array([1, -1, -1, -1, -1]), 0),
            (np.array([-1, 1, -1, -1, -1]), 1),
            (np.array([-1, -1, 1, -1, -1]), 2),
        ]
        
        self.server = privateCMSServer(self.epsilon, self.k, self.m, self.df, self.H)

    def test_update_sketch_matrix(self):
        v = np.array([1, -1, 1, -1, 1])  # Test vector
        j = 0  # Test index
        original_matrix = self.server.M.copy()
        
        self.server.update_sketch_matrix(v, j)
        
        # Verify that the matrix has been updated
        self.assertFalse(np.array_equal(self.server.M, original_matrix))

    def test_estimate_server(self):
        
        element = 'a'  # Element to estimate
        estimated_frequency = self.server.estimate_server(element)
        
        # Verify that the estimated frequency is a float
        self.assertIsInstance(estimated_frequency, float)

    def test_query_server(self):
        valid_element = 'a'
        invalid_element = 'z'
        
        valid_estimation = self.server.query_server(valid_element)
        self.assertIsInstance(valid_estimation, float)
        
        invalid_estimation = self.server.query_server(invalid_element)
        self.assertEqual(invalid_estimation, "Element not in the domain")

    @patch('builtins.input', return_value='a')
    def test_run_private_cms_server_query(self, mock_input):
        with patch('builtins.print') as mock_print:
            # Mock the query_server method
            self.server.query_server = lambda x: 3.14  # Return a fixed value
            
            self.server.query_server('a')  # Run the query
            mock_print.assert_called_with('The estimated frequency of a is 3.14')

    def test_execute_server(self):
        f_estimated = self.server.execute_server(self.privatized_data)
    
        self.assertIsInstance(f_estimated, dict)
        self.assertTrue(all(isinstance(val, float) for val in f_estimated.values()))

if __name__ == '__main__':
    unittest.main()
