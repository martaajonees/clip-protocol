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

from utils.utils import load_dataset, generate_error_table, generate_hash_functions, display_results

class CMSClient:
    def __init__(self, k, m, df):
        self.df = df
        self.k = k 
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.N = len(self.dataset)
        
        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.H = generate_hash_functions(self.k,p, 3,self.m)

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
        mean = 0
        for i in range(self.k):
            selected_hash = self.H[i]
            mean += self.M[i,selected_hash(d)]
        return mean/self.k
    
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

def run_cms_client_mean(k, m, df):
    # Initialize the CMSClient
    PCMS = CMSClient(k, m, df)

    # Simulate the server side
    f_estimated = PCMS.server_simulator()
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    # Show the results
    data_table, _= display_results(df, f_estimated)

    return data_table




  
