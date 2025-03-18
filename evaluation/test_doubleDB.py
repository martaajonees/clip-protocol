

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.count_mean.private_cms_client import run_private_cms_client
from src.scripts.preprocess import run_data_processor

def doubleDB(file_name):
    """
    Doubles the size of a given dataset by concatenating it with itself.

    Args:
        file_name (str): The name of the dataset file (without the extension).

    Returns:
        str: The name of the new dataset file that has been doubled.
    
    Saves the new dataset as a CSV file with '_doubled' added to the original file name.
    """
    # Load the dataset
    excel_file = os.path.join(os.path.join('..', '..', 'data', 'raw'), file_name) 
    df = pd.read_excel(excel_file)

    df_doubled = pd.concat([df, df], ignore_index=True)

    return df_doubled

def run_double_test():
    """
    Runs a test by evaluating the original and doubled versions of a dataset 
    using the Private Count Mean Sketch (PrivateCMS).

    The test runs the PrivateCMS client on both the original and doubled datasets, 
    and displays the error table after each run.
    
    The dataset used in this test is 'dataOviedo'.
    """
    excel_file = os.path.join(os.path.join('..', '..', 'data', 'raw'), 'dataOviedo.xlsx') 
    df = pd.read_excel(excel_file)

    print(" ========= Original DB ===========")
    run_private_cms_client(1024, 256, 50, df)

    # Transform the raw dataset 
    df = doubleDB('dataOviedo.xlsx')

    print(" ========= Double DB ===========")
    run_private_cms_client(1024, 256, 50, df)

if __name__ == '__main__':
    run_double_test()