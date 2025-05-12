import optuna
import pandas as pd
import numpy as np
import os
import sys
from tabulate import tabulate
import argparse
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client
from latex_plot_generator import generate_latex_line_plot

class Experiment1:
    def __init__(self, df):
        self.df = df
        self.events_names = ["user_id", "aoi_hit"]
        self.privacy_method = "PCMeS"
        self.error_metric = "MSE"
        self.error_value = 0.1
        self.tolerance = 0.1
        self.p = 1.5
        
        self.e_ref = 0
        self.found_best_values = False
        self.N = len(self.df)
    
    def filter_dataframe(self):
        self.df.columns = ["user", "value"]
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
    
        error_table = compute_error_table(self.real_freq, df_estimated, self.p)
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

def run_experiment1(df):
    """
    Main function to run the setup process.
    """
    experiment = Experiment1(df)
    experiment.filter_dataframe()

    k, m, er = experiment.optimize_k_m()
    print(f"---------k = {k} m = {m} ---------")

    error_history = {}

    # Run sketch with fixed k and m and vary e
    er = 10
    while er >= 0.5:
        error_table, _ = experiment.run_command(er, k, m)

        for metric, value in error_table:
            if metric not in error_history:
                error_history[metric] = []
            error_history[metric].append((er, value))

        er -= 0.5
    
    generate_latex_line_plot(error_history)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 1")
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

    run_experiment1(df)