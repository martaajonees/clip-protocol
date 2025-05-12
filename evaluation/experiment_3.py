import optuna
import pandas as pd
import os
import sys
import math
import time
from tqdm import tqdm
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency, display_results
from clip_protocol.utils.errors import compute_error_table

from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

PRIVACY_METHOD = "PCMeS"
ERROR_METRIC = "MAE"
ERROR_VALUE = 0.05  
TOLERANCE = 0.01
P = 1.5
PRIVACY_LEVEL = "low"
E_REF = 100

def filter_dataframe(df):
    event_names = ["Participant", "AOI Name"]
    matching_columns = [col for col in event_names if col in df.columns]
    if not matching_columns:
        print("⚠️ None of the specified event names match the DataFrame columns.")
    
    df = df[matching_columns].copy()
    df.columns = ["user", "value"]

    df['value'] = df['value'].astype(str).apply(lambda x: x.strip())
    df = df[df['value'] != '-']
    df = df[df['value'].str.contains(r'\w', na=False)]
    N = len(df)

    # Filter by percentage >= 0.1%
    real_freq = get_real_frequency(df)
    real_freq_dict = dict(zip(real_freq["Element"], real_freq["Frequency"]))
    real_percent = {k: (v * 100 /N) for k, v in real_freq_dict.items()}
    valid_elements = [k for k, v in real_percent.items() if v >= 0.1]
    df = df[df["value"].isin(valid_elements)]
    
    return df, N

def run_command(e, k, m, df):
    if PRIVACY_METHOD == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif PRIVACY_METHOD == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)

    error = compute_error_table(get_real_frequency(df), df_estimated, P)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table

def optimize_k_m(df, N):

        def objective(trial):
            # Choose the event with less frequency
            real_freq = get_real_frequency(df)
            min_freq_value = real_freq['Frequency'].min()
            
            # Calculate the value of the range of m
            sobreestimation = float(min_freq_value * ERROR_VALUE) / N
            m_range = 2.718/sobreestimation

            k = trial.suggest_int("k", 10, 1000)
            
            if PRIVACY_METHOD == "PHCMS":
                min_exp = int(math.log2(m_range // 2))
                max_exp = int(math.log2(m_range))
                m_options = [2 ** i for i in range(min_exp, max_exp + 1)]
                m = trial.suggest_categorical("m", m_options)
            else:
                m = trial.suggest_int("m", m_range/2, m_range) # m cant be 1 because in the estimation m/m-1 -> 1/0
                     
            error_table, _, _ = run_command(E_REF, k, m, df)  
            error = float([v for k, v in error_table if k == ERROR_METRIC][0])

            if error <= (ERROR_VALUE * min_freq_value):
                trial.study.stop()
            
            return m
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)

        return study.best_params["k"], study.best_params["m"]

def minimize_epsilon(k, m, df):
    def objective(trial):
        e = trial.suggest_int("e", 1, E_REF)

        _, df_estimated, table = run_command(E_REF, k, m, df)

        trial.set_user_attr('table', table)
        trial.set_user_attr('real', get_real_frequency(df))
        trial.set_user_attr('estimated', df_estimated)
        table = display_results(get_real_frequency(df), df_estimated)
        percentage_errors = [float(row[-1].strip('%')) for row in table]
        max_error = max(percentage_errors)

        if max_error <= (ERROR_VALUE * 100):
            trial.study.stop()
        
        return e
    
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=100)

    return study.best_params["e"]

def optimize_e(k, m, df, e_r):

    def objective(trial):
        e = round(trial.suggest_float('e', 0.1, e_r, step=0.1), 4)
        _, _, table = run_command(e, k, m, df)

        percentage_errors = [float(row[-1].strip('%')) for row in table]
        max_error = max(percentage_errors)

        trial.set_user_attr('table', table)
        trial.set_user_attr('e', e)
        trial.set_user_attr('max_error', max_error)

        if PRIVACY_LEVEL == "high":
            objective_high = (ERROR_VALUE + TOLERANCE)*100
            objective_low = (ERROR_VALUE * 100)
        elif PRIVACY_LEVEL == "medium":
            objective_high = (ERROR_VALUE * 100)
            objective_low = (ERROR_VALUE-TOLERANCE)*100
        elif PRIVACY_LEVEL == "low":
            objective_high = (ERROR_VALUE-TOLERANCE)*100
            objective_low = 0

        if objective_high >= max_error > objective_low:
            trial.study.stop()
        
        print(f"Trial {trial.number}: e = {e}, max_error = {max_error}")
        
        return round(abs(objective_high - max_error), 4)
        

    study = optuna.create_study(direction='minimize') 
    study.optimize(objective, n_trials=20)
            
    table = study.best_trial.user_attrs['table']
    max_error = study.best_trial.user_attrs['max_error']
    e = study.best_trial.user_attrs['e']
            
    return table, max_error, e
    
def run_experiment_3(df, datasets):
    df, N = filter_dataframe(df)
    k, m = optimize_k_m(df, N)
        
    e_r = minimize_epsilon(k, m, df)

    print(f"Best k: {k}, m: {m}, e: {e_r}")
    
    tables = []
    performance_records = []

    for data in datasets:
        data_df, _ = filter_dataframe(data)
        start_time = time.time()
        table, max_error, e = optimize_e(k, m, data_df, e_r)
        end_time = time.time()
        elapsed_time = end_time - start_time
        tables.append(table)
    
        performance_records.append({
            "User": data_df["user"].iloc[0],
            "Epsilon": e,
            "Maximun Error": max_error,
            "Execution time": round(elapsed_time, 4)
        })
    
    performance_df = pd.DataFrame(performance_records)
    performance_df.to_csv("figures/epsilon_execution_results.csv", index=False)


def load_excel_with_header_check(filepath):
    try:
        df_temp = pd.read_excel(filepath, nrows=2)
        header = 1 if any(col.startswith("Unnamed") for col in df_temp.columns) else 0
        df = pd.read_excel(filepath, header=header)
        return df
    except Exception as e:
        print(f"Error al leer {filepath}: {e}")
        return None
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 3")
    parser.add_argument("-d1", type=str, required=True, help="Path to the input excel file")
    parser.add_argument("-d2", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    #data_path = "/Users/martajones/Downloads/Databases"
    data_path = args.d1
    # setup_file = "s12-event-statistics-single.xlsx"
    setup_file = args.d2
    setup_path = os.path.join(data_path, setup_file)

    setup_df = pd.read_excel(setup_path)

    if any(col.startswith("Unnamed") for col in setup_df.columns):
        setup_df = pd.read_excel(setup_path, header=1)  

    datasets = []
    dataset_lengths = []

    excel_files = [f for f in os.listdir(data_path) if f.endswith(".xlsx") and f != setup_file]
    full_paths = [os.path.join(data_path, f) for f in excel_files]

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_file = {executor.submit(load_excel_with_header_check, path): path for path in full_paths}
        for future in tqdm(as_completed(future_to_file), total=len(full_paths), desc="Cargando archivos"):
            df = future.result()
            if df is not None and not df.empty:
                datasets.append(df)
                dataset_lengths.append(len(df))
            else:
                print(f"⚠️ Archivo inválido o vacío: {future_to_file[future]}")
    

    run_experiment_3(setup_df, datasets)