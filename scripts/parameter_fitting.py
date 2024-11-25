import subprocess
import re
import matplotlib.pyplot as plt

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

# Find the best parameters for a given algorithm
def find_best_parameters(data_file):
    best_params = {"-k": 1, "-m": 32, "-e": 8}
    best_error = float('inf')

    # Range of values for each parameter
    k_values = [1, 2, 3, 4, 5]
    m_values = [32, 64, 128, 256, 512]
    e_values = [3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]

    # Adjust parameters
    for k in k_values:
        for m in m_values:
            for e in e_values:
                # Build the command with all parameters
                cmd = ["python3","../external/DP-Sketching-Algorithms/Private Count Mean/private_cms.py", 
                    "-k", str(k),
                    "-m", str(m),
                    "-e", str(e),
                    "-d", data_file
                ]
                print(f"Running parameters: -k {k}, -m {m}, -e {e}")
                
                # Run the command
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error al ejecutar el comando: {cmd}")
                    print(f"Salida de error: {result.stderr}")
                    continue
                plt.close()  # Close the plot window

                # Analyse the output
                error_porcentual, frecuencias_negativas = parse_results(result.stdout)
                if not frecuencias_negativas and error_porcentual < best_error:
                    best_error = error_porcentual
                    best_params = {"-k": k, "-m": m, "-e": e}
    return best_params, best_error

if __name__ == "__main__":
    data_file = "filtrado2"
    best_params, best_error = find_best_parameters(data_file)
    print(f"Mejores parámetros: {best_params}")
    print(f"Error porcentual más bajo: {best_error:.2f}")
