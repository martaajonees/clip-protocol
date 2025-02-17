import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from scipy.stats import norm, laplace, uniform
from statsmodels.distributions.empirical_distribution import ECDF
from matplotlib import style
from tqdm import tqdm
import os
import sys
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from private_count_mean.private_cms_client import run_private_cms_client
from scripts.preprocess import run_data_processor

def transform_dataset(file_name, target_distribution):
    
    # matplotlib configuration
    plt.rcParams['savefig.bbox'] = "tight"
    style.use('ggplot') or plt.style.use('ggplot')

    # Load the dataset
    df = pd.read_excel(f'../../data/raw/{file_name}.xlsx')
    # delete first column
    df = df.drop(df.columns[0], axis=1)

    # Define distributions
    distributions = {
        'gaussian': norm,
        'normal': norm,
        'laplace': laplace,
        'uniform': uniform
    }
    
    # Apply the transformation
    distribution = distributions[target_distribution]
    columns = df.select_dtypes(include='number').columns

    for column_name in tqdm(columns, desc='Transforming columns'):
        column_data = df[column_name].dropna().values
        if len(column_data) > 0:
            ecdf = ECDF(column_data)
            uniform_values = ecdf(column_data)
            transformed_values = distribution.ppf(uniform_values)
            df[column_name] = transformed_values
    

    # Save the transformed dataset
    df.to_excel(f'../../data/raw/{file_name}_{target_distribution}.xlsx', index=False)

def display_error_table():
        # Go to data/error_tables and show the error table
        dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data/error_tables'))
        error_table_path = os.path.join(dir, 'errors_table.csv')
        if os.path.exists(error_table_path):
            error_table = pd.read_csv(error_table_path)
            print(error_table)
        else:
            print(f"Error: El archivo no existe en la ruta especificada: {error_table_path}")

def run_distribution_test():

    # Define distributions
    distributions = ['gaussian', 'laplace', 'uniform', 'normal']

    for distribution in distributions:
        print(f"\n============= {distribution} =============")
        file_name = "dataOviedo"
        # Transform the raw dataset 
        transform_dataset(file_name, distribution)

        # Filter the transformed dataset
        file_name = f"{file_name}_{distribution}"
        run_data_processor(file_name)

        # Test how the private CMS behaves with the transformed dataset
        run_private_cms_client(100, 543, 11, file_name)

        # Display the error table
        display_error_table()


if __name__ == '__main__':
    run_distribution_test()