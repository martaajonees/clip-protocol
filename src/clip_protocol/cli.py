import argparse
import os
import pandas as pd
import sys
import shutil

from clip_protocol.main.setup import run_setup
from clip_protocol.main.mask import run_mask
from clip_protocol.main.agregate import run_agregate
from clip_protocol.main.estimate import run_estimate

def cli_setup():
    parser = argparse.ArgumentParser(description="Run privatization mask with input CSV")
    parser.add_argument("-d", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    if not os.path.isfile(args.d):
        print(f"❌ File not found: {args.d}")
        sys.exit(1)

    df_temp = pd.read_excel(args.d)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.d, header=1)  
    else:
        df = df_temp

    run_setup(df)

def cli_mask():
    parser = argparse.ArgumentParser(description="Run privatization mask with input CSV")
    parser.add_argument("-d", type=str, required=True, help="Path to the input CSV file")
    parser.add_argument("-o", type=str, required=False, help="Path to save the privatized output CSV")
    args = parser.parse_args()

    if not os.path.isfile(args.d):
        print(f"❌ File not found: {args.d}")
        sys.exit(1)

    df_temp = pd.read_excel(args.d)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.d, header=1)  
    else:
        df = df_temp
        
    df_data = run_mask(df)

    if args.o:
        output_dir = os.path.dirname(args.o)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        df_data.to_csv(args.o, index=False)
        print(f"✅ Privatized dataset saved to {args.o}")

def cli_agregate():
    run_agregate()

def cli_estimate():
    run_estimate()

def clear():
    current_dir = os.path.dirname(__file__)
    data_path = os.path.abspath(os.path.join(current_dir, "../../data"))

    if not os.path.exists(data_path):
        print(f"ℹ️ Data folder does not exist: {data_path}")
        return

    for filename in os.listdir(data_path):
        file_path = os.path.join(data_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # borrar archivos o enlaces
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # borrar carpetas
        except Exception as e:
            print(f"❌ Failed to delete {file_path}. Reason: {e}")

    print(f"🧹 Data cleared")
