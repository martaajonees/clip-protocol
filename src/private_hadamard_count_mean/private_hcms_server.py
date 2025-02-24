
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

from utils.utils import load_dataset, display_results

class privateHCMSServer:
    def __init__(self, epsilon, k, m, dataset, domain, hashes):
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.H = self.hadamard_matrix(self.m)
        self.N = len(dataset)
        self.hashes = hashes

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

    def update_sketch_matrix(self, w, j, l):
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * c_e * w
        self.M[j,l] =  self.M[j,l] + x

    def traspose_M(self):
        self.M = self.M @ np.transpose(self.H)

    def estimate_server(self,d):
        return (self.m / (self.m-1)) * (1/self.k * np.sum([self.M[i,self.hashes[i](d)] for i in range(self.k)]) - self.N/self.m)

    def execute_server(self, privatized_data):
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
            F_estimated[x] = self.estimate_server(x)
            bar.next()
        bar.finish()
        return F_estimated

def run_private_hcms_server(k, m, e, d, hashes, privatized_data):
    dataset, df, domain = load_dataset(d)

    # Initialize the server
    server = privateHCMSServer(e, k, m, dataset, domain, hashes)
    
    # Execute the server
    f_estimated = server.execute_server(privatized_data)

    # Show the results
    os.system('cls' if os.name == 'nt' else 'clear>/dev/null')
    display_results(df, f_estimated)


  
