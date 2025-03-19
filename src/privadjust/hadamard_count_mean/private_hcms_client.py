from sympy import primerange
import random
import numpy as np
from rich.progress import Progress
import pandas as pd

from privadjust.utils.utils import generate_hash_functions, display_results


class privateHCMSClient:
    """
    This class implements the private Count-Min Sketch (privateCMS) for differential privacy.
    It processes the dataset, applies privatization, and estimates frequencies on the server side.

    Attributes:
        epsilon (float): The privacy parameter for differential privacy.
        k (int): The number of hash functions.
        m (int): The size of the sketch matrix.
        dataset (list): The dataset containing values to be processed.
        domain (list): The unique values in the dataset.
        H (numpy.ndarray): The Hadamard matrix used in the privatization process.
        N (int): The total number of elements in the dataset.
        M (numpy.ndarray): The sketch matrix used to store frequency estimates.
        client_matrix (list): A list to store privatized matrices for each client.
        hashes (list): A list of hash functions.
    """
    def __init__(self, epsilon, k, m, df):
        """
        Initializes the privateHCMSClient class with the given parameters.

        Args:
            epsilon (float): The privacy parameter for differential privacy.
            k (int): The number of hash functions.
            m (int): The size of the sketch matrix.
            df (pandas.DataFrame): The dataset in DataFrame format.
        """
        self.df = df
        self.epsilon = epsilon
        self.k = k
        self.m = m
        self.dataset = self.df['value'].tolist()
        self.domain = self.df['value'].unique().tolist()
        self.H = self.hadamard_matrix(self.m)
        self.N = len(self.dataset)

        # Creation of the sketch matrix
        self.M = np.zeros((self.k, self.m))

        # List to store the privatized matrices
        self.client_matrix = []

        # Definition of the hash family 3 by 3
        primes = list(primerange(10**6, 10**7))
        p = primes[random.randint(0, len(primes)-1)]
        self.hashes = generate_hash_functions(self.k,p, 3,self.m)
    
    def hadamard_matrix(self,n):
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
            # Recursive function to generate the Hadamard matrix
            h_half = self.hadamard_matrix(n // 2)
            h = np.block([[h_half, h_half], [h_half, -h_half]])
        return h

    def client(self,d):
        """
        Applies privatization to the data using a random hash function and the Hadamard matrix.

        Args:
            d (any): The element to be privatized.

        Returns:
            tuple: A tuple containing the privatized value, hash function index, and matrix index.
        """
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
        """
        Updates the sketch matrix based on the privatized value.

        Args:
            w (float): The privatized value.
            j (int): The index of the hash function.
            l (int): The index of the matrix.
        """
        c_e = (np.exp(self.epsilon/2)+1) / ((np.exp(self.epsilon/2))-1)
        x = self.k * c_e * w
        self.M[j,l] =  self.M[j,l] + x

    def traspose_M(self):
        """
        Transposes the sketch matrix.
        """
        self.M = self.M @ np.transpose(self.H)

    def estimate_client(self,d):
        """
        Estimates the frequency of an element using the sketch matrix.

        Args:
            d (any): The element whose frequency is to be estimated.

        Returns:
            float: The estimated frequency of the element.
        """
        return (self.m / (self.m-1)) * (1/self.k * np.sum([self.M[i,self.hashes[i](d)] for i in range(self.k)]) - self.N/self.m)
    
    def execute_client(self):
        """
        Executes the client-side privatization and stores the privatized data.

        Returns:
            list: A list of privatized data.
        """
        with Progress() as progress:
            task = progress.add_task('Processing client data', total=len(self.dataset))
            privatized_data = []
            for d in self.dataset:
                w_i, j_i, l_i = self.client(d)
                privatized_data.append((w_i,j_i,l_i))
                progress.update(task, advance=1)

        return privatized_data

    def server_simulator(self, privatized_data):
        """
        Simulates the server-side process by updating the sketch matrix and estimating frequencies.

        Args:
            privatized_data (list): The list of privatized data.

        Returns:
            tuple: A tuple containing the estimated frequencies and the hash functions used.
        """
        with Progress() as progress:
            task = progress.add_task('[cyan]Update sketch matrix', total=len(privatized_data))
            for data in privatized_data:
                self.update_sketch_matrix(data[0],data[1],data[2])
                progress.update(task, advance=1)

            # Transpose the matrix
            self.traspose_M()

            # Estimate the frequencies
            F_estimated = {}
            task = progress.add_task('[cyan]Obtaining histogram of estimated frequencies', total=len(self.domain))
            for x in self.domain:
                F_estimated[x] = self.estimate_client(x)
                progress.update(task, advance=1)
        return F_estimated, self.hashes
    
def run_private_hcms_client(k, m, e, df):
    """
    Runs the private Count-Min Sketch client, processes the data, and estimates frequencies on the server.

    Args:
        k (int): The number of hash functions.
        m (int): The size of the sketch matrix.
        e (float): The privacy parameter epsilon for differential privacy.
        df (pandas.DataFrame): The dataset in DataFrame format.

    Returns:
        tuple: A tuple containing the hash functions, data table, error table, privatized data, and the estimated frequencies.
    """
    # Initialize the client 
    client = privateHCMSClient(e, k, m, df)

    # Client side: process the private data
    privatized_data = client.execute_client()

    # Simulate the server side
    f_estimated, hashes = client.server_simulator(privatized_data)

    # Save f_estimated to a file
    df_estimated = pd.DataFrame(list(f_estimated.items()), columns=['Element', 'Frequency'])

    data_table, error_table = display_results(df, f_estimated)

    return hashes, data_table, error_table, privatized_data, df_estimated


  
