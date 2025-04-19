import numpy as np
import pandas as pd
import random
import string
import sys
import os
from tabulate import tabulate
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.clip_protocol.count_mean.private_cms_client import run_private_cms_client
from src.clip_protocol.scripts.preprocess import run_data_processor


def generate_user_id(length=10):
    """
    Generates a random user ID of the specified length.

    Args:
        length (int): The length of the generated user ID (default is 10).

    Returns:
        str: A randomly generated user ID.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_dataset(distribution, n):
    """
    Generates a dataset with a specified distribution and saves it as a CSV file.

    Args:
        distribution (str): The type of distribution to generate ('normal', 'laplace', 'uniform', 'exp').
        n (int): The number of data points to generate.

    Creates a CSV file with the dataset and stores it in the '../../data/filtered' directory.
    """
    if distribution == 'normal':
        valores = np.random.normal(loc=12, scale=2, size=n).astype(int)
    elif distribution == 'laplace':
        valores = np.random.laplace(loc=12, scale=2, size=n).astype(int)
    elif distribution == 'uniform':
        valores = np.random.uniform(low=0, high=4, size=n).astype(int)
    elif distribution == "exp":
        valores = np.random.exponential(scale=2.0, size=n).astype(int)

    user_ids = ["S01post"] * n

    
    user_ids = list(user_ids)

    data = {'user_id': user_ids, 'value': valores}
    df = pd.DataFrame(data)

    return df

def run_distribution_test():
    """
    Runs a distribution test by generating datasets for different distributions and evaluating 
    their error metrics using the Private Count Mean Sketch (PrivateCMS).

    Generates datasets for different distributions and calculates error metrics for 
    each distribution using various values for the 'k' and 'm' parameters. 
    It visualizes the estimated frequency distribution and displays the results as a table.

    Results include error metrics such as mean error, percentage error, MSE, RMSE, 
    and Pearson Correlation Coefficient.
    """
    N = 50000
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]
    e = 2

    # Define distributions
    distributions = ['laplace', 'uniform', 'normal', 'exp']

    for i in range(len(distributions)):
        print(f"\n================== {distributions[i]} ==================")
        
        # Generate the dataset
        df = generate_dataset(distributions[i], N)

        filename = f"{distributions[i]}_{N}"

        general_table = []

        for j in range(5):
            print(f"\nk={k[j]}, m={m[j]} ==================")
            _, error_table, estimated_freq = run_private_cms_client(k[j], m[j], e, df)

            error_dict = { key: value for key, value in error_table }

            row = [
                k[j],
                m[j],
                error_dict.get("Mean Error", ""),
                error_dict.get("Percentage Error", ""),
                error_dict.get("MSE", ""),
                error_dict.get("RMSE", ""),
                error_dict.get("Normalized MSE", ""),
                error_dict.get("Normalized RMSE", ""),
                error_dict.get("Pearson Correlation Coefficient", "")
            ]
            general_table.append(row)

            if j == 4:
                keys = list(estimated_freq.keys())
                values = list(estimated_freq.values())
                
                plt.figure(figsize=(10, 6))
                plt.bar(keys, values, color='skyblue')
                plt.xlabel("Element")
                plt.ylabel("Estimated Frequency")
                plt.title(f"Estimated Frequencies\nDistribution: {distributions[i]} (k={k[j]}, m={m[j]})")
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.show()

        headers = [
            "k", "m", "Mean Error", "Percentage Error", 
            "MSE", "RMSE", "Normalized MSE", "Normalized RMSE", "Pearson Corr"
        ]

        print(tabulate(general_table, headers=headers, tablefmt="grid"))


if __name__ == '__main__':
    run_distribution_test()