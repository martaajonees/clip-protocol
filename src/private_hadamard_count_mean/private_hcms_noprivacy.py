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

# Link with the route for the utilities (common functions)
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..',  'utils', 'utils.py'))
module_name = 'utils'

spec = importlib.util.spec_from_file_location(module_name, file_path)
utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(utils)

TEST_MODE = False

class privateHCMS:
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
        self.hashes = utils.generate_hash_functions(self.k,p, 3,self.m)
    
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

    def estimate_d(self,d):
        return 1 / self.k * np.sum([self.M[i, self.hashes[i](d)] for i in range(self.k)])
    
    def execute_client(self):
        bar = Bar('Processing client data', max=len(self.dataset), suffix='%(percent)d%%')
        for d in self.dataset:
            w = self.cliente(d)
            self.update_sketch_matrix(w)
            bar.next()
        bar.finish()

    def execute_server(self):
        # Transpose the matrix
        self.traspose_M()

        # Estimate the frequencies
        F_estimated = {}
        bar = Bar('Obtaining histogram of estimated frequencies', max=len(self.domain), suffix='%(percent)d%%')
        for x in self.domain:
            F_estimated[x] = self.estimate_d(x)
            bar.next()
        bar.finish()
        return F_estimated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Private HADMARD Count Mean Sketch Algorithm for frequency estimation from a known domain reducing bandwidth.")
    parser.add_argument("-k", type=int, required=True, help="Number of hash functions used (Rows in the sketch matrix).")
    parser.add_argument("-m", type=int, required=True, help="Maximum domain value of the hash functions (Columns in the sketch matrix).")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset used.")
    parser.add_argument("--verbose_time", action="store_true", help="Show execution times of the functions.")
    args = parser.parse_args()

    # Load the dataset
    dataset, df, domain = utils.load_dataset(args.d)

    # Initialize the class
    HCMS = privateHCMS(args.k, args.m, dataset, domain)

    # Client side: process the private data
    HCMS.execute_client()

    # Server side: process the private data 
    f_estimated = HCMS.execute_server()

    # Show the results
    os.system('cls' if os.name == 'nt' else 'clear>/dev/null')
    
    utils.display_results(df, f_estimated)
