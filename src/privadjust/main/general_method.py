
from privadjust.main.individual_method import IndividualMethod
from privadjust.scripts.preprocess import run_data_processor
from privadjust.scripts.parameter_fitting import PrivacyUtilityOptimizer

import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style
import ast

def run_general_method(df):
        """
        Executes the general method for optimizing privacy and utility trade-offs.

        Steps:
        1. Selects the error metric to optimize (MSE, LP, or Percentage Error).
        2. Identifies the user with the most data in the dataset.
        3. Calculates k and m values using the IndividualMethod class.
        4. Executes no-privacy and private algorithms.
        5. Optimizes privacy-utility trade-off for each user.

        Args:
                df (pd.DataFrame): The dataset containing user data with frequency values.
        """
        df = run_data_processor(df)

        # Step 1: Set value for error metric
        print(f"📊 Selection of the Optimization Metric")
        metric = input(f"\nEnter the metric to optimize: \n1. {Fore.CYAN}MSE{Style.RESET_ALL}\n2. {Fore.CYAN}LP{Style.RESET_ALL}\n3. {Fore.CYAN}Porcentual Error{Style.RESET_ALL} \nSelect:  ")
        if metric == "1":
                Lp = float(input("⭢ Enter the MSE to reach: "))
                p = 2
        elif metric == "2":
                Lp = float(input("⭢ Enter the Lp to reach: "))
                p = float(input("⭢ Enter the type of error ρ: "))
        elif metric == "3":
                Lp = float(input(f"⭢ Enter the {Fore.CYAN}Porcentual Error{Style.RESET_ALL} to reach: "))
                p = 1

        # Step 2: Set the user with more data
        df['values'] = df['values'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        df = df.explode("values", ignore_index=True).rename(columns={"values": "value"})
        
        user_counts = df["user"].value_counts() # Count the number of times each user appears in the dataset
        max_user = user_counts.idxmax() # Get the user with more data
        df_user = df[df["user"] == max_user] # Get the data of the user with more data
        
        # Step 3: Set k and m
        e = 150
        while(True):
                individual = IndividualMethod(df_user)
                k, m = individual.calculate_k_m()
                individual.execute_no_privacy()
                individual.execute_private_algorithms(e)
                algorithm = individual.select_algorithm()

                print(f"\n Do you want to test with another value of ϵ? (yes/no): ")
                if input() == "no":
                        break
                else:
                        e = input("⭢ Enter the value of ϵ: ")

        # Step 4: Execute utility error
        headers = ["Element", "Real Frequency", "Real Percentage", "Estimated Frequency", "Estimated Percentage", "Estimation Difference", "Percentage Error"]
        results = []
        for user in df["user"].unique():
                print(f"Processing user {user}")
                df_user_specific = df[df["user"] == user]

                optimizer = PrivacyUtilityOptimizer(df_user_specific, k, m, algorithm)
                e, _, _, data_table = optimizer.utility_error(Lp, p, metric)
                
                data_table = pd.DataFrame(data_table, columns=headers)
                results.append({"e": e, "Porcentual Error Table": data_table})
        
        results_df = pd.DataFrame(results)

        for index, result in results_df.iterrows():
                print(f"\nUser: {df['user'].unique()[index]}, ϵ:{result['e']}, k:{k}, m:{m}")  # Imprimir el usuario
                print(tabulate(result["Porcentual Error Table"], headers='keys', tablefmt='fancy_grid'))

if __name__ == "__main__":
    run_general_method()