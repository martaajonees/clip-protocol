import os
import importlib.util
import pandas as pd
import math

from tabulate import tabulate
import numpy as np

# Importing CMeS functions
from private_count_mean.private_cms_server import run_private_cms_server
from private_count_mean.private_cms_client import run_private_cms_client
from private_count_mean.cms_client_mean import run_cms_client_mean

# Importing data preprocessing functions
from scripts.preprocess import run_data_processor
from scripts.parameter_fitting import run_parameter_fitting

# Importing CMiS functions
from private_count_min.private_cmins_client import run_private_cmins_client
from private_count_min.private_cmins_server import run_private_cmins_server
from private_count_min.cms_client_min import run_cmins_client

# Importing HCMS functions
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client
from private_hadamard_count_mean.private_hcms_server import run_private_hcms_server

def execute(database, algorithm, k, m):
    print("\nExecuting personalized privacy ...")
    e, result, privatized_data = run_parameter_fitting(database, k, m, algorithm)

    H = result["H"]
    hashes = result["hashes"]
    G = result["G"]

    print("\nExecuting server ...")
    if algorithm == '1':
        run_private_cms_server(k, m, e, database, H, privatized_data)
    elif algorithm == '2':
        run_private_hcms_server(k, m, e, database, hashes, privatized_data)

    print("\nProcess done and results saved.")

def calculate_k_m():
    f = float(input("Enter the failure probability: "))
    E = float(input("Enter the overestimation factor: "))

    k = int(1 / f)
    m = int(2.71828 / E )

    print(f"k={k}, m={m}")
    print(f"Space complexity: {k*m}")
    return k, m

def execute_no_privacy(k, m, database):
    headers=[
        "Element", "Real Frequency", "Real Percentage", 
        "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
        "Percentage Error"
    ]

    # print("\n CMiS without privacy")
    # data_table = run_cmins_client(k, m, database)
    # print(tabulate(data_table, headers=headers, tablefmt="grid"))

    print("\n CMeS without privacy")
    data_table = run_cms_client_mean(k, m, database)
    print(tabulate(data_table, headers=headers, tablefmt="grid"))
    
def execute_algorithms(database, k_client, m_client):
    e = 150   
    # k_values = [k_client, 16, 128, 1024, 32768]
    # m_values = [m_client, 16, 1024, 256, 256]

    k_values = [32768]
    m_values = [256]

    results = {"CMeS": [], "HCMS": []}

    headers=[
        "Element", "Real Frequency", "Real Percentage", 
        "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
        "Percentage Error"
    ]

    for k, m in zip(k_values, m_values):
        for algorithm, client in zip(["CMeS", "HCMS"], [run_private_cms_client, run_private_hcms_client]):
            
            print(f"\n========= {algorithm} k: {k}, m:{m}, e:{e} ==========")
            if algorithm == "HCMS":
                if math.log2(m).is_integer() == False:
                    m = 2 ** math.ceil(math.log2(m))
                    print(f"m must be a power of 2: m ={m}")

            _, data_table, _, _ = client(k, m, e, database)

            data_dicts = [dict(zip(headers, row)) for row in data_table]

            for data_dict in data_dicts:
                results[algorithm].append([
                    k, m, 
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

    for algo, table in results.items():
        print(f"\nResults for {algo}")
        print(tabulate(table, headers=headers, tablefmt="grid"))


def main(step=1):
    while True:
        if step == 1:
            # Step 1: Data preprocessing
            database = input("Enter the database name: ")
            #run_data_processor(database)
            step = 2
    
        if step == 2:
            #Step 2: Calculate k and m
            k, m = calculate_k_m()

            # Step 3: Execute no privacy algorithms
            execute_no_privacy(k, m, database)

            res = input("Are you satisfied with the results? (yes/no): ")
            if res == 'yes':
                step = 3
            else:
                step = 2
        elif step == 3:
            # Step 4: Execute algorithms
            print("\nExecuting private algorithms ...")
            execute_algorithms(database, k, m)

            # Step 5: Choose an algorithm, k and m
            k = int(input("Enter the value of k: "))
            m = int(input("Enter the value of m: "))
            algorithm = input("Enter the algorithm to execute:\n1. Count-Mean Sketch\n2. Hadamard Count-Mean Sketch\n")
            res = input("Are you satisfied with the results? (yes/no): ")
            if res == 'yes':
                step = 4
                
            else:
                step = 2
        elif step == 4:
            # Step 6: Parameter fitting and execute server
            execute(database, algorithm, k, m)
            break

if __name__ == "__main__":
    main()
