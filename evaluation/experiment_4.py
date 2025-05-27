import pandas as pd
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency, display_results
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

def filter_dataframe(df):
    df.columns = ["user", "value"]
    return df

def run_command(e, k, m, df, privacy_method):
    if privacy_method == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)

    error = compute_error_table(get_real_frequency(df), df_estimated, 1.5)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table

def run_experiment_4(datasets, params):
    for distribution, df in datasets.items():
        k = params["k"]
        m = params["m"]
        e = params["e"]

        df.columns = ["user", "value"]
        df = filter_dataframe(df)

        for method in ["PCMeS", "PHCMS"]:
            print(f"🔍 Ejecutando {method} en distribución {distribution}...")
            error_by_aoi, _, _ = run_command(e, k, m, df, method)

            path_individual = f"figures/experimet_4_d{distribution}_{method}.csv"
            error_by_aoi.to_csv(path_individual, index=False)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run scalability experiment")
    parser.add_argument("-f", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    data_path = args.f # folder

    params_path = os.path.join(os.path.dirname(__file__), "figures", "experiment_4_params.json")
    with open(params_path, 'r') as f:
        params = json.load(f)
    
    distributions = ["1", "2", "3", "4"]

    datasets = {}
    for distribution in distributions:
        pattern = f"aoi-hits-d{distribution}-5000"
        file_path = os.path.join(args.f, pattern + ".xlsx")
        header = 1 if "Unnamed" in pd.read_excel(file_path, nrows=1).columns[0] else 0
        df = pd.read_excel(file_path, header=header)
        datasets[distribution] = df  
    
    run_experiment_4(datasets, params)