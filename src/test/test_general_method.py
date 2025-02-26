
import pandas as pd
import sys
import os
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from general_method import run_general_method

def generate_synthetic_dataset(num_users=5, num_values=10):
    data = {
        "user": [f"u{i+1}" for i in range(num_users)],
        "values": [np.random.choice([f"AOI {str(i+1).zfill(3)}" for i in range(3)], num_values).tolist() for _ in range(num_users)]
    }
    return pd.DataFrame(data)

def test_general_method():
    df = generate_synthetic_dataset()
    run_general_method(df)

if __name__ == "__main__":
    test_general_method()
