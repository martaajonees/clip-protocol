
import os
import sys
from tabulate import tabulate

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from private_count_mean.private_cms_client import run_private_cms_client
from private_count_sketch.private_cs_client import run_private_cs_client
from private_hadamard_count_mean.private_hcms_client import run_private_hcms_client

def run_distribution_test():
    k = [16, 128, 128, 1024, 32768]
    m = [16, 16, 1024, 256, 256]
    e = 2

    filename = f"dataOviedo"

    for j in range(len(k)):
        print(f"\n================== k: {k[j]}, m: {m[j]} ==================")
        print(" \n========= CMS ==========")
        _, error_table = run_private_cms_client(k[j], m[j], e, filename)
        print(" \n========= CS ===========")
        _, error_table = run_private_cs_client(k[j], m[j], e, filename)
        print(" \n========= HCMS ===========")
        _, error_table = run_private_hcms_client(k[j], m[j], e, filename)


if __name__ == '__main__':
    run_distribution_test()