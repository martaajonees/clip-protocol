import numpy as np
import pandas as pd
import os
from colorama import Fore, Style
from rich.progress import Progress

from privadjust.utils.utils import generate_hash_functions, display_results

class Server:
    """
    Unified server for Private Count-Mean Sketch (PCMeS) and Private Hadamard Count-Min Sketch (PHCMS).
    """
    def __init__(self, epsilon, k, m, df, hashes, method):
        """
        Initializes the private sketch server.
        
        :param method: Either 'PCMeS' or 'PHCMS'
        :param epsilon: Privacy parameter
        :param k: Number of hash functions
        :param m: Number of columns in the sketch matrix
        :param df: Dataframe containing the dataset
        :param hashes: List of hash functions
        """
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.df = df
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.N = len(self.dataset)
        self.M = np.zeros((self.k, self.m))
        self.hashes = hashes
        print(method)
        if method == '1':
            self.method = 'PCMeS'
        else:
            self.method = 'PHCMS'
        print(self.method)

        if self.method == 'PCHMS':
            self.H = self.hadamard_matrix(self.m)

    def hadamard_matrix(self, n):
        """
        Generates the Hadamard matrix recursively.

        Args:
            n (int): The size of the matrix.

        Returns:
            numpy.ndarray: The generated Hadamard matrix.
        """
        if n == 1:
            return np.array([[1]])
        else:
            h_half = self.hadamard_matrix(n // 2)
            h = np.block([[h_half, h_half], [h_half, -h_half]])
        return h

    def update_sketch_matrix(self, data_point):
        """Updates the sketch matrix based on the privatized data."""
        if self.method == "PCMeS":
            v, j = data_point
            c_e = (np.exp(self.epsilon / 2) + 1) / (np.exp(self.epsilon / 2) - 1)
            x = self.k * ((c_e / 2) * v + (1 / 2) * np.ones_like(v))
            self.M[j, :] += x
        elif self.method == "PHCMS":
            w, j, l = data_point
            c_e = (np.exp(self.epsilon / 2) + 1) / (np.exp(self.epsilon / 2) - 1)
            x = self.k * c_e * w
            self.M[j, l] += x
    
    def execute_server(self, privatized_data):
        """Processes privatized data and estimates frequencies."""
        with Progress() as progress:
            task = progress.add_task("[cyan]Updating sketch matrix", total=len(privatized_data))
            for data in privatized_data:
                self.update_sketch_matrix(data)
                progress.update(task, advance=1)
            
            if self.method == "PHCMS":
                self.M = self.M @ np.transpose(self.H)
            
            F_estimated = {}
            task = progress.add_task("[cyan]Estimating frequencies", total=len(self.domain))
            for x in self.domain:
                F_estimated[x] = self.estimate_server(x)
                progress.update(task, advance=1)
        return F_estimated
    
    def estimate_server(self, d):
        """Estimates the frequency of an element in the dataset."""
        if self.method == "PCMeS":
            return (self.m / (self.m - 1)) * (1 / self.k * np.sum([self.M[i, self.hashes[i](d)] for i in range(self.k)]) - self.N / self.m)
        elif self.method == "PHCMS":
            return (self.m / (self.m - 1)) * (1 / self.k * np.sum([self.M[i, self.hashes[i](d)] for i in range(self.k)]) - self.N / self.m)
    
    def query_server(self, query_element):
        """Queries the estimated frequency of an element."""
        if query_element not in self.domain:
            return "Element not in the domain"
        return self.estimate_server(query_element)

def run_private_sketch_server(method, k, m, e, df, hashes, privatized_data):
    """
    Runs the private sketch server pipeline.
    
    :param method: Either 'PCMeS' or 'PHCMS'
    :param k: Number of hash functions
    :param m: Number of columns in the sketch matrix
    :param e: Privacy parameter
    :param df: Dataframe containing the dataset
    :param hashes: List of hash functions
    :param privatized_data: List of privatized data points
    """
    server = Server( e, k, m, df, hashes, method)
    privatized_data_save = pd.DataFrame(privatized_data)
    f_estimated = server.execute_server(privatized_data)
    display_results(df, f_estimated)
    
    while True:
        query = input("Enter an element to query the server or 'exit' to finish: ")
        if query.lower() == 'exit':
            break
        estimation = server.query_server(query)
        print(f"The estimated frequency of {query} is {estimation:.2f}")
    
    return privatized_data_save
