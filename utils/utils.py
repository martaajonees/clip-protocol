import numpy as np
import pandas as pd
import random
import os
import string
import matplotlib.pyplot as plt
from tabulate import tabulate
from scipy.stats import pearsonr

TEST_MODE = False  # (ENABLE for testing)

def create_dataset(N: int, dist_type: str) -> tuple[list, pd.DataFrame, list]:
    """
    Creates a dataset for frequency estimation.

    Args:
        N (int): Number of elements in the dataset.
        dist_type (string): Distribution type [exp (exponential), norm (normal), small (values within a reduced domain)].

    Returns:
        values (list): Generated dataset in list format.
        df (DataFrame): Generated dataset in Pandas DataFrame format.
        unique_values (list): Unique values (domain) in the dataset.

    Examples:
        >>> create_dataset(10**6, 'exp')
        >>> create_dataset(1000, 'small')
    """
    if dist_type == 'exp':
        values = np.random.exponential(scale=2.0, size=N).astype(int)
    elif dist_type == 'norm':
        values = np.random.normal(loc=12, scale=2, size=N).astype(int)
    elif dist_type == 'small':
        elements = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        frequencies = [0.29, 0.19, 0.15, 0.12, 0.1, 0.08, 0.05, 0.02]
        dataset = np.random.choice(elements, size=N, p=frequencies)
        values = dataset.tolist()
        np.random.shuffle(values)
    
    df = pd.DataFrame({'value': values})
    unique_values = df['value'].unique().tolist()
    unique_values.sort()
    return values, df, unique_values

def load_dataset(csv_filename):
    """
    Loads a dataset from a CSV file and returns the values, the DataFrame, and unique 'value' entries.

    Args:
        csv_filename (str): Name of the CSV file located in the 'datasets' folder.

    Returns:
        values (list): Dataset in list format.
        df (DataFrame): Dataset in Pandas DataFrame format.
        unique_values (list): Unique values (domain) of the dataset.
    """
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/filtered', csv_filename + '.csv'))
    df = pd.read_csv(dataset_path)
    df = df[['value']]
    values = df['value'].tolist()
    unique_values = df['value'].unique().tolist()
    return values, df, unique_values

def generate_hash_functions(k, p, c, m):
    """
    Generates a set of k c-independent hash functions (D -> m).

    Args:
        c (int): Number of coefficients for c-independent hash functions.
        k (int): Number of hash functions.
        p (int): Large prime number for hash function construction.
        m (int): Maximum domain value to which the hash functions map.

    Returns:
        hash_functions (list): Set of k hash functions.
    """
    hash_functions = []
    for _ in range(k):
        coefficients = [random.randint(1, p - 1) for _ in range(c)]
        hash_func = lambda x, coeffs=coefficients, p=p: (sum((coeffs[i] * (hash(x) ** i)) % p for i in range(c)) % p) % m
        hash_functions.append(hash_func)
    return hash_functions

def display_results(real_freq: pd.DataFrame, estimated_freq: dict):
    """
    Displays and compares real and estimated frequencies, along with error metrics.

    Args:
        real_freq (DataFrame): Real frequency data.
        estimated_freq (dict): Estimated frequency data.
    """
    N = real_freq.shape[0]
    f = real_freq['value'].value_counts()
    real_num_freq = f.sort_index().to_dict()
    real_percent_freq = ((f * 100 / N).sort_index()).to_dict()

    data_table = []
    for element in real_num_freq:
        if element in estimated_freq:
            real_count = real_num_freq[element]
            real_percent = real_percent_freq[element]
            estimated_count = estimated_freq[element]
            estimated_percent = (estimated_count / N) * 100
            diff = abs(real_num_freq[element] - estimated_freq[element])
            data_table.append([element, real_count, f"{real_percent:.3f}%", f"{estimated_count:.2f}", f"{estimated_percent:.3f}%", f"{diff:.2f}"])

    errors = [abs(real_num_freq[key] - estimated_freq[key]) for key in estimated_freq]
    mean_error = np.mean(errors)
    total_errors = np.sum(errors)
    max_freq = max(real_num_freq.values())
    min_freq = min(real_num_freq.values())
    mse = np.sum([(real_num_freq[key] - estimated_freq[key]) ** 2 for key in estimated_freq]) / len(estimated_freq)
    normalized_mse = mse / (max_freq - min_freq)
    pearson_corr, _ = pearsonr(list(real_num_freq.values()), list(estimated_freq.values()))

    error_table = [
        ['Total Errors', f"{total_errors:.2f}"],
        ['Mean Error', f"{mean_error:.2f}"],
        ['Percentage Error', f"{(mean_error / N) * 100:.2f}%"],
        ['MSE', f"{mse:.2f}"],
        ['RMSE', f"{np.sqrt(mse):.2f}"],
        ['Normalized MSE', f"{normalized_mse:.2f}"],
        ['Normalized RMSE', f"{np.sqrt(normalized_mse):.2f}"],
        ['Pearson Correlation Coefficient', f"{pearson_corr:.4f}"],
    ]

    if TEST_MODE:
        for error in error_table:
            print(f"{error[0]}: {error[1]}")
    else:
        print("RESULTS")
        print(tabulate(data_table, headers=["Element", "Real Frequency", "Real Percentage", "Estimated Frequency", "Estimated Percentage", "Estimation Difference"], tablefmt="pretty"))
        print('\n' + tabulate(error_table, tablefmt="pretty"))
