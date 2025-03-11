import pandas as pd
from utils.utils import load_dataset, generate_hash_functions, display_results, generate_error_table
from individual_method import IndividualMethod
from scripts.parameter_fitting import PrivacyUtilityOptimizer
from tabulate import tabulate

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
        # Step 1: Set value for error metric
        metric = input("Enter the metric to optimize: \n1. MSE\n2. LP\n3. Porcentual Error \nSelect (1, 2 or 3):  ")
        if metric == "1":
                Lp = float(input("Enter the MSE to reach: "))
                p = 2
        elif metric == "2":
                Lp = float(input("Enter the Lp to reach: "))
                p = float(input("Enter the type of error (p): "))
        elif metric == "3":
                Lp = float(input("Enter the Porcentual Error to reach: "))
                p = 1

        # Step 2: Set the user with more data
        df = df.explode("values", ignore_index=True).rename(columns={"values": "value"})
        user_counts = df["user"].value_counts() # Count the number of times each user appears in the dataset
        max_user = user_counts.idxmax() # Get the user with more data
        df_user = df[df["user"] == max_user] # Get the data of the user with more data
        print(df_user.head())

        # Step 3: Set k and m
        individual = IndividualMethod(df_user)
        k, m = individual.calculate_k_m()
        individual.execute_no_privacy()
        individual.execute_private_algorithms()
        algorithm = individual.select_algorithm()

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
                print(f"\nUser: {df['user'].unique()[index]}, e:{result['e']}, k:{k}, m:{m}")  # Imprimir el usuario
                print(tabulate(result["Porcentual Error Table"], headers='keys', tablefmt='fancy_grid'))