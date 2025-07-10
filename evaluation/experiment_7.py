import optuna
import pandas as pd
import os
import sys
import numpy as np
import time
from rich.progress import Progress
from tqdm import tqdm
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency, display_results, load_setup_json, rebuild_hash_functions
from clip_protocol.utils.errors import compute_error_table

from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client


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
    
    return df

def run_command(e, k, m, df, privacy_method):
    if privacy_method == "PCMeS":
        coeffs, privatized_data, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        coeffs, privatized_data, df_estimated = run_private_hcms_client(k, m, e, df)

    error = compute_error_table(get_real_frequency(df), df_estimated, 1.5)
    table = display_results(get_real_frequency(df), df_estimated)
    return coeffs, table, privatized_data

def optimize_e(k, m, df, e_r, privacy_level, error_value, tolerance, privacy_method, n_trials):
    matching_trial = {"trial": None}
    def objective(trial):
        e = round(trial.suggest_float('e', 0.1, e_r, step=0.1), 4)
        coeffs, table, privatized_data = run_command(e, k, m, df, privacy_method)

        percentage_errors = [float(row[-1].strip('%')) for row in table]
        max_error = max(percentage_errors)

        trial.set_user_attr('privatized_data', privatized_data)
        trial.set_user_attr('table', table)
        trial.set_user_attr('hash', coeffs)
        trial.set_user_attr('e', e)
        trial.set_user_attr('max_error', max_error)
        print(f"Trial: e = {e}, max_error = {max_error}")

        if privacy_level == "high":
            objective_high = (error_value + tolerance)*100
            objective_low = (error_value-tolerance)*100
        elif privacy_level == "low":
            objective_high = (error_value-tolerance)*100
            objective_low = 0

        if objective_high >= max_error > objective_low:
            matching_trial["trial"] = trial
            trial.study.stop()
        
        if max_error > objective_high:
            return float("inf")
        
        return round(abs(objective_high - max_error), 4)
        

    study = optuna.create_study(direction='minimize') 
    study.optimize(objective, n_trials=20)

    final_trial = matching_trial["trial"] or study.best_trial
            
    table = final_trial.user_attrs['table']
    max_error = final_trial.user_attrs['max_error']
    e = final_trial.user_attrs['e']
    coeffs = final_trial.user_attrs['hash']
    privatized_data = final_trial.user_attrs['privatized_data']
    privatized_data = pd.DataFrame(privatized_data, columns=["0", "1", "2"])
    return table, max_error, e, privatized_data, coeffs

def measure_size_on_disk(df, prefix):
    temp_path = f"temp_{prefix}.csv"
    df = pd.DataFrame(df)
    df.to_csv(temp_path, index=False)
    size_on_disk = os.path.getsize(temp_path)
    os.remove(temp_path)
    return size_on_disk

# Agregation
def update_sketch_matrix(M, k, e, privacy_method, data_point):
    """Updates the sketch matrix based on the privatized data."""
    if privacy_method == "PCMeS":
        v, j = data_point
        v = np.array(v)
        c_e = (np.exp(e / 2) + 1) / (np.exp(e / 2) - 1)
        x = k * ((c_e / 2) * v + (1 / 2) * np.ones_like(v))
        M[j, :] += x
    elif privacy_method == "PHCMS":
        w, j, l = data_point
        c_e = (np.exp(e / 2) + 1) / (np.exp(e / 2) - 1)
        x = k * c_e * w
        M[j, l] += x
    return M

def compute_data(user_data, privacy_method, k, m, e):
    M = np.zeros((k, m)) # Sketch matrix empty
    with Progress() as progress:
        task = progress.add_task("[cyan]Updating sketch matrix", total=len(user_data))
        for _, row in user_data.iterrows(): # Iterate over the rows of the user data
                if privacy_method == "PCMeS":
                    #v = np.array([int(x) for x in row["0"].split()])
                    v = np.array(row["0"])
                    data = (v, int(row["1"]))
                elif privacy_method == "PHCMS":
                    data = (row["0"], row["1"], row["2"])
                M = update_sketch_matrix(M, k, e, privacy_method, data)
                progress.update(task, advance=1)
            
    user_id = user_data["2"].iloc[0]
    return user_id, {"M": M.tolist(), "N": len(user_data)}

def agregate_per_user(private_dataset, privacy_method, k, m, e):
    users = private_dataset["2"].unique() # List of all users
    user_groups = [private_dataset[private_dataset["2"] == user] for user in users] # List of sketches for each user
    sketch_by_user = {}

    for i in range(len(users)):
        user_id, sketch = compute_data(user_groups[i], privacy_method, k, m, e)
        sketch_by_user[user_id] = sketch

    return sketch_by_user

# Estimation
def estimate_element(d, M, N, m, k, hashes):
    """Estimates the frequency of an element in the dataset."""
    return (m / (m - 1)) * (1 / k * np.sum([M[i, hashes[i](d)] for i in range(k)]) - N / m)

def query_all_users_event(event, sketch_by_user, m, k, hashes):
    print(f"\n📊 Estimated frequency of '{event}' per user:\n")
    estimates = {}
    for user_id, user_data in sketch_by_user.items():
        M = np.array(user_data["M"])
        N = user_data["N"]
        est = estimate_element(event, M, N, m, k, hashes)
        if est < 0:
            est = 0
        estimates[user_id] = est
        print(f"🧑 User {user_id}: {est:.4f}")
    return estimates
    
def run_experiment_7(datasets, privatized_path):
    k, m,  e_r, n_trials, _,  privacy_method,  _,  error_value,  tolerance,  _ = load_setup_json()
    privacy_level = "low"
    privacy_method = "PCMeS"
    k = 841
    m = 41356
    e_r = 16
    error_value = 0.04
    tolerance = 0.01
    
    all_estimates = []
    performance = []
    for data in datasets:
        data_df = filter_dataframe(data)

        # Mask
        start_time = time.time()
        _, max_error, e, privatized_data, coeffs = optimize_e(k, m, data_df, e_r, privacy_level, error_value, tolerance, privacy_method, n_trials)
        if error_value + tolerance <= max_error:
            print(f"🔍 Columnas del DataFrame privatized_data: {privatized_data.columns.tolist()}")
            end_time = time.time()
            hash_functions = rebuild_hash_functions(coeffs)

            performance.append({
                    "User": data_df["user"].iloc[0],
                    "Epsilon": e,
                    "Maximun Error": max_error,
                    "Execution time": round(end_time - start_time, 4)
                })
            
            # Agregation
            sketch_by_user = agregate_per_user(privatized_data, privacy_method, k, m, e)
            
            # Estimation
            estimate_events = {"AOI 001", "AOI 002", "AOI 003"}
            for event in estimate_events:
                user_estimates = query_all_users_event(event, sketch_by_user, m, k, hash_functions)
                for user_id, est in user_estimates.items():
                    all_estimates.append({
                        "data": data_df["user"].iloc[0],
                        "user": user_id,
                        "event": event,
                        "estimated_frequency": est,
                    })

    # Save results
    csv_path = os.path.join(privatized_path, "estimates.csv")
    df = pd.DataFrame(all_estimates)
    df.to_csv(csv_path, index=False)
    print(f"📄 Estimates also saved to: {csv_path}")

    csv_path = os.path.join(privatized_path, "experimet_7_results.csv")
    df = pd.DataFrame(performance)
    df.to_csv(csv_path, index=False)
    print(f"📄 Performance also saved to: {csv_path}")

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
    parser.add_argument("-d2", type=str, required=True, help="Path save privatized data")
    args = parser.parse_args()

    data_path = args.d1 # folder
    privatized_path = args.d2 # folder

    CACHE_PATH = os.path.join(data_path, "cached_datasets.pkl")
    if os.path.exists(CACHE_PATH):
        print("✅ Cargando datasets desde caché...")
        with open(CACHE_PATH, "rb") as f:
            datasets = pickle.load(f)

    else:
        print("📥 Procesando archivos Excel...")
        datasets = []
        dataset_lengths = []

        excel_files = [f for f in os.listdir(data_path) if f.endswith(".xlsx")]
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
        
        with open(CACHE_PATH, "wb") as f:
            pickle.dump(datasets, f)
            print(f"💾 Datasets guardados en caché: {CACHE_PATH}")
    

    run_experiment_7(datasets, privatized_path)