import numpy as np
import pandas as pd

def compute_error_table(real_freq, estimated_freq):
    # Turn both into dictionaries {element: frequency}
    real_num_freq = dict(zip(real_freq['Element'], real_freq['Frequency']))
    estimated_num_freq = dict(zip(estimated_freq['Element'], estimated_freq['Frequency']))

    # Join both dictionaries to get all elements
    all_elements = set(real_num_freq.keys()).union(estimated_num_freq.keys())

    # Calculate error
    errors = [
        abs(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0))
        for key in all_elements
    ]
    N = len(real_freq)
    mean_error = np.mean(errors)
    total_errors = np.sum(errors)
    max_freq = max(real_num_freq.values())
    min_freq = min(real_num_freq.values())
    mse = np.mean([(real_num_freq.get(key, 0) - estimated_num_freq.get(key, 0)) ** 2 
                  for key in all_elements])
    normalized_mse = mse / (max_freq - min_freq)

    error_table = [
        ['Total Errors', f"{total_errors:.2f}"],
        ['Mean Error', f"{mean_error:.2f}"],
        ['Percentage Error', f"{(mean_error / N) * 100:.2f}%"],
        ['MSE', f"{mse:.2f}"],
        ['RMSE', f"{np.sqrt(mse):.2f}"],
        ['Normalized MSE', f"{normalized_mse:.4f}"],
        ['Normalized RMSE', f"{np.sqrt(normalized_mse):.2f}"]
    ]
    return error_table