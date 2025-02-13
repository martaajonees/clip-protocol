import os
import importlib.util
import pandas as pd

from private_count_mean.private_cms_server import run_private_cms_server
from private_count_mean.private_cms_client import run_private_cms_client
from scripts.preprocess import run_data_processor
from private_count_mean.cms_client import run_cms_client
from scripts.parameter_fitting import run_parameter_fitting

def execute_client(database):
    f = float(input("Enter the failure probability: "))
    E = float(input("Enter the overestimation factor: "))

    k = int(1 / f)
    m = int(2.71828 / E )

    print(f"k={k}, m={m}")
    print(f"Space complexity: {k*m}")
    
    run_cms_client(k, m, database)

    error_table = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/error_tables', 'errors_table.csv'))
    print(pd.read_csv(error_table))

    choice = input("Are you satisfied with k and m? (yes/no): ")
    if choice == 'no':
        execute_client()
    return k, m, f, E
            

def execute(database):
    print("\nExecuting client ...")
    k, m, f, E = execute_client(database)

    print("\nExecuting personalized privacy ...")
    e, H = run_parameter_fitting(database, f, E)

    print("\nExecuting server ...")
    run_private_cms_server(k, m, e, database, H)

    print("\nProcess done and results saved.")

if __name__ == "__main__":
    print("Executing preprocessing ...")
    database = input("Enter the database name: ")
    run_data_processor(database)
    
    execute(database)
