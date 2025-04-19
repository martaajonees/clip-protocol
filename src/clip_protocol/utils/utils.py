import numpy as np
import pandas as pd
import random
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../../data")
CONFIG_FILE = os.path.join(DATA_PATH, "setup_config.json")
CONFIG_MASK = os.path.join(DATA_PATH, "mask_config.json")

def save_setup_json(setup_instance):
    config = {
        "k": setup_instance.k,
        "m": setup_instance.m,
        "e": setup_instance.e_ref,
        "events_names": setup_instance.events_names,
        "privacy_method": setup_instance.privacy_method,
        "error_metric": setup_instance.error_metric,
        "error_value": setup_instance.error_value,
        "tolerance": setup_instance.tolerance,
        "p": setup_instance.p if hasattr(setup_instance, 'p') else None,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
        print("✅ Setup configuration saved")

def load_setup_json():
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return config["k"], config["m"], config["e"],config["events_names"], config["privacy_method"], config["error_metric"], config["error_value"], config["tolerance"], config["p"]

def save_mask_json(mask_instance, e, coeffs, privatized_dataset):
    config = {
        "k": mask_instance.k,
        "m": mask_instance.m,
        "e": e,
        "hash": coeffs,
        "privacy_method": str(mask_instance.privacy_method),
    }
    dataset_path = os.path.join(DATA_PATH, f"privatized_dataset.csv")

    df = pd.DataFrame(privatized_dataset)
    df.to_csv(dataset_path, index=False)

    with open(CONFIG_MASK, "w") as f:
        json.dump(config, f)
        print("✅ Mask configuration saved")

def load_mask_json():
    with open(CONFIG_MASK, "r") as f:
        config = json.load(f)
    
    hash_params = config["hash"]
    hash_functions = rebuild_hash_functions(hash_params)

    return config["k"], config["m"], config["e"], hash_functions, config["privacy_method"]
        
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
    coeffs = []
    functions_params = {}
    for _ in range(k):
        coefficients = [random.randint(1, p - 1) for _ in range(c)]
        hash_func = lambda x, coeffs=coefficients, p=p: (sum((coeffs[i] * (hash(x) ** i)) % p for i in range(c)) % p) % m
        hash_functions.append(hash_func)
        coeffs.append(coefficients)
    
    functions_params = {
        "coefficients": coeffs,
        "p": p,
        "m": m
    }
    return hash_functions, functions_params

def rebuild_hash_functions(functions_params):
    """
    Rebuilds the hash functions from the coefficients.

    Args:
        hash_coeff (list): Coefficients of the hash functions.
        p (int): Large prime number for hash function construction.
        m (int): Maximum domain value to which the hash functions map.

    Returns:
        list: Rebuilt hash functions.
    """
    hash_functions = []
    hash_coeffs = functions_params["coefficients"]
    p = functions_params["p"]
    m = functions_params["m"]
    for coeffs in hash_coeffs:
        hash_func = lambda x, coeffs=coeffs, p=p: (sum((coeffs[i] * (hash(x) ** i)) % p for i in range(len(coeffs))) % p) % m
        hash_functions.append(hash_func)
    return hash_functions

def display_results(real_freq: pd.DataFrame, estimated_freq: dict):
    real_num_freq = dict(zip(real_freq['Element'], real_freq['Frequency']))

    N = sum(real_num_freq.values())

    real_percent_freq = {k: (v * 100 / N) for k, v in real_num_freq.items()}
    estimated_freq_dict = dict(zip(estimated_freq['Element'], estimated_freq['Frequency']))

    data_table = []
    for element in estimated_freq_dict:
        if element in estimated_freq_dict:
            real_count = real_num_freq[element]
            real_percent = real_percent_freq[element]
            estimated_count = estimated_freq_dict[element]
            estimated_percent = (estimated_count / N) * 100
            diff = abs(real_count - estimated_count)
            
            if real_count > 0:
                percent_error = abs(real_count - estimated_count) / real_count * 100
            else:
                percent_error = 0.0
            
            data_table.append([
                element, 
                real_count, 
                f"{real_percent:.3f}%", 
                f"{estimated_count:.2f}", 
                f"{estimated_percent:.3f}%", 
                f"{diff:.2f}", 
                f"{percent_error:.2f}%"
            ])
    return data_table

def get_real_frequency(df):
    count = df['value'].value_counts().reset_index()
    count.columns = ['Element', 'Frequency']
    return count