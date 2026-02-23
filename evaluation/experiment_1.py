import pandas as pd
import os
import sys
import argparse

# Experimento 1. Influencia de epsilon en PCMeS y PHCMeS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

def filter_dataframe(df):
    df.columns = ["user", "value"]
    N = len(df)
    return df, N

def run_command(e, k, m, df, privacy_method):
    if privacy_method == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)

    return compute_error_table(get_real_frequency(df), df_estimated, 2), df_estimated

def run_experiment1(df, privacy_method):
    k = int(input("🔑 Enter k value: "))
    m = int(input("🔢 Enter m value: "))
    df, _ = filter_dataframe(df)
    error_history = {}

    epsilons = [round(e, 1) for e in list(reversed([x * 0.5 for x in range(1, 21)])) + [0.4, 0.3, 0.2, 0.1]]

    for eps in epsilons:
        table, _ = run_command(eps, k, m, df, privacy_method)
        for metric, val in table:
            error_history.setdefault(metric, []).append((eps, val))
    
    df = pd.DataFrame(error_history)
    df.to_csv(f"table_experiment_1_{privacy_method}.csv", index=False)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 1")
    parser.add_argument("-f", required=True, help="Path to input Excel file")
    args = parser.parse_args()
    
    distribution = input(" Enter the distribution 1/2/3/4: ")
    
    pattern = f"SynLog-5000-d{distribution}"
    matching_files = [f for f in os.listdir(args.f) if pattern in f and f.endswith(".xlsx")]

    file_path = os.path.join(args.f, matching_files[0])
    print(f"📂 Usando archivo: {file_path}")

    header = 1 if "Unnamed" in pd.read_excel(file_path, nrows=1).columns[0] else 0
    df = pd.read_excel(file_path, header=header)

    for method in ["PCMeS", "PHCMS"]:
        print(f"Running experiment with {method}...")
        run_experiment1(df, method)