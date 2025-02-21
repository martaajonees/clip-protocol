import subprocess
import re
import argparse
import random
import pandas as pd
import os
import optuna
import statistics

from tabulate import tabulate
import numpy as np

from private_count_mean.private_cms_client import run_private_cms_client
from private_count_sketch.private_cs_client import run_private_cs_client
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client


class PrivacyUtilityOptimizer:
    def __init__(self, dataset_name, k, m, algorithm):
        self.algorithm = algorithm
        self.dataset_name = dataset_name

        self.frequency_estimation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/frequencies', self.dataset_name + '_freq_estimated_cms.csv'))
        self.filtered_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/filtered', self.dataset_name + '_filtered.csv'))

        self.privatized_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/privatized', self.dataset_name + '_private.csv'))
        self.privatized_pickle = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/privatized', self.dataset_name + '_private.pkl'))

        self.real_frequency = self.get_real_frequency()
        self.load_frequency_estimation()
        
        self.N = self.real_frequency['Frequency'].sum()

        self.headers = headers=[ "Element", "Real Frequency", "Real Percentage", "Estimated Frequency", "Estimated Percentage", "Estimation Difference", "Percentage Error"]

        self.k = k
        self.m = m
    
    def load_frequency_estimation(self):
        self.frequency_estimation = pd.read_csv(self.frequency_estimation_path)

    def function_LP(self, f_estimated, f_real, p):
        sum_error = 0
        merged = f_estimated.merge(f_real, on="Element", suffixes=("_estimated", "_real"))
        for _, row in merged.iterrows():
            sum_error += abs(row["Frequency_estimated"] - row["Frequency_real"]) ** p
        
        return (1 / self.N) * sum_error

    def run_command(self, e):
        data_table = []
        result = {"H": None, "G": None,"hashes": None}
        if self.algorithm == '1':
            result["H"], data_table, _ = run_private_cms_client(self.k, self.m, e, self.dataset_name)
        elif self.algorithm == '2':
            result["hashes"], data_table, _ = run_private_hcms_client(self.k, self.m, e, self.dataset_name)
        
        self.load_frequency_estimation()
        return result, data_table

    def get_real_frequency(self):
        df = pd.read_csv(self.filtered_path)
        df = df[['value']]
        dataset = df['value'].tolist()
        domain = df['value'].unique().tolist()
        
        f_real = {}
        for d in domain:
            f_real[d] = dataset.count(d)
        
        df_real_frequency = pd.DataFrame(list(f_real.items()), columns=['Element', 'Frequency'])
        return df_real_frequency

    def frequencies(self):
        return self.frequency_estimation, self.get_real_frequency()

    def display_error_table(self):
        # Go to data/error_tables and show the error table
        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/error_tables'))
        error_table_path = os.path.join(dir, 'errors_table.csv')
        if os.path.exists(error_table_path):
            error_table = pd.read_csv(error_table_path)
            print(error_table)
        else:
            print(f"Error: El archivo no existe en la ruta especificada: {error_table_path}")

    def optimize_e_with_optuna(self, target_error, p):
        def objective(trial):
            e = trial.suggest_float('e', 0.01, 20, step = 0.01)
            self.run_command(e)
            self.display_error_table()
    
            actual_error = self.function_LP(self.frequency_estimation, self.get_real_frequency(), p)
            
            # Minimize the diference: LP - target_error
            return abs(actual_error - target_error)

        # Create a study object and optimize the objective function
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=30)

        best_e = study.best_params['e']

        print(f"Best value of e: {best_e}")
        print(f"Closest error (LP - target_error): {study.best_value}")
        
        return best_e

    def utility_error(self):
        Lp = float(input("Enter the percentage error to reach (Lp): "))
        p = float(input("Enter the type of error (p): "))

        # Adjust the value of e to reach the desired error
        e = self.optimize_e_with_optuna(Lp, p)

        # Show database with the e
        result, data_table = run_command(e)
        print(data_table)

        # Ask the user if he is satisfied with the results
        option = input("Are you satisfied with the results? (y/n): ")
        if option == "n":
            utility_error()
        else:
            print("Sending database to server ...")
        return e, result

    def privacy_error(self):
        from start import main
        p = float(input("Enter the type of error (p): "))
        error = self.function_LP(self.frequency_estimation, self.real_frequency, p)
        print(f"Initial Privacy Error (LP): {error}")

        while True:
            # Ask for a range for e to optimize 
            e_min = input("Enter the minimum value of e: ")
            e_max = input("Enter the maximum value of e: ")

            step = input("Enter the step value: ")

            saved_e = 0

            for e in range(int(e_min), int(e_max), int(step)):
                result, data_table = self.run_command(e)
                f_estimated, f_real = self.frequencies()
    
                error = self.function_LP(f_estimated, f_real, p)
                print(f"\nError for e = {e}: {error}")
                print(tabulate(data_table, headers=self.headers, tablefmt="grid"))

                save = input("Do you want to save this privatized values? (y/n): ")
                if save == "y":
                    saved_e = e
                    H_fav = result
                    privatized_data = pd.read_csv(self.privatized_path)
                    privatized_data.to_csv(self.privatized_path.replace('.csv', f'_fav.csv'), index=False)

                    new_pickle = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/privatized', self.dataset_name + '_private_fav.pkl'))
                    os.rename(self.privatized_pickle, new_pickle)
                    
                    
            choice = input("\n1. Change e\n2. Change k or m\n3. Continue\n Select (1, 2 or 3): ")
            if choice == "2":
                main(2)
                break
            elif choice == "3":
                break
        
        if saved_e == 0:
            e = input("Enter the value of e to use: ")
            # Show database with the e
            H_fav = self.run_command(e)
            self.display_error_table()
        else:
            print(f"Using the saved value of e: {saved_e}")

        # Ask the user if he is satisfied with the results
        option = input("Are you satisfied with the results? (y/n): ")
        if option == "n":
            self.privacy_error()
        else:
            print("\nSending database to server ...")
        return saved_e, H_fav

    def run(self):
        e = 0
        choice = input("Choose Utility or Privacy (u/p): ")
        if choice == "u":
            e, result = self.utility_error()
        elif choice == "p":
            e, result = self.privacy_error()
        else:
            print("Invalid choice. Please try again.")
        return e, result

    
def run_parameter_fitting(d, k, m, algorithm):
    optimizer = PrivacyUtilityOptimizer(d, k, m, algorithm)
    e, result = optimizer.run()
    return e, result

    

