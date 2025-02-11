
import os
import subprocess
import importlib.util


if __name__ == "__main__":
    print("Executing preprocessing ...")
    database = input("Enter the database name: ")
    subprocess.run(['python3', 'preprocess.py', '-d', database , ])
    
    print("\nExecuting client ...")
    f = float(input("Enter the failure probability: "))
    E = float(input("Enter the overestimation factor: "))

    k = int(1 / f)
    m = int(2.71828 / E )
    
    os.chdir('../src/private_count_mean')  
    subprocess.run(['python3', 'private_cms_client.py', '-k', str(k), '-m', str(m), '-e', '5.0', '-d', database], stdout=subprocess.DEVNULL)

    print("\nExecuting personalized privacy ...")
    os.chdir('../../scripts') 
    subprocess.run(['python3', 'parameter_fitting.py', '-d', database, '-f', str(f), '-E', str(E)])

    print("\nExecuting server ...")
    os.chdir('../src/private_count_mean')  
    subprocess.run(['python3', 'private_cms_server.py', '-k', str(k), '-m', str(m), '-e', '5.0', '-d', database])

    print("\nProcess done and results saved.")

