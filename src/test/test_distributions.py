import numpy as np
import pandas as pd
import random
import string
import sys
import os
from tabulate import tabulate
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from private_count_mean.private_cms_client import run_private_cms_client
from scripts.preprocess import run_data_processor


def generate_user_id(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_dataset(distribution, n):
    if distribution == 'normal':
        valores = np.random.normal(loc=12, scale=2, size=n).astype(int)
    elif distribution == 'laplace':
        valores = np.random.laplace(loc=12, scale=2, size=n).astype(int)
    elif distribution == 'uniform':
        valores = np.random.uniform(low=0, high=4, size=n).astype(int)
    elif distribution == "exp":
        valores = np.random.exponential(scale=2.0, size=n).astype(int)

    # user_ids = set()
    # while len(user_ids) < n:
    #     user_ids.add("S01post")

    user_ids = ["S01post"] * n

    
    user_ids = list(user_ids)

    data = {'user_id': user_ids, 'value': valores}
    df = pd.DataFrame(data)

    # Save the new dataset 
    df.to_csv(f'../../data/filtered/{distribution}_{n}_filtered.csv', index=False)

def run_distribution_test():

    N = 50000
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]
    e = 2

    # Define distributions
    distributions = ['laplace', 'uniform', 'normal', 'exp']

    for i in range(len(distributions)):
        print(f"\n================== {distributions[i]} ==================")
        
        # Generate the dataset
        generate_dataset(distributions[i], N)

        filename = f"{distributions[i]}_{N}"

        general_table = []

        for j in range(5):
            print(f"\nk={k[j]}, m={m[j]} ==================")
            _, error_table, estimated_freq = run_private_cms_client(k[j], m[j], e, filename)

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