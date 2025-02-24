import pandas as pd
import os
import optuna

from tabulate import tabulate
import numpy as np

from private_count_mean.private_cms_client import run_private_cms_client
from private_count_sketch.private_cs_client import run_private_cs_client
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client


class PrivacyUtilityOptimizer:
    def __init__(self, dataset_name, k, m, algorithm):
        self.algorithm = algorithm
        self.dataset_name = dataset_name
        self.k = k
        self.m = m

        self.frequency_estimation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/frequencies', self.dataset_name + '_freq_estimated_cms.csv'))
        self.filtered_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/filtered', self.dataset_name + '_filtered.csv'))

        self.real_frequency = self.get_real_frequency()
        self.load_frequency_estimation()
        
        self.N = self.real_frequency['Frequency'].sum()

        self.headers = headers=[ "Element", "Real Frequency", "Real Percentage", "Estimated Frequency", "Estimated Percentage", "Estimation Difference", "Percentage Error"]
    
    def load_frequency_estimation(self):
        self.frequency_estimation = pd.read_csv(self.frequency_estimation_path)

    def function_LP(self, f_estimated, f_real, p):
        merged = f_estimated.merge(f_real, on="Element", suffixes=("_estimated", "_real"))
        return (1 / self.N) * sum(abs(row["Frequency_estimated"] - row["Frequency_real"]) ** p for _, row in merged.iterrows())

    def run_command(self, e):
        result = {"H": None, "G": None,"hashes": None}
        if self.algorithm == '1':
            result["H"], data_table, error_table, privatized_data = run_private_cms_client(self.k, self.m, e, self.dataset_name)
        elif self.algorithm == '2':
            result["hashes"], data_table, error_table, privatized_data= run_private_hcms_client(self.k, self.m, e, self.dataset_name)
        
        self.load_frequency_estimation()
        return result, data_table, error_table, privatized_data

    def get_real_frequency(self):
        df = pd.read_csv(self.filtered_path)
        df = df[['value']]
        count = df['value'].value_counts().reset_index()
        return count.rename(columns={'value': 'Element', 'count': 'Frequency'})

    def frequencies(self):
        return self.frequency_estimation, self.get_real_frequency()

    def optimize_e_with_optuna(self, target_error, p):
        def objective(trial):
            e = trial.suggest_float('e', 0.01, 20, step = 0.01)
            result, data_table, error_table, privatized_data = self.run_command(e)

            trial.set_user_attr('result', result)
            trial.set_user_attr('privatized_data', privatized_data)
            trial.set_user_attr('error_table', error_table)
            trial.set_user_attr('data_table', data_table)

            print(tabulate(data_table, headers=self.headers, tablefmt="grid"))
            # Minimize the diference: LP - target_error
            return abs(self.function_LP(self.frequency_estimation, self.get_real_frequency(), p) - target_error)

        study = optuna.create_study(direction='minimize') # minimize the difference
        study.optimize(objective, n_trials=1)

        best_e = study.best_params['e']
        privatized_data = study.best_trial.user_attrs['privatized_data']
        error_table = study.best_trial.user_attrs['error_table']
        result = study.best_trial.user_attrs['result']
        data_table = study.best_trial.user_attrs['data_table']

        print("\n================ e Optimization finished ====================")
        print(f"Best value of e: {best_e}")
        print(f"Closest error (LP - target_error): {study.best_value}")
        
        return best_e, privatized_data, error_table, result, data_table

    def utility_error(self):
        Lp = float(input("Enter the percentage error to reach (Lp): "))
        p = float(input("Enter the type of error (p): "))

        e, privatized_data, error_table, result, data_table = self.optimize_e_with_optuna(Lp, p) # Adjust the value of e to reach the desired error

        print(tabulate(data_table, headers=self.headers, tablefmt="grid"))

        option = input("Are you satisfied with the results? (yes/no): ") # Ask the user if he is satisfied with the results
        if option == "no":
            self.utility_error()
        else:
            print(f"\nError metrics for k={self.k}, m={self.m}, e={e}")
            print(tabulate(error_table, tablefmt="pretty"))

            print("Sending database to server ...")
        return e, result, privatized_data

    def privacy_error(self):
        from start import main
        p = float(input("Enter the type of error (p): "))
        error = self.function_LP(self.frequency_estimation, self.real_frequency, p)
        print(f"Initial Privacy Error (LP): {error}")

        error_table = []
        error_table_fav = []
        privatized_fav = None

        while True:
            e_min = input("Enter the minimum value of e: ") # Ask for a range for e to optimize 
            e_max = input("Enter the maximum value of e: ")
            step = input("Enter the step value: ")

            saved_e = 0

            for e in range(int(e_min), int(e_max), int(step)): # Optimize e
                result, data_table, error_table, privatized_data = self.run_command(e)
                f_estimated, f_real = self.frequencies()
                error = self.function_LP(f_estimated, f_real, p)

                print(f"\nError for e = {e}: {error}")
                print(tabulate(data_table, headers=self.headers, tablefmt="grid"))

                save = input("Do you want to save this privatized values? (yes/no): ")
                if save == "yes":
                    saved_e = e
                    H_fav = result
                    error_table_fav = error_table
                    privatized_fav = privatized_data
                    
            choice = input("\n1. Change e\n2. Change k or m\n3. Continue\n Select (1, 2 or 3): ")
            if choice == "2":
                main(2)
                break
            elif choice == "3":
                break
        
        if saved_e == 0:
            e = input("Enter the value of e to use: ")
            
            H_fav, data_table, error_table_fav, privatized_fav = self.run_command(e)
            print(tabulate(data_table, headers=self.headers, tablefmt="grid")) # Show database with the e
        else:
            print(f"Using the saved value of e: {saved_e}")

        option = input("Are you satisfied with the results? (yes/no): ")
        if option == "no":
            self.privacy_error()
        else:
            print(f"\nError metrics for k={self.k}, m={self.m}, e={saved_e}")
            print(tabulate(error_table_fav, tablefmt="pretty"))

            print("\nSending database to server ...")
        return saved_e, H_fav, privatized_fav

    def run(self):
        e = 0
        choice = input("Choose Utility or Privacy (u/p): ")
        if choice == "u":
            e, result, privatized_data = self.utility_error()
        elif choice == "p":
            e, result, privatized_data = self.privacy_error()
        else:
            print("Invalid choice. Please try again.")
        return e, result, privatized_data

    
def run_parameter_fitting(d, k, m, algorithm):
    optimizer = PrivacyUtilityOptimizer(d, k, m, algorithm)
    e, result, privatized_data = optimizer.run()
    return e, result, privatized_data

    

