import optuna
import pandas as pd
import numpy as np
import os
import sys
from tabulate import tabulate
import argparse
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from clip_protocol.utils.utils import save_setup_json, get_real_frequency, display_results
from clip_protocol.utils.errors import compute_error_table

from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client
class Setup:
    def __init__(self, df):
        self.df = df
        
        self.events_names, self.privacy_method, self.error_metric, self.error_value, self.tolerance = self.ask_values()
        self.e_ref = 0
        self.found_best_values = False
        self.N = len(self.df)

    def ask_values(self):
        """
        Prompt the user to input configuration parameters.
        Returns:
            tuple: Contains events_names (list), privacy_method (str), 
                   error_metric (str), error (float), tolerance (float)
        """
        print("Please enter the values for the parameters:")

        print(self.df.columns)
        events_inputs = input("🔹 Event columns names (comma-separated): ")
        events_names = [e.strip() for e in events_inputs.split(",") if e.strip()]

        privacy_options = {"1": "PCMeS", "2": "PHCMS"}
        privacy_method = self._ask_option("🔹 Privacy method", privacy_options)
        
        error_metric_options = { "1": "MSE", "2": "RMSE","3": "Lρ Norm"}
        error_metric = self._ask_option("🔹 Error metric", error_metric_options)
        if error_metric == "Lρ Norm":
            self.p = int(input("🔹 ρ value: "))
        
        error_value = float(input("🔹 Error value: "))
        tolerance = float(input("🔹 Tolerance: "))

        return events_names, privacy_method, error_metric, error_value, tolerance
    
    def _ask_option(self, prompt, options):
        """Prompt the user to input configuration parameters."""
        print(f"{prompt}:\n" + "\n".join([f"\t {k}. {v}" for k, v in options.items()]))
        choice = input(f"\t Enter option ({'/'.join(options)}): ").strip()
        while choice not in options:
            choice = input("Invalid option. Try again: ").strip()
        return options[choice]
    
    def filter_dataframe(self):
        """
        Filters the DataFrame to keep only the columns specified,
        if they exist in the DataFrame.
        Returns:
            pd.DataFrame: Filtered DataFrame with selected columns.
        """
        matching_columns = [col for col in self.events_names if col in self.df.columns]
        if not matching_columns:
            print("⚠️ None of the specified event names match the DataFrame columns.")
        
        self.df = self.df[matching_columns].copy()
        self.df.columns = ["user", "value"]

        self.df['value'] = self.df['value'].astype(str).apply(lambda x: x.strip())
        self.df = self.df[self.df['value'] != '-']
        self.df = self.df[self.df['value'].str.contains(r'\w', na=False)]
        self.N = len(self.df)
    
    def run_command(self, e, k, m):
        """
        Runs the selected privacy algorithm with a given privacy budget `e`, `k` y `m`.

        Returns:
            tuple: Containing result, data table, error table, privatized data, and estimated frequencies.
        """
        if self.privacy_method == "PCMeS":
            _, _, df_estimated = run_private_cms_client(k, m, e, self.df)
        elif self.privacy_method == "PHCMS":
            _, _, df_estimated = run_private_hcms_client(k, m, e, self.df)
    
        error_table = compute_error_table(self.real_freq, df_estimated)
        return error_table, df_estimated
    
    def optimize_k_m(self, er=150):
        """
        Optimize the parameters k and m using Optuna.
        Returns:
            tuple: Contains the best k and m values found during optimization.
        """
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

                     
            error_table, _ = self.run_command(self.e_ref, k, m)
            error = float([v for k, v in error_table if k == self.error_metric][0])


            if error <= (self.error_value * min_freq_value):
                self.found_best_values = True
                trial.study.stop()
            
            return m
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)

        return study.best_params["k"], study.best_params["m"], er
    
    def minimize_epsilon(self, k, m):
        def objective(trial):
            e = trial.suggest_int("e", 1, self.e_ref)

            _, df_estimated = self.run_command(self.e_ref, k, m)

            table = display_results(get_real_frequency(self.df), df_estimated)
            percentage_errors = [float(row[-1].strip('%')) for row in table]
            max_error = max(percentage_errors)

            print(f"Max error: {max_error}")
            print(f"Error value: {self.error_value * 100}")
            if max_error <= (self.error_value * 100):
                trial.study.stop()
            
            return e
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=100)

        return study.best_params["e"]
    
    def no_privacy(self):
        headers=[
            "Element", "Real Frequency", "Real Percentage", 
            "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
            "Percentage Error"
        ]
        _, _, estimated = run_private_cms_client(self.k, self.m, self.e_ref, self.df)
        real = get_real_frequency(self.df)
        table = display_results(real, estimated)
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

def run_setup(df):
    """
    Main function to run the setup process.
    """
    df_temp = df.copy()
    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp

    setup_instance = Setup(df)
    setup_instance.filter_dataframe()

    while not setup_instance.found_best_values:
        setup_instance.k, setup_instance.m, setup_instance.e = setup_instance.optimize_k_m()
        if not setup_instance.found_best_values:
            setup_instance.e_ref += 50
    
    setup_instance.e_ref = setup_instance.minimize_epsilon(setup_instance.k, setup_instance.m)
    setup_instance.no_privacy()
    
    print(f"Optimal parameters found: k={setup_instance.k}, m={setup_instance.m}, e={setup_instance.e_ref}")
    print(f"Events: {setup_instance.events_names}")
    print(f"Privacy method: {setup_instance.privacy_method}")
    print(f"Error metric: {setup_instance.error_metric}")
    
    save_setup_json(setup_instance)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run privatization mask with input CSV")
    parser.add_argument("-i", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    if not os.path.isfile(args.i):
        print(f"❌ File not found: {args.i}")
        sys.exit(1)

    df_temp = pd.read_excel(args.i)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp

    run_setup(df)