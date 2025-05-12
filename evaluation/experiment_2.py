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

class Experiment2:
    def __init__(self, df):
        self.df = df
        self.events_names = ["user_id", "aoi_hit"]
        self.privacy_method = "PCMeS"
        self.error_metric = "MSE"
        self.error_value = 0.05
        self.tolerance = 0.01
        self.p = 1.5
        self.privacy_level = "low"

        self.e_ref = 0
        self.found_best_values = False
        self.N = len(self.df)

    def filter_dataframe(self):
        self.df.columns = ["user", "value"]
        self.N = len(self.df)
        return self.df
    
    def run_command(self, e, k, m, df):
        if self.privacy_method == "PCMeS":
            _, _, df_estimated = run_private_cms_client(k, m, e, df)
        elif self.privacy_method == "PHCMS":
            _, _, df_estimated = run_private_hcms_client(k, m, e, df)
    
        error = compute_error_table(self.real_freq, df_estimated, self.p)
        table = display_results(self.real_freq, df_estimated)
        return error, df_estimated, table
    
    def optimize_k_m(self, er=150):
        self.e_ref = er

        def objective(trial):
            # Choose the event with less frequency
            self.real_freq = get_real_frequency(self.df)
            min_freq_value = self.real_freq['Frequency'].min()
            
            # Calculate the value of the range of m
            sobreestimation = float(min_freq_value * self.error_value) / self.N
            m_range = 2.718/sobreestimation

            k = trial.suggest_int("k", 10, 1000)
            
            if self.privacy_method == "PHCMS":
                min_exp = int(math.log2(m_range // 2))
                max_exp = int(math.log2(m_range))
                m_options = [2 ** i for i in range(min_exp, max_exp + 1)]
                m = trial.suggest_categorical("m", m_options)
            else:
                m = trial.suggest_int("m", m_range/2, m_range) # m cant be 1 because in the estimation m/m-1 -> 1/0

                     
            error_table, _, _ = self.run_command(self.e_ref, k, m, self.df)  
            error = float([v for k, v in error_table if k == self.error_metric][0])


            if error <= (self.error_value * min_freq_value):
                self.found_best_values = True
                trial.study.stop()
            
            return m
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)

        return study.best_params["k"], study.best_params["m"], er
    
    def minimize_epsilon(self, k, m, df):
        def objective(trial):
            e = trial.suggest_int("e", 1, self.e_ref)

            _, df_estimated, table = self.run_command(self.e_ref, k, m, df)

            trial.set_user_attr('table', table)
            trial.set_user_attr('real', get_real_frequency(self.df))
            trial.set_user_attr('estimated', df_estimated)
            table = display_results(get_real_frequency(self.df), df_estimated)
            percentage_errors = [float(row[-1].strip('%')) for row in table]
            max_error = max(percentage_errors)

            if max_error <= (self.error_value * 100):
                trial.study.stop()
            
            return e
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)

        return study.best_params["e"]
    
    def optimize_e(self, k, m, df, e_r):
        def objective(trial):
            e = round(trial.suggest_float('e', 0.1, e_r, step=0.1), 4)
            _, _, table = self.run_command(e, k, m, df)

            percentage_errors = [float(row[-1].strip('%')) for row in table]
            max_error = max(percentage_errors)

            trial.set_user_attr('table', table)
            trial.set_user_attr('e', e)
            trial.set_user_attr('max_error', max_error)

            if self.privacy_level == "high":
                objective_high = (self.error_value + self.tolerance)*100
                objective_low = (self.error_value * 100)
            elif self.privacy_level == "medium":
                objective_high = (self.error_value * 100)
                objective_low = (self.error_value-self.tolerance)*100
            elif self.privacy_level == "low":
                objective_high = (self.error_value-self.tolerance)*100
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
    experiment = Experiment2(df)
    df = experiment.filter_dataframe()

    while not experiment.found_best_values:
        experiment.k, experiment.m, experiment.e = experiment.optimize_k_m()
        if not experiment.found_best_values:
            experiment.e_ref += 50
    
    e_r = experiment.minimize_epsilon(experiment.k, experiment.m, df)
    
    tables = []
    dataset_sizes = [len(d) for d in datasets]
    performance_records = []

    for data in datasets:
        data.columns = ["user", "value"]
        start_time = time.time()
        table, max_error = experiment.optimize_e(experiment.k, experiment.m, df, e_r)
        end_time = time.time()
        elapsed_time = end_time - start_time
        tables.append(table)
    
        performance_records.append({
            "max error": max_error,
            "dataset_size": len(data),
            "execution_time_seconds": round(elapsed_time, 4)
        })
    
    performance_df = pd.DataFrame(performance_records)
    performance_df.to_csv("figures/epsilon_execution_results.csv", index=False)
    plot_relative_errors_multiple_tables(tables, dataset_sizes)

def plot_relative_errors_multiple_tables(tables, dataset_sizes, output_path="figures/aoi_relative_errors.tex"):
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Extraer labels y errores
    all_errors = {}  # {AOI_label: {dataset_size: error_value}}

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