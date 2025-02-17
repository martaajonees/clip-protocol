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

from utils.utils import load_dataset, generate_error_table, generate_hash_functions

class HCMSClient:
    def __init__(self, k, m, dataset, domain):
        self.k = k
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.H = self.hadamard_matrix(self.m)
        self.N = len(dataset)

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.hashes = generate_hash_functions(self.k,p, 3,self.m)
    
    def hadamard_matrix(self,n):
        """
        Generate the Hadamard matrix of order n.
        """
        if n == 1:
            return np.array([[1]])
        else:
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
    
        self.client_matrix.append((w[l], j, l))
        return w[l],j,l

    def update_sketch_matrix(self, w):
        x = self.k *  w
        self.M[j,l] =  self.M[j,l] + x

    def traspose_M(self):
        self.M = self.M @ np.transpose(self.H)

    def estimate_client(self,d):
        return 1 / self.k * np.sum([self.M[i, self.hashes[i](d)] for i in range(self.k)])
    
    def execute_client(self):
        bar = Bar('Processing client data', max=len(self.dataset), suffix='%(percent)d%%')
        for d in self.dataset:
            w = self.cliente(d)
            self.update_sketch_matrix(w)
            bar.next()
        bar.finish()

    def server_simulator(self):
        # Transpose the matrix
        self.traspose_M()

        # Estimate the frequencies
        F_estimated = {}
        bar = Bar('Obtaining histogram of estimated frequencies', max=len(self.domain), suffix='%(percent)d%%')
        for x in self.domain:
            F_estimated[x] = self.estimate_client(x)
            bar.next()
        bar.finish()
        return F_estimated

def run_hcms_client(k, m, d):
    dataset_name = f"{d}_filtered"
    dataset, df, domain = load_dataset(dataset_name)

    # Initialize the HCMSClient
    HCMS = HCMSClient(k, m, dataset, domain)

    HCMS.execute_client()

    # Simulate the server side
    f_estimated = HCMS.server_simulator()

    # Save f_estimated to a file
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "../../data/frequencies")
    df_estimated.to_csv(os.path.join(output_dir, f"{d}_freq_estimated_cms.csv"), index=False)

    # Show the results
    generate_error_table(df, f_estimated)

