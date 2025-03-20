import argparse
import os
import pandas as pd
from colorama import Style

from privadjust.main.individual_method import run_individual_method  
from privadjust.main.general_method import run_general_method

def main():
    parser = argparse.ArgumentParser(description="Run the individual method for private frequency estimation.")
    parser.add_argument("file_path", type=str, help="The path to the input dataset file.")
    parser.add_argument("output_path", type=str, help="The path to the output where you want the final database to be saved.")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        raise FileNotFoundError(f"File not found at {args.file_path}")
    elif not os.path.exists(args.output_path):
        raise FileNotFoundError(f"Output path not found at {args.output_path}")
    
    file_name = os.path.basename(args.file_path)
    print(f"Processing {Style.BRIGHT}{file_name}{Style.RESET_ALL}")
    df = pd.read_excel(args.file_path)

    priv_df = run_individual_method(df)
    output = os.path.join(args.output_path, 'private_database.csv')
    priv_df.to_csv(output, index=False)
    print(f"{Style.BRIGHT}Private dataset saved at {args.output_path}{Style.RESET_ALL}")

def main_general():
    parser = argparse.ArgumentParser(description="Run the individual method for private frequency estimation.")
    parser.add_argument("file_path", type=str, help="The path to the input dataset file.")
    parser.add_argument("output_path", type=str, help="The path to the output where you want the final database to be saved.")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        raise FileNotFoundError(f"File not found at {args.file_path}")
    elif not os.path.exists(args.output_path):
        raise FileNotFoundError(f"Output path not found at {args.output_path}")
    
    file_name = os.path.basename(args.file_path)
    print(f"Processing {Style.BRIGHT}{file_name}{Style.RESET_ALL}")
    df = pd.read_excel(args.file_path)

    priv = run_general_method(df)

    for user, privatized_data in priv.items():
        output_file = os.path.join(args.output_path, f'{user}.csv')
        privatized_data.to_csv(args.output_path, index=False)
        
    print(f"{Style.BRIGHT}Private datasets saved at {args.output_path}{Style.RESET_ALL}")





