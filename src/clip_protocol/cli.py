import argparse
import os
import pandas as pd
import sys

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

    df = pd.read_excel(args.d)
    run_setup(df)

def cli_mask():
    parser = argparse.ArgumentParser(description="Run privatization mask with input CSV")
    parser.add_argument("-d", type=str, required=True, help="Path to the input CSV file")
    args = parser.parse_args()
    if not os.path.isfile(args.d):
        print(f"❌ File not found: {args.d}")
        sys.exit(1)

    df = pd.read_excel(args.d)
    run_mask(df)

def cli_agregate():
    run_agregate()

def cli_estimate():
    run_estimate()