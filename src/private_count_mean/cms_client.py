from sympy import primerange
import random
import numpy as np
import importlib.util
import os
import argparse
import time
from progress.bar import Bar
from tabulate import tabulate
import sys
import pandas as pd
import pickle

# Enlace con la ruta para las utilidades (funciones de uso comun)
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  'utils', 'utils.py'))
module_name = 'utils'

spec = importlib.util.spec_from_file_location(module_name, file_path)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

TEST_MODE = False

class CMSClient:
    def __init__(self, k, m, dataset, domain):
        self.k = k 
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.N = len(dataset)
        
        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.H = utils.generate_hash_functions(self.k,p, 3,self.m)

    def client(self, d):
        j = random.randint(0, self.k-1)
        v = np.full(self.m, -1)
        selected_hash = self.H[j]
        v[selected_hash(d)] = 1
        return v, j
   
    def update_sketch_matrix(self, d):
        for i in range (self.k):
            selected_hash = self.H[i]
            hash_index = selected_hash(d)
            self.M[i ,hash_index] += 1

    def estimate_client(self,d):
        min_estimation = float('inf')
        for i in range(self.k):
            selected_hash = self.H[i]
            min_estimation = min(min_estimation, self.M[i,selected_hash(d)])
        return min_estimation
    
    def server_simulator(self):
        bar = Bar('Processing client data', max=len(self.dataset), suffix='%(percent)d%%')

        for d in self.dataset:
            self.update_sketch_matrix(d)
            bar.next()
        bar.finish()

        F_estimated = {}
        bar = Bar('Obtaining histogram of estimated frequencies', max=len(self.domain), suffix='%(percent)d%%')
        for x in self.domain:
            F_estimated[x] = self.estimate_client(x)
            bar.next()
        bar.finish()
        return F_estimated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count Mean Sketch Algorithm for frequency estimation from a known domain.")
    parser.add_argument("-k", type=int, required=True, help="Number of hash functions used (Rows in the sketch matrix).")
    parser.add_argument("-m", type=int, required=True, help="Maximum domain value of the hash functions (Columns in the sketch matrix).")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset used.")
    parser.add_argument("--verbose_time", action="store_true", help="Display execution times of the functions.")
    args = parser.parse_args()

    # Load the dataset
    dataset_name = f"{args.d}_filtered"
    dataset, df, domain = utils.load_dataset(dataset_name)

    # Initialize the CMSClient
    PCMS = CMSClient(args.k, args.m, dataset, domain)

    # Simulate the server side
    f_estimated = PCMS.server_simulator()

    # Save f_estimated to a file
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "../../data/frequencies")
    df_estimated.to_csv(os.path.join(output_dir, f"{args.d}_freq_estimated_cms.csv"), index=False)

    # Show the results
    os.system('cls' if os.name == 'nt' else 'clear>/dev/null')
    utils.display_results(df, f_estimated)


  
