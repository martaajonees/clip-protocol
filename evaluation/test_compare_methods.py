
import os
import sys
from tabulate import tabulate

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.count_mean.private_cms_client import run_private_cms_client
from src.hadamard_count_mean.private_hcms_client import run_private_hcms_client

def run_distribution_test():
    """
    This script performs a distribution test using different private count-sketch methods.

    The purpose of this test is to compare the accuracy of three different private estimation techniques:
    1. **Private Count-Min Sketch (CMS)**
    2. **Private Count Sketch (CS)**
    3. **Private Hadamard Count-Min Sketch (HCMS)**

    These methods are used to estimate frequency distributions while preserving privacy. The test runs each method with different parameters and prints the corresponding error tables.
    - `k`: A list of values determining different sketch sizes.
    - `m`: A list of values controlling the memory allocation for each method.
    - `e`: Privacy parameter (presumably epsilon, controlling differential privacy strength).
    - `filename`: The input dataset file (`dataOviedo`).

    For each combination of `k` and `m`, the script runs the three private sketching methods and prints their respective error tables.
    """
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]
    e = 2

    filename = f"dataOviedo"

    for j in range(len(k)):
        print(f"\n================== k: {k[j]}, m: {m[j]} ==================")
        print(" \n========= CMS ==========")
        _, error_table = run_private_cms_client(k[j], m[j], e, filename)
        print(" \n========= HCMS ===========")
        _, error_table = run_private_hcms_client(k[j], m[j], e, filename)


if __name__ == '__main__':
    run_distribution_test()