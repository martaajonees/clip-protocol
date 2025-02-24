
import os
import importlib.util
import numpy as np
import pandas as pd
import random
import argparse
from sympy import primerange
from progress.bar import Bar
import pickle

from utils.utils import load_dataset, display_results

class privateCMSServer:
    def __init__(self, epsilon, k, m, dataset, domain, H):
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = dataset
        self.domain = domain
        self.N = len(dataset)
        self.H = H

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))
    
    def update_sketch_matrix(self,v,j):
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * ((c_e/2) * v + (1/2) * np.ones_like(v))
        for i in range (self.m):
            self.M[j,i] += x[i]

    def execute_server(self,privatized_data):
        bar = Bar('Update sketch matrix', max=len(privatized_data), suffix='%(percent)d%%')

        for data in privatized_data:
            self.update_sketch_matrix(data[0],data[1])
            bar.next()
        bar.finish()

        F_estimated = {}
        for x in self.domain:
            F_estimated[x] = self.estimate_server(x)
            bar.next()
        bar.finish()
        return F_estimated

    def estimate_server(self,d):
        sum_aux = 0
        for i in range(self.k):
            selected_hash = self.H[i]
            sum_aux += self.M[i, selected_hash(d)]
        
        f_estimated = (self.m/(self.m-1))*((sum_aux/self.k)-(self.N/self.m))
        return f_estimated
    
    def query_server(self, query_element):
        if query_element not in self.domain:
            return "Element not in the domain"
        estimation = self.estimate_server(query_element)
        return estimation

    
def run_private_cms_server(k, m, e, d, H, privatized_data):
    dataset, df, domain = load_dataset(f"{d}_filtered")
    
    #Initialize the server Count-Mean Sketch
    server = privateCMSServer(e, k, m, dataset, domain, H)
    
    # Execute the server
    f_estimated = server.execute_server(privatized_data)

    # Show the results
    os.system('cls' if os.name == 'nt' else 'clear>/dev/null')
    display_results(df, f_estimated)

    # Query the server
    while True:
        query = input("Enter an element to query the server or 'exit' to finish: ")
        if query.lower() == 'exit':
            break
        estimation = server.query_server(query)
        print(f"The estimated frequency of {query} is {estimation:.2f}")
