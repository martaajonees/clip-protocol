import os
import importlib.util
import pandas as pd

# Importing CMS functions
from private_count_mean.private_cms_server import run_private_cms_server
from private_count_mean.private_cms_client import run_private_cms_client
from private_count_mean.cms_client import run_cms_client

# Importing data preprocessing functions
from scripts.preprocess import run_data_processor
from scripts.parameter_fitting import run_parameter_fitting

# Importing CS functions
from private_count_sketch.private_cs_server import run_private_cs_server
from private_count_sketch.private_cs_client import run_private_cs_client
from private_count_sketch.cs_client import run_cs_client


# Importing HCMS functions
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client
from private_hadamard_count_mean.private_hcms_server import run_private_hcms_server

def execute_client(database, algorithm):
    f = float(input("Enter the failure probability: "))
    E = float(input("Enter the overestimation factor: "))

    k = int(1 / f)
    m = int(2.71828 / E )

    print(f"k={k}, m={m}")
    print(f"Space complexity: {k*m}")
    
    if algorithm == '1':
        run_cms_client(k, m, database)
    elif algorithm == '2':
        run_cs_client(k, m, database)
    elif algorithm == '3':
        if math.log2(m).is_integer() == False:
            m = 2 ** math.ceil(math.log2(m))
            print("m must be a power of 2: m ={m}")
        run_cms_client(k, m, database)

    error_table = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/error_tables', 'errors_table.csv'))
    print(pd.read_csv(error_table))

    choice = input("Are you satisfied with k and m? (yes/no): ")
    if choice == 'no':
        execute_client(database, algorithm)
    return k, m, f, E
            

def execute(database, algorithm):
    print("\nExecuting client ...")
    k, m, f, E = execute_client(database, algorithm)

    print("\nExecuting personalized privacy ...")
    e, result = run_parameter_fitting(database, f, E, algorithm)

    H = result["H"]
    hashes = result["hashes"]
    G = result["G"]

    print("\nExecuting server ...")
    if algorithm == '1':
        run_private_cms_server(k, m, e, database, H)
    elif algorithm == '2':
        run_private_cs_server(k, m, e, database, H, G)
    elif algorithm == '3':
        run_private_hcms_server(k, m, e, database, hashes)

    print("\nProcess done and results saved.")

if __name__ == "__main__":
    print("Executing preprocessing ...")
    database = input("Enter the database name: ")
    run_data_processor(database)

    algorithm = input("Which algorithm do you want to execute?:\n1. Count-Mean Sketch\n2. Count Sketch\n3. Hadamard Count-Mean Sketch\n")
    
    execute(database, algorithm)
