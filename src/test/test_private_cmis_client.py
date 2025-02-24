import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from private_count_min.private_cmins_client import run_private_cmins_client
from tabulate import tabulate

def test_algoritmos():
    data = "dataOviedo"
    e = 150
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]

    general_table = []

    headers=[
        "Element", "Real Frequency", "Real Percentage", 
        "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
        "Percentage Error"
    ]

    

    for i in range(len(k)):
        _, data_table, G = run_private_cmins_client(k[i], m[i], e, data)
        
        
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




