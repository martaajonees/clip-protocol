import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from io import StringIO

from src.scripts.preprocess import DataProcessor

class TestDataProcessor(unittest.TestCase):

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('pandas.read_excel')

    def test_initialization_and_file_loading(self, mock_read_excel, mock_listdir, mock_exists):
        mock_exists.return_value = True # Mocking the existence of the file
        mock_listdir.return_value = ['data1.xlsx', 'data2.xlsx']

        mock_read_excel.return_value = pd.DataFrame({
            'Participant': [1, 2, 3],
            'Fixation Position X [px]': [100, 200, 300],
            'Fixation Position Y [px]': [100, 200, 300],
            'AOI Name': ['AOI1', 'AOI2', 'AOI3']
        })

        processor = DataProcessor()

        self.assertEqual(processor.file_name, 'data2.xlsx')
        self.assertTrue(isinstance(processor.df, pd.DataFrame))
    
    @patch('pandas.read_excel')
    def test_filter_columns(self, mock_read_excel):
        # Mocking a dataset with some values
        mock_read_excel.return_value = pd.DataFrame({ 
            'Participant': [1, 2],
            'Fixation Position X [px]': [100, '-'],
            'Fixation Position Y [px]': ['-', 200],
            'AOI Name': ['AOI1', 'AOI2']
        })

        processor = DataProcessor()
        filtered_df = processor.filter_columns()

        # Verifying if the columns are correctly filtered
        self.assertEqual(filtered_df.shape[0], 1)  # Only one row should remain
        self.assertIn('Participant', filtered_df.columns)
        self.assertNotIn('Fixation Position X [px]', filtered_df.columns)
        self.assertNotIn('Fixation Position Y [px]', filtered_df.columns)

    @patch('pandas.read_excel')
    def test_aoi_hits(self, mock_read_excel):
        # Mocking a dataset with some values
        mock_read_excel.return_value = pd.DataFrame({
            'Participant': [1, 2],
            'Fixation Position X [px]': ['100', '-'],
            'Fixation Position Y [px]': ['-', '200'],
            'AOI Name': ['AOI1', 'AOI2']
        })

        processor = DataProcessor()
        processor.filter_columns()
        processor.aoi_hits()  # Processing the AOI hits

        # Verifying if the AOI hits are correctly processed
        self.assertIn('user_id', processor.df.columns)
        self.assertIn('value', processor.df.columns)
        self.assertEqual(processor.df.shape[0], 2)  # Two rows should be added

if __name__ == '__main__':
    unittest.main()