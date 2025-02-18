import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client
from tabulate import tabulate

def test_algoritmos():
    data = "exp_distrib_50k"
    e = 2
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]

    general_table = []

    for i in range(len(k)):
        _, error_table = run_private_hcms_client(k[i], m[i], e, data)

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




