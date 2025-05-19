import optuna
import pandas as pd
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import load_setup_json, display_results, get_real_frequency
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

privacy_method = "PCMeS" 

def filter_dataframe(df):
    df.columns = ["user", "value"]
    return df

def run_command(e, k, m, df):
    if privacy_method == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)
    
    error = compute_error_table(get_real_frequency(df), df_estimated, 2)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table

def optimize_e(k, m, df, e_r, privacy_level, error_value, tolerance):
    matching_trial = {"trial": None}
    def objective(trial):
        e = round(trial.suggest_float('e', 0.1, e_r, step=0.1), 4)
        _, _, table = run_command(e, k, m, df)

        percentage_errors = [float(row[-1].strip('%')) for row in table]
        max_error = max(percentage_errors)

        trial.set_user_attr('table', table)
        trial.set_user_attr('e', e)
        trial.set_user_attr('max_error', max_error)

        if privacy_level == "high":
            objective_high = (error_value + tolerance)*100
            objective_low = (error_value-tolerance)*100
        elif privacy_level == "low":
            objective_high = (error_value-tolerance)*100
            objective_low = 0

        if objective_high >= max_error > objective_low:
            matching_trial["trial"] = trial
            trial.study.stop()
        print("Error: ", max_error)
        # if max_error > objective_high:
        #     return float("inf")
        
        return round(abs(objective_high - max_error), 4)
        

    study = optuna.create_study(direction='minimize') 
    study.optimize(objective, n_trials=20)

    final_trial = matching_trial["trial"] or study.best_trial
            
    table = final_trial.user_attrs['table']
    max_error = final_trial.user_attrs['max_error']
    e = final_trial.user_attrs['e']
            
    return table, max_error, e


def run_experiment_2(datasets):
    k, m,  e_r, _, _,  _,  _,  error_value,  tolerance,  _ = load_setup_json()
    privacy_level = "high"
    # k = 818
    # m = 286
    # e_r = 8

    tables = []
    performance_records = []
    all_individual_aoi_errors = []

    for data in datasets:
        data.columns = ["user", "value"]
        data = filter_dataframe(data)
        start_time = time.time()
        table, max_error, e = optimize_e(k, m, data, e_r, privacy_level, error_value, tolerance)
        end_time = time.time()
        elapsed_time = end_time - start_time
        tables.append(table)

        performance_records.append({
            "e": e,
            "max error": max_error,
            "dataset_size": len(data),
            "execution_time_seconds": round(elapsed_time, 4)
        })

        for row in table:
            aoi = row[0]
            percent_error = float(row[-1].strip('%'))
            all_individual_aoi_errors.append({
                "dataset": f"dataset_{len(data)}",
                "AOI": aoi,
                "percent_error": percent_error
            })
    
    performance_df = pd.DataFrame(performance_records)
    performance_df.to_csv("figures/table_experiment_2-phcms.csv", index=False)

    aoi_errors_df = pd.DataFrame(all_individual_aoi_errors)
    aoi_errors_df.to_csv("figures/individual_aoi_errors_exp_2-phcms.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 3")
    parser.add_argument("-d1", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()

    data_path = args.d1 # folder

    datasets = []
    for file in os.listdir(data_path):
        if file.endswith(".xlsx"):
            filepath = os.path.join(data_path, file)
            print(f"File: {filepath}")
            df = pd.read_excel(os.path.join(data_path, file))
            datasets.append(df)

    run_experiment_2(datasets)