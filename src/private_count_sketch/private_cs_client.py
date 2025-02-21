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
import statistics

from utils.utils import load_dataset, generate_hash_functions, display_results, generate_error_table, generate_hash_function_G

class privateCSClient:
    def __init__(self, epsilon, k, m, dataset, domain, dataset_name):
        self.dataset_name = dataset_name
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
        self.H = generate_hash_functions(self.k,p, 3,self.m)

        #Definition of the hash family 4 by 4
        prime = 2**61 - 1
        self.G = generate_hash_function_G(self.k, prime)

    
    def bernoulli_vector(self):
        b = np.random.binomial(1, (np.exp(self.epsilon / 2) / (np.exp(self.epsilon / 2) + 1)), self.m)
        b = 2 * b - 1 
        return b

    def client(self, d):
        j = random.randint(0, self.k-1)
        v = np.zeros(self.m)

        v[self.H[j](d)] = 1 * self.G[j](d)
        
        b = self.bernoulli_vector()
        v_aux = v * b 

        self.client_matrix.append((v_aux,j))
        return v_aux, j

    def update_sketch_matrix(self, v, j):
        c_e = (np.exp(self.epsilon / 2) + 1) / (np.exp(self.epsilon / 2) - 1)
        x = self.k * ((c_e/2) * v + (1/2) * np.ones_like(v))
        for i in range (self.m):
            self.M[j,i] += x[i] 

    def estimate_client(self, d):
        median_vector = []
        for i in range(self.k):
            median_vector.append(self.M[i, self.H[i](d)] * self.G[i](d))
        median = statistics.median(median_vector)

        #f_estimated = (self.m/(self.m-1))*(median -(self.N/self.m))
        f_estimated = (self.m/(self.m-1))*(median)
        return f_estimated
    
    def execute_client(self):
        bar = Bar('Processing client data', max=len(self.dataset), suffix='%(percent)d%%')
        privatized_data = []
        for d in self.dataset:
            v_i, j_i = self.client(d)
            privatized_data.append((v_i, j_i))
            bar.next()
        bar.finish()
        
        df_client_matrix = pd.DataFrame(privatized_data, columns=['v', 'j'])

        data_dict = df_client_matrix.to_dict(orient='list')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "../../data/privatized")

        output_file = os.path.join(output_dir, f"{self.dataset_name}_private.pkl")
    
        with open(output_file, 'wb') as f:
            pickle.dump(privatized_data, f)
    
        df_client_matrix.to_csv(os.path.join(output_dir, f"{self.dataset_name}_private.csv"), index=False)
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
        return F_estimated, self.H, self.G

def run_private_cs_client(k, m, e, d):
    dataset, df, domain = load_dataset(f"{d}_filtered")

    # Initialize the private Count-Mean Sketch
    PCMS = privateCSClient(e, k, m, dataset, domain, d)

    # Client side: process the private data
    privatized_data = PCMS.execute_client()

    # Simulate the server side
    f_estimated, H, G = PCMS.server_simulator(privatized_data)

    # Save f_estimated to a file
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "../../data/frequencies")
    df_estimated.to_csv(os.path.join(output_dir, f"{d}_freq_estimated_cms.csv"), index=False)

    # Show the results
    data_table = display_results(df, f_estimated)
    return H, data_table, G