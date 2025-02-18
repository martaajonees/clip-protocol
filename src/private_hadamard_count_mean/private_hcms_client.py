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

from utils.utils import load_dataset, generate_hash_functions, display_results, generate_error_table


class privateHCMSClient:
    def __init__(self, epsilon, k, m, dataset, domain, dataset_name):
        self.dataset_name = dataset_name
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.H = self.hadamard_matrix(self.m)
        self.N = len(dataset)

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # List to store the privatized matrices
        self.client_matrix = []

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.hashes = generate_hash_functions(self.k,p, 3,self.m)
    
    def hadamard_matrix(self,n):
        if n == 1:
            return np.array([[1]])
        else:
            # Recursive function to generate the Hadamard matrix
            h_half = self.hadamard_matrix(n // 2)
            h = np.block([[h_half, h_half], [h_half, -h_half]])
        return h

    def cliente(self,d):
        j = random.randint(0, self.k-1)
        v = np.full(self.m, 0)
        selected_hash = self.hashes[j]
        v[selected_hash(d)] = 1
        w = np.dot(self.H, v)
        l = random.randint(0, self.m-1)

        P_active = np.exp(self.epsilon) / (np.exp(self.epsilon) + 1)
        if random.random() <= P_active:
            b = 1
        else:
            b = -1
    
        self.client_matrix.append((b * w[l], j, l))
        return b * w[l],j,l

    def update_sketch_matrix(self, w, j, l):
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * c_e * w
        self.M[j,l] =  self.M[j,l] + x

    def traspose_M(self):
        self.M = self.M @ np.transpose(self.H)

    def estimate_client(self,d):
        return (self.m / (self.m-1)) * (1/self.k * np.sum([self.M[i,self.hashes[i](d)] for i in range(self.k)]) - self.N/self.m)
    
    def execute_client(self):
        bar = Bar('Processing client data', max=len(self.dataset), suffix='%(percent)d%%')
        privatized_data = []
        for d in self.dataset:
            w_i, j_i, l_i = self.cliente(d)
            privatized_data.append((w_i,j_i,l_i))
            bar.next()
        bar.finish()

        df_client_matrix = pd.DataFrame(privatized_data, columns=['v', 'j', 'l'])

        data_dict = df_client_matrix.to_dict(orient='list')

        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "../../data/privatized")

        output_file = os.path.join(output_dir, f"{self.dataset_name}_private.pkl")
    
        with open(output_file, 'wb') as f:
            pickle.dump(privatized_data, f)
    
        df_client_matrix.to_csv(os.path.join(output_dir, f"{self.dataset_name}_private.csv"), index=False)
        return privatized_data

    def server_simulator(self, privatized_data):
        bar = Bar('Update sketch matrix', max=len(privatized_data), suffix='%(percent)d%%')
        for data in privatized_data:
            self.update_sketch_matrix(data[0],data[1],data[2])
            bar.next()
        bar.finish()

        # Transpose the matrix
        self.traspose_M()

        # Estimate the frequencies
        F_estimated = {}
        bar = Bar('Obtaining histogram of estimated frequencies', max=len(self.domain), suffix='%(percent)d%%')
        for x in self.domain:
            F_estimated[x] = self.estimate_client(x)
            bar.next()
        bar.finish()
        return F_estimated, self.hashes
    
def run_private_hcms_client(k, m, e, d):
    dataset, df, domain = load_dataset(f"{d}_filtered")

    # Initialize the client 
    client = privateHCMSClient(e, k, m, dataset, domain, d)

    # Client side: process the private data
    privatized_data = client.execute_client()

    # Simulate the server side
    f_estimated, hashes = client.server_simulator(privatized_data)

    # Save f_estimated to a file
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "../../data/frequencies")
    df_estimated.to_csv(os.path.join(output_dir, f"{d}_freq_estimated_cms.csv"), index=False)

    error_table = display_results(df, f_estimated)

    return hashes, error_table


  
