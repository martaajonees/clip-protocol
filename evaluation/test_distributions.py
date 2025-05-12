import numpy as np
import pandas as pd
import random
import string
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def generate_user_id(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_dataset(distribution, n):
    
    if distribution == 'normal':
        valores = np.random.normal(loc=2, scale=1, size=n).astype(int)
    elif distribution == 'laplace':
        valores = np.random.laplace(loc=12, scale=2, size=n).astype(int)
    elif distribution == 'uniform':
        valores = np.random.uniform(low=0, high=4, size=n).astype(int)
    elif distribution == "exp":
        valores = np.random.exponential(scale=2.0, size=n).astype(int)
    else:
        raise ValueError("Unsupported distribution type")
    

    user_ids = [generate_user_id() for _ in range(n)]
    user_ids = list(user_ids)

    data = {'user_id': user_ids, 'aoi_hit': valores}
    df = pd.DataFrame(data)
    df.to_excel(f'datasets/aoi-hits-prueba.xlsx', index=False)

    return df

if __name__ == "__main__":
    generate_dataset('normal', 750)

