import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

from src.scripts.parameter_fitting import PrivacyUtilityOptimizer

class TestPrivacyUtilityOptimizer(unittest.TestCase):

    def setUp(self):
        # Create a sample dataset
        data = {'value': ['A', 'B', 'A', 'C', 'B', 'A']}
        self.df = pd.DataFrame(data)
        self.k = 2
        self.m = 3
        self.algorithm = '1'  # CMS

        # Initialize the PrivacyUtilityOptimizer object
        self.optimizer = PrivacyUtilityOptimizer(self.df, self.k, self.m, self.algorithm)

    def test_get_real_frequency(self):
        # Verify that the real frequency is calculated correctly
        expected_freq = {'Element': ['A', 'B', 'C'], 'Frequency': [3, 2, 1]}
        real_freq = self.optimizer.get_real_frequency()
        pd.testing.assert_frame_equal(real_freq, pd.DataFrame(expected_freq))

    @patch('privacy_utility_optimizer.run_private_cms_client')
    def test_run_command(self, mock_run_private_cms_client):
        # Simulate the execution of the command
        mock_run_private_cms_client.return_value = ('result', 'data_table', 'error_table', 'privatized_data', 'df_estimated')

        result, data_table, error_table, privatized_data = self.optimizer.run_command(0.1)

        # Verify that the run_command function returns the expected values
        self.assertEqual(result, 'result')
        self.assertEqual(data_table, 'data_table')
        self.assertEqual(error_table, 'error_table')
        self.assertEqual(privatized_data, 'privatized_data')

    @patch('privacy_utility_optimizer.run_private_cms_client')
    def test_optimize_e_with_optuna(self, mock_run_private_cms_client):
        # Test to optimize the value of e using Optuna
        mock_run_private_cms_client.return_value = ('result', 'data_table', 'error_table', 'privatized_data', 'df_estimated')

        # Simulate the optimization process
        best_e, privatized_data, error_table, result, data_table = self.optimizer.optimize_e_with_optuna(0.1, 2, '2', 10)

        # Verify that the best value of e is returned
        self.assertIsInstance(best_e, float)

    @patch('privacy_utility_optimizer.run_private_cms_client')
    def test_frequencies(self, mock_run_private_cms_client):
        # Test to get the estimated and real frequencies
        mock_run_private_cms_client.return_value = ('result', 'data_table', 'error_table', 'privatized_data', 'df_estimated')

        estimated_freq, real_freq = self.optimizer.frequencies()

        # Verify that the frequencies are returned as DataFrames
        self.assertIsInstance(estimated_freq, pd.DataFrame)
        self.assertIsInstance(real_freq, pd.DataFrame)

    @patch('builtins.input', return_value="1")
    def test_run(self, mock_input):
        # Test to run the optimizer
        mock_input.return_value = "1"  # Simulate the user input

        e, result, privatized_data = self.optimizer.run()

        # Verify that the run function returns the expected values
        self.assertIsInstance(e, float)

if __name__ == '__main__':
    unittest.main()
