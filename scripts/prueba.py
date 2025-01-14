import subprocess
import re
import argparse
import random
import pandas as pd
import os
import optuna

# Constants
ALGORITHM_PATHS = {
    1: "../src/private_count_mean/private_cms.py",
    2: "../src/private_hadamard_count_mean/private_hcms.py",
}

def function_LP(N, f_estimated, f_real, p):
    sum_error = 0
    merged = f_estimated.merge(f_real, on="Element", suffixes=("_estimated", "_real"))
    for _, row in merged.iterrows():
        sum_error += abs(row["Frequency_estimated"] - row["Frequency_real"]) ** p
    return (1 / N) * sum_error

def load_dataset(csv_filename):
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/filtered', csv_filename + '.csv'))
    df = pd.read_csv(dataset_path)
    df = df[['value']]
    unique_values = df['value'].unique().tolist()
    return unique_values

def run_command(k, m, e, data_file, algorithm_option):
    cmd = ["python3", ALGORITHM_PATHS[algorithm_option], "-k", str(k), "-m", str(m), "-e", str(e), "-d", data_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error al ejecutar el comando: {result.stderr}")
        return None
    

def real_frequency(args):
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/filtered', args.d + '.csv'))
    df = pd.read_csv(dataset_path)
    df = df[['value']]
    dataset = df['value'].tolist()
    domain = df['value'].unique().tolist()
    
    f_real = {}
    for d in domain:
        f_real[d] = dataset.count(d)
    
    df_real_frequency = pd.DataFrame(list(f_real.items()), columns=['Element', 'Frequency'])
    return df_real_frequency

def frequencies(args):
    f_estimada = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/frequencies', args.d + '_freq_estimated_cms.csv')))
    f_real = real_frequency(args)
    return f_estimada, f_real

def exponential_search(k, m, target_error, args):
    max_e = 1e6 # Maximum value of e
    e = 1 # Initial value of e
    e_prev = 0.1 # Previous value of e

    # Run the command with the initial value of e
    run_command(k, m, e, args.d, 1)
    f_estimated, f_real = frequencies(args)
    
    actual_error = function_LP(N, f_estimated, f_real, e)
    
    print("Exponential search begins ...")

    # Exponential search to find the best range of e
    while actual_error > target_error and e < max_e:
        e_prev = e
        e *= 2 # Double the value of e
        run_command(k, m, e, args.d, 1)
        f_estimated, f_real = frequencies(args)
        actual_error = function_LP(N, f_estimated, f_real, e)
    
    if e >= max_e:
        print("Error: Maximum value of e reached.")
        return e_prev
    
    print(f"Range of e: [{e_prev}, {e}]")

    print("Binary search begins ...")
    # Binary search to find the best value of e
    while abs(actual_error - target_error) > 1e-6 and e_prev < e:
        e_mid = (e + e_prev) / 2
        run_command(k, m, e_mid, args.d, 1)
        f_estimated, f_real = frequencies(args)
        actual_error = function_LP(N, f_estimated, f_real, e_mid)
        
        if actual_error > target_error:
            e_prev = e_mid
        else:
            e = e_mid
    return e

def utility_error():
    Lp = input("Enter the percentage error to reach: ")
    # estimar e DP, empezar e -> 50

    # guardar BBDD

def privacy_error(N, k, m, f_estimated, f_real, args):
    p = float(input("Enter the type of error (p): "))
    error = function_LP(N, f_estimated, f_real, p)
    print(f"Initial Privacy Error (LP): {error}")

    # Adjust the value of e to reach the desired error
    e = exponential_search(k, m, error, args)

    # Show database with the e
    run_command(k, m, e, args.d, 1)
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/privatized', args.d + '_private.csv'))
    df = pd.read_csv(dataset_path)
    print(df)

    # Ask the user if he is satisfied with the results
    option = input("Are you satisfied with the results? (y/n): ")
    if option == "n":
        privacy_error(N, k, m, f_estimated, f_real, args)
    else:
        print("Sending database to server ...")
        

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Script to find the best parameters for a given algorithm")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset to use")
    args = parser.parse_args()

    # Sketch frequency estimation
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/frequencies', args.d + '_freq_estimated_cms.csv'))
    f_estimated = pd.read_csv(dataset_path)

    # Real frequency
    f_real = real_frequency(args)
    N = f_real['Frequency'].sum()

    # Constants
    DATA_FILE = args.d
    f = 0.01 # Failure probability
    E = 0.5 # Overestimation factor
    euler = 2.71828 # Euler's number
    
    # Calculation of m and k
    k = int(1/f)
    m = int(euler/ E )
    print(f"Initial values: k = {k}, m = {m}")

    # Utility or Privacy?
    choice = input("Choose Utility or Privacy (u/p): ")

    if choice == "u":
        utility_error()
    elif choice == "p":
        privacy_error(N, k, m, f_estimated, f_real, args)
    else:
        print("Invalid choice. Please try again.")

    

