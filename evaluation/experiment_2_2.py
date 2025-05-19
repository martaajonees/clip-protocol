import optuna
import pandas as pd
import os
import sys
import time
from tabulate import tabulate

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import display_results, get_real_frequency
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

def filter_dataframe(df):
    df.columns = ["user", "value"]
    return df

def run_command(e, k, m, df):
    _, _, df_estimated = run_private_hcms_client(k, m, e, df)
    
    error = compute_error_table(get_real_frequency(df), df_estimated, 2)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table


def run_experiment_2(datasets):
    k = 818
    m = 326
    e_r = 8

    headers=[
            "Element", "Real Frequency", "Real Percentage", 
            "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
            "Percentage Error"
    ]

    tables = []

    for data in datasets:
        data.columns = ["user", "value"]
        data = filter_dataframe(data)
        error, _, table = run_command(e_r, k, m, data)
        print(error)
        tables.append(table)
        print(f"Dataset size: {len(data)}")
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
    

if __name__ == "__main__":
    datasets = []
    data_path = "datasets"
    for file in os.listdir(data_path):
        if file.endswith(".xlsx"):
            filepath = os.path.join(data_path, file)
            print(f"File: {filepath}")
            df = pd.read_excel(os.path.join(data_path, file))
            datasets.append(df)

    run_experiment_2(datasets)