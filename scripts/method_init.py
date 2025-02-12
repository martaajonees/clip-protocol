
import os
import subprocess
import importlib.util
import pandas as pd

if __name__ == "__main__":
    print("Executing preprocessing ...")
    database = input("Enter the database name: ")
    subprocess.run(['python3', 'preprocess.py', '-d', database , ])
    
    print("\nExecuting client ...")
    while True:
        f = float(input("Enter the failure probability: "))
        E = float(input("Enter the overestimation factor: "))

        k = int(1 / f)
        m = int(2.71828 / E )

        print(f"k={k}, m={m}")
        
        os.chdir('../src/private_count_mean')  
        subprocess.run(['python3', 'cms_client.py', '-k', str(k), '-m', str(m), '-d', database], stdout=subprocess.DEVNULL)
    
        error_table = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data/error_tables', 'errors_table.csv'))
        print(pd.read_csv(error_table))

        choice = input("Are you satisfied with k and m? (yes/no): ")
        if choice == 'yes':
            break

    print("\nExecuting personalized privacy ...")
    os.chdir('../../scripts') 
    subprocess.run(['python3', 'parameter_fitting.py', '-d', database, '-f', str(f), '-E', str(E)])

    print("\nExecuting server ...")
    os.chdir('../src/private_count_mean')  
    subprocess.run(['python3', 'private_cms_server.py', '-k', str(k), '-m', str(m), '-e', '5.0', '-d', database])

    print("\nProcess done and results saved.")

