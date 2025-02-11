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

# Link with the route for the utilities (common functions)
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  'utils', 'utils.py'))
module_name = 'utils'

spec = importlib.util.spec_from_file_location(module_name, file_path)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

TEST_MODE = False

class privateCMSClient:
    def __init__(self, epsilon, k, m, dataset, domain):
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.N = len(dataset)

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # List to store the privatized matrices
        self.client_matrix = []

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.H = utils.generate_hash_functions(self.k,p, 3,self.m)
    
    def bernoulli_vector(self):
        b = np.random.binomial(1, (np.exp(self.epsilon/2)) / ((np.exp(self.epsilon/2)) + 1), self.m)
        b = 2 * b - 1  # Convert 0 to -1
        return b

    def client(self, d):
        j = random.randint(0, self.k-1)
        v = np.full(self.m, -1)
        selected_hash = self.H[j]
        v[selected_hash(d)] = 1
        b = self.bernoulli_vector()
        v_aux = v*b
        # Store the privatized matrix
        self.client_matrix.append((v_aux,j))
        return v_aux,j

    def update_sketch_matrix(self,v,j):
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * ((c_e/2) * v + (1/2) * np.ones_like(v))
        for i in range (self.m):
            self.M[j,i] += x[i]

    def estimate_client(self,d):
        sum_aux = 0
        for i in range(self.k):
            selected_hash = self.H[i]
            sum_aux += self.M[i, selected_hash(d)]
        
        f_estimated = (self.m/(self.m-1))*((sum_aux/self.k)-(self.N/self.m))
        return f_estimated
    
    def execute_client(self):
        bar = Bar('Processing client data', max=len(self.dataset), suffix='%(percent)d%%')
        privatized_data = []
        for d in self.dataset:
            v_i, j_i = self.client(d)
            privatized_data.append((v_i,j_i))
            bar.next()
        bar.finish()
        
        df_client_matrix = pd.DataFrame(privatized_data, columns=['v', 'j'])

        data_dict = df_client_matrix.to_dict(orient='list')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "../../data/privatized")

        output_file = os.path.join(output_dir, f"{args.d}_private.pkl")
    
        with open(output_file, 'wb') as f:
            pickle.dump(privatized_data, f)
    
        #df_client_matrix.to_csv(os.path.join(output_dir, f"{args.d}_private.csv"), index=False)
        return privatized_data
    
    def server_simulator(self,privatized_data):
        bar = Bar('Update sketch matrix', max=len(privatized_data), suffix='%(percent)d%%')
        for data in privatized_data:
            self.update_sketch_matrix(data[0],data[1])
            bar.next()
        bar.finish()

        F_estimated = {}
        for x in self.domain:
            F_estimated[x] = self.estimate_client(x)
            bar.next()
        bar.finish()
        return F_estimated
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Private Count Mean Sketch Algorithm for frequency estimation from a known domain.")
    parser.add_argument("-k", type=int, required=True, help="Number of hash functions used (Rows in the sketch matrix).")
    parser.add_argument("-m", type=int, required=True, help="Maximum domain value of the hash functions (Columns in the sketch matrix).")
    parser.add_argument("-e", type=float, required=True, help="Epsilon value.")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset used.")
    parser.add_argument("--verbose_time", action="store_true", help="Display execution times of the functions.")
    args = parser.parse_args()

    # Load the dataset
    dataset_name = f"{args.d}_filtered"
    dataset, df, domain = utils.load_dataset(dataset_name)

    # Initialize the private count mean sketch
    PCMS = privateCMSClient(args.e, args.k, args.m, dataset, domain)

    # Client side: process the private data
    privatized_data = PCMS.execute_client()

    # Simulate the server side
    f_estimated = PCMS.server_simulator(privatized_data)
 
    # Save f_estimated to a file
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "../../data/frequencies")
    df_estimated.to_csv(os.path.join(output_dir, f"{args.d}_freq_estimated_cms.csv"), index=False)

    # Show the results
    os.system('cls' if os.name == 'nt' else 'clear>/dev/null')
    utils.display_results(df, f_estimated)
