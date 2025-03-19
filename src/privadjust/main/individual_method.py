import math
from tabulate import tabulate
from colorama import Fore, Style
import pandas as pd
import argparse
import os

# Importing CMeS functions
from privadjust.count_mean.private_cms_server import run_private_cms_server
from privadjust.count_mean.private_cms_client import run_private_cms_client
from privadjust.count_mean.cms_client_mean import run_cms_client_mean

# Importing data preprocessing functions
from privadjust.scripts.preprocess import run_data_processor
from privadjust.scripts.parameter_fitting import run_parameter_fitting

# Importing HCMS functions
from privadjust.hadamard_count_mean.private_hcms_client import run_private_hcms_client
from privadjust.hadamard_count_mean.private_hcms_server import run_private_hcms_server


class IndividualMethod:
    """
    This class represents the execution of various algorithms for private frequency estimation.
    It includes preprocessing data, computing parameters, and executing different privacy-preserving algorithms.
    """
    def __init__(self, df,  k=None, m=None, algorithm=None):
        """
        Initializes the IndividualMethod instance.

        :param df: The input dataset as a pandas DataFrame.
        :param k: The number of hash functions for the sketching algorithm.
        :param m: The number of bins in the sketching algorithm.
        :param algorithm: The selected algorithm for execution.
        """
        self.df = df
        self.k = k
        self.m = m
        self.algorithm = algorithm
    
    def preprocess_data(self):
        """Step 1: Data preprocessing by loading and filtering the dataset."""
        self.df = run_data_processor(self.df)
    
    def calculate_k_m(self):
        """
        Step 2: Calculate k and m values based on user input for failure probability and overestimation factor.
        
        :return: The computed values of k and m.
        """
        print("\n📂 Calculating k and m ... ")
        f = float(input("→ Enter the failure probability δ: "))
        E = float(input("→ Enter the overestimation factor ε: "))

        self.k = int(1 / f)
        self.m = int(2.71828 / E )

        print(f"{Fore.GREEN}Calculated k = {self.k} and m = {self.m}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Space complexity: {self.k*self.m}{Style.RESET_ALL}")
        return self.k, self.m
        
    def execute_no_privacy(self):
        """Step 3: Execute Count-Mean Sketch (CMeS) without privacy protection."""
        headers=[
            "Element", "Real Frequency", "Real Percentage", 
            "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
            "Percentage Error"
        ]
        
        print("\n📊 Calculing CMeS without privacy")
        data_table = run_cms_client_mean(self.k, self.m, self.df)
        print(tabulate(data_table, headers=headers, tablefmt="fancy_grid"))

    def execute_private_algorithms(self, e=150):
        """Step 4: Execute privacy-preserving algorithms (CMeS and HCMS)."""
        print("\n🔍 Searching parameters k and m ...")  
        k_values = [self.k, 16, 128, 1024, 32768]
        m_values = [self.m, 16, 1024, 256, 256]

        results = {"PCMeS": [], "PHCMS": []}

        headers=[
            "Element", "Real Frequency", "Real Percentage", 
            "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
            "Percentage Error"
        ]
         
        for k, m in zip(k_values, m_values):
            for algorithm, client in zip(["PCMeS", "PHCMS"], [run_private_cms_client, run_private_hcms_client]):
                
                print(f"\nRunning {Fore.GREEN}{algorithm}{Style.RESET_ALL} with k: {k}, m: {m} and ϵ: {e}")
                if algorithm == "PHCMS":
                    if math.log2(m).is_integer() == False:
                        m = 2 ** math.ceil(math.log2(m))
                        print(f"{Fore.RED}Adjusting m to a power of 2 → m = {m}{Style.RESET_ALL}")

                _, data_table, _, _,_ = client(k, m, e, self.df)

                data_dicts = [dict(zip(headers, row)) for row in data_table]

                for data_dict in data_dicts:
                    results[algorithm].append([
                        k, m, 
                        data_dict.get("Element", ""),
                        data_dict.get("Real Frequency", ""),
                        data_dict.get("Real Percentage", ""),
                        data_dict.get("Estimated Frequency", ""),
                        data_dict.get("Estimated Percentage", ""),
                        data_dict.get("Estimation Difference", ""),
                        data_dict.get("Percentage Error", ""),
                    ])
        

        for algo, table in results.items():
            print(f"\n 🔍Results for {Fore.CYAN}{algo}{Style.RESET_ALL}")
            print(tabulate(table, headers=["k", "m"] + headers, tablefmt="fancy_grid"))
    
    def select_algorithm(self):
        """Step 5: Choose an algorithm and specify k and m values."""
        print(f"\n🔍 Selecting an parameters and algorithm ...")
        self.k = int(input("→ Enter the value of k: "))
        self.m = int(input("→ Enter the value of m: "))
        self.algorithm = input("→ Enter the algorithm to execute:\n  1. Count-Mean Sketch\n  2. Hadamard Count-Mean Sketch\nSelect: ")
        return self.algorithm
    
    def execute_algorithms(self):
        """Step 6: Perform parameter fitting and execute the selected server algorithm."""
        print("\n🔄 Executing personalized privacy ...")
        e, result, privatized_data = run_parameter_fitting(self.df, self.k, self.m, self.algorithm)


        print("\n⚙️ Running server ...")
        priv_df = None
        if self.algorithm == '1':
            priv_df = run_private_cms_server(self.k, self.m, e, self.df, result, privatized_data)
        elif self.algorithm == '2':
            priv_df = run_private_hcms_server(self.k, self.m, e, self.df, result, privatized_data)
        return priv_df

def run_individual_method(df, step=1):
    """Main function to run the step-by-step execution of the method."""
    experiment = IndividualMethod(df)
    priv_df = None
    while True:
        if step == 1:
            # Step 1: Data preprocessing
            experiment.preprocess_data()
            step = 2
    
        if step == 2:
            #Step 2: Calculate k and m
            experiment.calculate_k_m()

            # Step 3: Execute no privacy algorithms
            experiment.execute_no_privacy()

            if input("Are you satisfied with the results? (yes/no): ") == 'yes':
                step = 3
            else:
                step = 2
                
        elif step == 3:
            # Step 4: Execute private algorithms
            experiment.execute_private_algorithms()

            if input("\nDo you want to change ϵ value? (yes/no): ") == 'yes':
                e1 = float(input("→ Enter the new value of ϵ: "))
                experiment.execute_private_algorithms(e1)

            # Step 5: Choose an algorithm, k and m
            experiment.select_algorithm()
            if input("Are you satisfied with the results? (yes/no): ") == 'yes':
                step = 4
            else:
                step = 2

        elif step == 4:
            # Step 6: Parameter fitting and execute server
            priv_df = experiment.execute_algorithms()
            break
    return priv_df
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the individual method for private frequency estimation.")
    parser.add_argument("file_path", type=str, help="The path to the input dataset file.")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        raise FileNotFoundError(f"File not found at {args.file_path}")
    
    file_name = os.path.basename(args.file_path)
    print(f"Processing {Style.BRIGHT}{file_name}{Style.RESET_ALL}")
    df = pd.read_excel(args.file_path)
    run_individual_method(df)
