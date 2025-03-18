import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.count_mean.private_cms_client import run_private_cms_client
from tabulate import tabulate

def test_algoritmos():
    """
    Runs a test for various parameter combinations using the Private Count Mean Sketch algorithm.

    This function tests the algorithm by passing different values of k (number of hash functions) and 
    m (number of counters) to the `run_private_cms_client` function. The real and estimated frequencies
    for different elements are compared, and the results are displayed in a tabulated format.
    
    The test data used is based on the 'dataOviedo' dataset, and the error tolerance (e) is set to 50.

    The results include:
        - Real frequency
        - Real percentage
        - Estimated frequency
        - Estimated percentage
        - Estimation difference
        - Percentage error
    
    The results are printed in a tabular format using the `tabulate` library.
    """
    excel_file = os.path.join(os.path.join('..', '..', 'data', 'raw'), 'dataOviedo.xlsx') 
    df = pd.read_excel(excel_file)
    
    e = 50
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]

    general_table = []

    headers=[
        "Element", "Real Frequency", "Real Percentage", 
        "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
        "Percentage Error"
    ]

    for i in range(len(k)):
        _, data_table, _ = run_private_cms_client(k[i], m[i], e, df)

        data_dicts = [dict(zip(headers, row)) for row in data_table]

        for data_dict in data_dicts:
            general_table.append([
                k[i], m[i], 
                data_dict.get("Element", ""),
                data_dict.get("Real Frequency", ""),
                data_dict.get("Real Percentage", ""),
                data_dict.get("Estimated Frequency", ""),
                data_dict.get("Estimated Percentage", ""),
                data_dict.get("Estimation Difference", ""),
                data_dict.get("Percentage Error", ""),
            ])
            

    headers=[
        "k", "m", "Element", "Real Frequency", "Real Percentage", 
        "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
        "Percentage Error"
    ]

    print(tabulate(general_table, headers=headers, tablefmt="grid"))
    
if __name__ == '__main__':
    test_algoritmos()




