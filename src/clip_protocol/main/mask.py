import os
import sys
import optuna
import numpy as np
import pandas as pd
from tabulate import tabulate
import argparse
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from clip_protocol.utils.utils import load_setup_json, get_real_frequency, save_mask_json, display_results
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

class Mask:
    def __init__(self, privacy_level, df):
        self.k, self.m, self.e_ref, self.events_names, self.privacy_method, self.error_metric, self.error_value, self.tolerance, self.p = load_setup_json()
        self.privacy_level = privacy_level
        self.df = df

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
        
        # Pseudonimize the user column
        self.df['user'] = self.df['user'].apply(self.pseudonimize)

        print(self.df.head(10))
    

    def calculate_metrics(self, f_estimated, f_real):
        """
        Placeholder for calculating metrics based on the privacy level.
        """
        metric = 0
        m = f_real['Frequency'].sum()
        merged = f_estimated.merge(f_real, on="Element", suffixes=("_estimated", "_real"))
        if self.error_metric == "MSE":
            metric = (1 / m) * sum((row["Frequency_estimated"] - row["Frequency_real"]) ** 2 for _, row in merged.iterrows())
        elif self.error_metric == "RMSE":
            metric = ((1 / m) * sum((row["Frequency_estimated"] - row["Frequency_real"]) ** 2 for _, row in merged.iterrows())) ** 0.5
        elif self.error_metric == "Lρ Norm":
            metric = sum(abs(row["Frequency_estimated"] - row["Frequency_real"]) ** self.p for _, row in merged.iterrows()) ** (1/self.p)  
        return metric
    
    def run_command(self, e):
        """
        Runs the selected privacy algorithm with a given privacy budget `e`, `k` y `m`.

        Returns:
            tuple: Containing result, data table, error table, privatized data, and estimated frequencies.
        """
        if self.privacy_method == "PCMeS":
            coeffs, privatized_data, df_estimated = run_private_cms_client(self.k, self.m, e, self.df)
        elif self.privacy_method == "PHCMS":
            coeffs, privatized_data, df_estimated = run_private_hcms_client(self.k, self.m, e, self.df)
        
        return coeffs, privatized_data, df_estimated

    def optimize_e(self):
        """
        Optimizes the privacy parameter `ϵ` using Optuna to reach a target error.
        
        Args:
            target_error (float): Desired error value.
            p (float): Order of the Lp norm.
            metric (str): Metric type (1 = MSE, 2 = Lp norm, 3 = Percentage Error).
        
        Returns:
            tuple: Best `ϵ`, privatized data, error table, result, and data table.
        """
        def objective(trial):
            e = round(trial.suggest_float('e', 0.1, self.e_ref, step=0.1), 4)
            coeffs, privatized_data, df_estimated = self.run_command(e)

            headers=[
                "Element", "Real Frequency", "Real Percentage", 
                "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
                "Percentage Error"
            ]

            table = display_results(get_real_frequency(self.df), df_estimated)
            print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

            percentage_errors = [float(row[-1].strip('%')) for row in table]
            max_error = max(percentage_errors)

            trial.set_user_attr('e', e)
            trial.set_user_attr('hash', coeffs)
            trial.set_user_attr('privatized_data', privatized_data)

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
               
        best_e = study.best_params['e']
        coeffs = study.best_trial.user_attrs['hash']
        privatized_data = study.best_trial.user_attrs['privatized_data']
                
        return best_e, privatized_data, coeffs

    def pseudonimize(self, user_name):
        hash_object = hashlib.sha256(user_name.encode())
        return hash_object.hexdigest()[:10]
    
def run_mask(df):
    privacy_level = input("Enter the privacy level (high/medium/low): ").strip().lower()
    if privacy_level not in ["high", "medium", "low"]:
        print("Invalid privacy level. Please enter 'high', 'medium', or 'low'.")
        return
    mask_instance = Mask(privacy_level, df)
    mask_instance.filter_dataframe()
    best_e, privatized_data, coeffs = mask_instance.optimize_e()
    save_mask_json(mask_instance, best_e, coeffs, privatized_data)
    return privatized_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run privatization mask with input CSV")
    parser.add_argument("-i", type=str, required=True, help="Path to the input CSV file")
    args = parser.parse_args()
    if not os.path.isfile(args.i):
        print(f"❌ File not found: {args.i}")
        sys.exit(1)

    df_temp = pd.read_excel(args.i)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp
    run_mask(df)