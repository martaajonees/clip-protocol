
import pandas as pd
import sys
import os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.main.general_method import run_general_method
from colorama import Fore, Style

def generate_synthetic_dataset(num_users=5, num_values=10):
    """
    Generates a synthetic dataset for testing.

    Args:
        num_users (int): The number of users to generate in the dataset (default is 5).
        num_values (int): The number of values per user in the dataset (default is 10).

    Returns:
        pd.DataFrame: A DataFrame containing the synthetic dataset with user IDs and associated values.
    
    The dataset contains two columns:
        - 'user': A list of user IDs in the form 'u1', 'u2', ..., 'un'.
        - 'values': A list of values assigned to each user, with each user having a list of randomly chosen "AOI" values.
    """
    data = {
        "user": [f"u{i+1}" for i in range(num_users)],
        "values": [np.random.choice([f"AOI {str(i+1).zfill(3)}" for i in range(3)], num_values).tolist() for _ in range(num_users)]
    }
    df = pd.DataFrame(data)

    # save the dataset to a CSV file en  ../../data/raw/synthetic_dataset.xlsx
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
    output_path = os.path.join(output_dir, "synthetic_dataset.xlsx")

    df.to_excel(output_path, index=False)

    return df

def test_general_method():
    """
    Tests the general method with a generated synthetic dataset.

    Generates a synthetic dataset and passes it to the `run_general_method` function for processing.
    """
    df = generate_synthetic_dataset()
    run_general_method()

if __name__ == "__main__":
    test_general_method()
