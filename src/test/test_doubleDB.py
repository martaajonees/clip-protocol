

import os
import sys
import pandas as pd


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from private_count_mean.private_cms_client import run_private_cms_client
from scripts.preprocess import run_data_processor

def display_error_table():
        # Go to data/error_tables and show the error table
        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/error_tables'))
        error_table_path = os.path.join(dir, 'errors_table.csv')
        if os.path.exists(error_table_path):
            error_table = pd.read_csv(error_table_path)
            print(error_table)
        else:
            print(f"Error: El archivo no existe en la ruta especificada: {error_table_path}")

def doubleDB(file_name):
    # Load the dataset
    df = pd.read_csv(f'../../data/filtered/{file_name}_filtered.csv')
    df_doubled = pd.concat([df, df], ignore_index=True)

    doubled_file_name = f'../../data/filtered/{file_name}_doubled_filtered.csv'
    df_doubled.to_csv(f"{doubled_file_name}", index=False)
    print(f"Database doubled and saved as {doubled_file_name}")
    return f"{file_name}_doubled"

def run_double_test():

    file_name = "dataOviedo"

    print(" ========= Original DB ===========")
    run_private_cms_client(100, 543, 11, file_name)
    display_error_table()

    # Transform the raw dataset 
    file_name = doubleDB(file_name)


    print(" ========= Double DB ===========")
    run_private_cms_client(100, 543, 11, file_name)

    # Display the error table
    display_error_table()

if __name__ == '__main__':
    run_double_test()