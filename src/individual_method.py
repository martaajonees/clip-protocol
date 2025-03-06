import os
import math
import pandas as pd
import numpy as np
from tabulate import tabulate

# Importing CMeS functions
from private_count_mean.private_cms_server import run_private_cms_server
from private_count_mean.private_cms_client import run_private_cms_client
from private_count_mean.cms_client_mean import run_cms_client_mean

# Importing data preprocessing functions
from scripts.preprocess import run_data_processor
from scripts.parameter_fitting import run_parameter_fitting

# Importing HCMS functions
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client
from private_hadamard_count_mean.private_hcms_server import run_private_hcms_server


class IndividualMethod:
    """
    This class represents the execution of various algorithms for private frequency estimation.
    It includes preprocessing data, computing parameters, and executing different privacy-preserving algorithms.
    """
    def __init__(self, df=None,  k=None, m=None, algorithm=None):
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
        #database = input("Enter the database name: ")
        self.df = run_data_processor()
    
    def calculate_k_m(self):
        """
        Step 2: Calculate k and m values based on user input for failure probability and overestimation factor.
        
        :return: The computed values of k and m.
        """
        f = float(input("Enter the failure probability: "))
        E = float(input("Enter the overestimation factor: "))

        self.k = int(1 / f)
        self.m = int(2.71828 / E )

        print(f"Calculated k={self.k}, m={self.m}")
        print(f"Space complexity: {self.k*self.m}")
        return self.k, self.m
        
    def execute_no_privacy(self):
        """Step 3: Execute Count-Mean Sketch (CMeS) without privacy protection."""
        headers=[
            "Element", "Real Frequency", "Real Percentage", 
            "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
            "Percentage Error"
        ]

        print("\n CMeS without privacy")
        data_table = run_cms_client_mean(self.k, self.m, self.df)
        print(tabulate(data_table, headers=headers, tablefmt="grid"))

    def execute_private_algorithms(self):
        """Step 4: Execute privacy-preserving algorithms (CMeS and HCMS)."""
        e = 150   
        k_values = [self.k, 16, 128, 1024, 32768]
        m_values = [self.m, 16, 1024, 256, 256]

        # k_values = [32768]
        # m_values = [256]

        results = {"CMeS": [], "HCMS": []}

        headers=[
            "Element", "Real Frequency", "Real Percentage", 
            "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
            "Percentage Error"
        ]

        for k, m in zip(k_values, m_values):
            for algorithm, client in zip(["CMeS", "HCMS"], [run_private_cms_client, run_private_hcms_client]):
                
                print(f"\n========= {algorithm} k: {k}, m:{m}, e:{e} ==========")
                if algorithm == "HCMS":
                    if math.log2(m).is_integer() == False:
                        m = 2 ** math.ceil(math.log2(m))
                        print(f"m must be a power of 2: m ={m}")

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
            print(f"\nResults for {algo}")
            print(tabulate(table, headers=["k", "m"] + headers, tablefmt="grid"))
    
    def select_algorithm(self):
        """Step 5: Choose an algorithm and specify k and m values."""
        self.k = int(input("Enter the value of k: "))
        self.m = int(input("Enter the value of m: "))
        self.algorithm = input("Enter the algorithm to execute:\n1. Count-Mean Sketch\n2. Hadamard Count-Mean Sketch\n")
        return self.algorithm
    
    def execute_algorithms(self):
        """Step 6: Perform parameter fitting and execute the selected server algorithm."""
        print("\nExecuting personalized privacy ...")
        e, result, privatized_data = run_parameter_fitting(self.df, self.k, self.m, self.algorithm)


        print("\nExecuting server ...")
        if self.algorithm == '1':
            run_private_cms_server(self.k, self.m, e, self.df, result, privatized_data)
        elif self.algorithm == '2':
            run_private_hcms_server(self.k, self.m, e, self.df, result, privatized_data)

        print("\nProcess done and results saved.")

def main(step=1):
    """Main function to run the step-by-step execution of the method."""
    experiment = IndividualMethod()
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

            # Step 5: Choose an algorithm, k and m
            experiment.select_algorithm()
            if input("Are you satisfied with the results? (yes/no): ") == 'yes':
                step = 4
            else:
                step = 2

        elif step == 4:
            # Step 6: Parameter fitting and execute server
            experiment.execute_algorithms()
            break
    

if __name__ == "__main__":
    main()
