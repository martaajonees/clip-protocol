import argparse
import os
from colorama import Style

from privadjust.main.individual_method import main  

def main():
    parser = argparse.ArgumentParser(description="Run the individual method for private frequency estimation.")
    parser.add_argument("file_path", type=str, help="The path to the input dataset file.")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        raise FileNotFoundError(f"File not found at {args.file_path}")
    
    file_name = os.path.basename(args.file_path)
    print(f"Processing {Style.BRIGHT}{file_name}{Style.RESET_ALL}")
    df = pd.read_excel(args.file_path)

    run_individual_method(df)

