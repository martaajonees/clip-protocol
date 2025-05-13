import optuna
import pandas as pd
import os
import sys
import math
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency, display_results
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client


PRIVACY_METHOD = "PHCMS"
E_REF = 150
ERROR_VALUE = 0.05
TOLERANCE = 0.01
ERROR_METRIC = "MSE"
PRIVACY_LEVEL = "low"

def filter_dataframe(df):
    df.columns = ["user", "value"]
    N = len(df)
    return df, N

def run_command(e, k, m, df):
    if PRIVACY_METHOD == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif PRIVACY_METHOD == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)

    error = compute_error_table(get_real_frequency(df), df_estimated, 1.5)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table

def optimize_k_m(df, N):
    matching_trial = {"trial": None}
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
            matching_trial["trial"] = trial
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
            objective_low = (ERROR_VALUE - TOLERANCE)*100
        elif PRIVACY_LEVEL == "low":
            objective_high = (ERROR_VALUE - TOLERANCE)*100
            objective_low = 0

        if objective_high >= max_error > objective_low:
            trial.study.stop()
        
        return abs(objective_high - max_error)

    study = optuna.create_study(direction='minimize') 
    study.optimize(objective, n_trials=20)
            
    table = study.best_trial.user_attrs['table']
    max_error = study.best_trial.user_attrs['max_error']
            
    return table, max_error


def run_experiment_2(df, datasets):
    df, N = filter_dataframe(df)

    k, m = optimize_k_m(df, N)
    
    e_r = minimize_epsilon(k, m, df)
    
    tables = []
    dataset_sizes = [len(d) for d in datasets]
    performance_records = []

    for data in datasets:
        data.columns = ["user", "value"]
        start_time = time.time()
        table, max_error = optimize_e(k, m, df, e_r)
        end_time = time.time()
        elapsed_time = end_time - start_time
        tables.append(table)
    
        performance_records.append({
            "method": PRIVACY_METHOD,
            "max error": max_error,
            "dataset_size": len(data),
            "execution_time_seconds": round(elapsed_time, 4)
        })
    
    performance_df = pd.DataFrame(performance_records)
    performance_df.to_csv("figures/epsilon_execution_results.csv", index=False)
    plot_relative_errors_multiple_tables(tables, dataset_sizes)

if __name__ == "__main__":
    datasets = []
    data_path = "datasets"

    for file in os.listdir(data_path):
        if file.endswith(".xlsx"):
            filepath = os.path.join(data_path, file)
            print(f"File: {filepath}")
            df = pd.read_excel(os.path.join(data_path, file))
            datasets.append(df)

    run_experiment_2(datasets[3], datasets)

    

def plot_relative_errors_multiple_tables(tables, dataset_sizes, output_path="figures/aoi_relative_errors.tex"):
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    all_errors = {}  
    for table, size in zip(tables, dataset_sizes):
        for row in table:
            aoi_index = row[0].split("_")[-1]
            aoi_label = f"$AOI_{{{aoi_index}}}$"
            error_percent = float(row[-1].strip('%'))
            if aoi_label not in all_errors:
                all_errors[aoi_label] = {}
            all_errors[aoi_label][size] = error_percent

    # Generar código TikZ
    tikz_lines = [
        r"\begin{figure}[h]",
        r"\centering",
        r"\begin{tikzpicture}",
        r"\begin{axis}[",
        r"    ybar,",
        r"    bar width=10pt,",
        r"    ylabel={Error porcentual (\%)},",
        r"    xlabel={Áreas de Interés},",
        r"    symbolic x coords={" + ", ".join(all_errors.keys()) + "},",
        r"    xtick=data,",
        r"    x tick label style={rotate=45, anchor=east},",
        r"    ymin=0,",
        r"    enlarge x limits=0.15,",
        r"    legend style={at={(0.5,-0.2)}, anchor=north,legend columns=-1},",
        r"    legend cell align={left}",
        r"]"
    ]

    # Añadir un \addplot por cada dataset
    for size in dataset_sizes:
        tikz_lines.append(r"\addplot coordinates {")
        for aoi_label in all_errors:
            value = all_errors[aoi_label].get(size, 0)
            tikz_lines.append(f"({aoi_label}, {value})")
        tikz_lines.append("};")

    legend_entries = [f"{size} muestras" for size in dataset_sizes]
    tikz_lines.append(r"\legend{" + ", ".join(legend_entries) + "}")
    tikz_lines.append(r"\end{axis}")
    tikz_lines.append(r"\end{tikzpicture}")
    tikz_lines.append(r"\caption{Errores porcentuales por AOI en distintos tamaños de dataset}")
    tikz_lines.append(r"\end{figure}")

    with open(output_path, "w") as f:
        f.write("\n".join(tikz_lines))

    print(f"Gráfico LaTeX generado en: {output_path}")
        

