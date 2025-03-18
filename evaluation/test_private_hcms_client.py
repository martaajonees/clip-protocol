import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.hadamard_count_mean.private_hcms_client import run_private_hcms_client
from tabulate import tabulate

def test_algoritmos():
    """
    Runs a test for various parameter combinations using the Private Hadamard Count Mean Sketch algorithm.

    This function tests the algorithm by passing different values of k (number of hash functions) and 
    m (number of counters) to the `run_private_hcms_client` function. The results include various error 
    metrics, including Mean Error, Percentage Error, MSE, RMSE, Normalized MSE, Normalized RMSE, and Pearson 
    Correlation Coefficient. The results are displayed in a tabular format.

    The test data used is based on the 'exp_distrib_50k' dataset, and the error tolerance (e) is set to 2.

    The results are printed in a table, where each row contains:
        - k: Number of hash functions
        - m: Number of counters
        - Mean Error
        - Percentage Error
        - MSE (Mean Squared Error)
        - RMSE (Root Mean Squared Error)
        - Normalized MSE
        - Normalized RMSE
        - Pearson Correlation Coefficient
    """
    excel_file = os.path.join(os.path.join('..', '..', 'data', 'raw'), 'dataOviedo.xlsx') 
    df = pd.read_excel(excel_file)

    e = 2
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]

    general_table = []

    for i in range(len(k)):
        _, error_table = run_private_hcms_client(k[i], m[i], e, df)

        error_dict = { key: value for key, value in error_table }

        row = [
            k[i],
            m[i],
            error_dict.get("Mean Error", ""),
            error_dict.get("Percentage Error", ""),
            error_dict.get("MSE", ""),
            error_dict.get("RMSE", ""),
            error_dict.get("Normalized MSE", ""),
            error_dict.get("Normalized RMSE", ""),
            error_dict.get("Pearson Correlation Coefficient", "")
        ]
        general_table.append(row)

    headers = [
        "k", "m", "Mean Error", "Percentage Error", 
        "MSE", "RMSE", "Normalized MSE", "Normalized RMSE", "Pearson Corr"
    ]

    print(tabulate(general_table, headers=headers, tablefmt="grid"))
    
if __name__ == '__main__':
    test_algoritmos()




