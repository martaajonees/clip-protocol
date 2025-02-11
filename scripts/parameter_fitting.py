import subprocess
import re
import argparse
import random
import pandas as pd
import os
import optuna

ALGORITHM_PATHS = {
        1: "../src/private_count_mean/private_cms_client.py",
        2: "../src/private_hadamard_count_mean/private_hcms.py",
}   

class PrivacyUtilityOptimizer:
    def __init__(self, dataset_name, failure_probability, overestimation_factor):
        self.dataset_name = dataset_name
        self.failure_probability = failure_probability
        self.overestimation_factor = overestimation_factor

        self.frequency_estimation_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/frequencies', dataset_name + '_freq_estimated_cms.csv'))
        self.filtered_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/filtered', args.d + '_filtered.csv'))
        
        self.real_frequency = self.get_real_frequency()
        self.load_frequency_estimation()
        
        self.N = self.real_frequency['Frequency'].sum()

        self.k = int(1 / self.failure_probability)
        self.m = int(2.71828 / self.overestimation_factor)
    
    def load_frequency_estimation(self):
        self.frequency_estimation = pd.read_csv(self.frequency_estimation_path)

    def function_LP(self, f_estimated, f_real, p):
        sum_error = 0
        merged = f_estimated.merge(f_real, on="Element", suffixes=("_estimated", "_real"))
        for _, row in merged.iterrows():
            sum_error += abs(row["Frequency_estimated"] - row["Frequency_real"]) ** p
        return (1 / self.N) * sum_error

    def run_command(self, e):
        script_dir = os.path.abspath(ALGORITHM_PATHS[1])
        cmd = ["python3", script_dir, "-k", str(self.k), "-m", str(self.m), "-e", str(e), "-d", self.dataset_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.load_frequency_estimation()
        if result.returncode != 0:
            print(f"Error al ejecutar el comando: {result.stderr}")

    def get_real_frequency(self):
        #dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/filtered', args.d + '.csv'))
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
        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/error_tables'))
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
        run_command(e)
        dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/privatized', args.d + '_private.csv'))
        df = pd.read_csv(dataset_path)
        print(df)

        # Ask the user if he is satisfied with the results
        option = input("Are you satisfied with the results? (y/n): ")
        if option == "n":
            utility_error(args)
        else:
            print("Sending database to server ...")

    def privacy_error(self):
        p = float(input("Enter the type of error (p): "))
        error = self.function_LP(self.frequency_estimation, self.real_frequency, p)
        print(f"Initial Privacy Error (LP): {error}")

        # Ask for a range for e to optimize 
        e_min = input("Enter the minimum value of e: ")
        e_max = input("Enter the maximum value of e: ")

        step = input("Enter the step value: ")

        for e in range(int(e_min), int(e_max), int(step)):
            self.run_command(e)
            f_estimated, f_real = self.frequencies()
            error = self.function_LP(f_estimated, f_real, p)
            print(f"Error for e = {e}: {error}")
        
        e = input("Enter the value of e to use: ")

        # Show database with the e
        self.run_command(e)
        dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/privatized', self.dataset_name + '_private.csv'))
        df = pd.read_csv(dataset_path)
        print(df)

        # Ask the user if he is satisfied with the results
        option = input("Are you satisfied with the results? (y/n): ")
        if option == "n":
            self.privacy_error()
        else:
            print("Sending database to server ...")

    def run(self):
        choice = input("Choose Utility or Privacy (u/p): ")
        if choice == "u":
            self.utility_error()
        elif choice == "p":
            self.privacy_error()
        else:
            print("Invalid choice. Please try again.")

    
        

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Script to find the best parameters for a given algorithm")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset to use")
    parser.add_argument("-f", type=str, required=True, help="Failure probability")
    parser.add_argument("-E", type=str, required=True, help="Overestimation factor")
    args = parser.parse_args()

    f = float(args.f)
    E = float(args.E)
    optimizer = PrivacyUtilityOptimizer(args.d, f, E)
    optimizer.run()

    # Sketch frequency estimation
    # dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/frequencies', args.d + '_freq_estimated_cms.csv'))
    #f_estimated = pd.read_csv(dataset_path)

    # Real frequency
    # f_real = real_frequency(args)
    #N = f_real['Frequency'].sum()

    # Constants
    #DATA_FILE = args.d
    # f = 0.01 # Failure probability
    # E = 0.5 # Overestimation factor
    #euler = 2.71828 # Euler's number
    
    # Calculation of m and k
    #k = int(1/f)
    #m = int(euler/ E )
    #print(f"Initial values: k = {k}, m = {m}")

    # Utility or Privacy?
    # choice = input("Choose Utility or Privacy (u/p): ")

    # if choice == "u":
    #     utility_error(args)
    # elif choice == "p":
    #     privacy_error(N, k, m, f_estimated, f_real, args)
    # else:
    #     print("Invalid choice. Please try again.")

    

