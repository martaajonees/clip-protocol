import subprocess
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

option = {
    1: "../external/DP-Sketching-Algorithms/Private Count Mean/private_cms.py",
    2: "../external/DP-Sketching-Algorithms/Private Hadmard Count Mean/private_hcms.py",
}

# Extract metrics from the output
def parse_results(output):
    lines = output.split('\n')
    error_porcentual = None
    frecuencias_negativas = False
    for line in lines:
        if "Error porcentual" in line:
            match = re.search(r'\d+\.\d+', line)
            if match:
                error_porcentual = float(match.group(0))
        if "Frecuencias estimada" in line:
            freq_values = [float(x) for x in re.findall(r'\d+\.\d+', line)]
            if any(x < 0 for x in freq_values):
                frecuencias_negativas = True
    print(f"Error porcentual: {error_porcentual}, Frecuencias negativas: {frecuencias_negativas}")
    return error_porcentual, frecuencias_negativas

def run_command(k, m, e, data_file, algorithm_option):
    # Build the command with all parameters
    cmd = ["python3", option[algorithm_option], 
            "-k", str(k),
            "-m", str(m),
            "-e", str(e),
            "-d", data_file 
        ]
    print(f"Running parameters: -k {k}, -m {m}, -e {e}")
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None
    return parse_results(result.stdout)

# Find the best parameters for a given algorithm
def find_best_parameters(data_file, algorithm_option):
    best_params = {"-k": 1, "-m": 32, "-e": 8}
    best_error = float('inf')

    # Range of values for each parameter
    k_values = [1, 2, 3, 4, 5]
    m_values = [32, 64, 128, 256, 512]
    e_values = [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]

    with ThreadPoolExecutor() as executor:
        futures = []
        for k in k_values:
            for m in m_values:
                for e in e_values:
                    futures.append(executor.submit(run_command, k, m, e, data_file, algorithm_option))
        
        # Analyse the output
        for future in as_completed(futures):
            error_porcentual, frecuencias_negativas = future.result()
            if error_porcentual is not None and not frecuencias_negativas and error_porcentual < best_error:
                best_error = error_porcentual
                best_params = {"-k": k, "-m": m, "-e": e}
    return best_params, best_error

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Script to find the best parameters for a given algorithm")
    parser.add_argument("-d", type=str, required=True, help='Name of the dataset to use')
    parser.add_argument("-o", type=int, choices=[1, 2], required=True, help='Algorithm to use')
    
    args = parser.parse_args()

    data_file = args.d
    algorithm_option = args.o

    best_params, best_error = find_best_parameters(data_file, algorithm_option)
    print(f"Mejores parámetros: {best_params}")
    print(f"Error porcentual más bajo: {best_error:.2f}")
