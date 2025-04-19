
import os
import sys
import matplotlib.pyplot as plt
from tabulate import tabulate
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.clip_protocol.count_mean.private_cms_client import run_private_cms_client
from src.clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client
from test_distributions import generate_dataset

def save_table_to_pdf(df_results, filename="results.pdf"):
    # Create a figure and axis to plot the table
    fig, ax = plt.subplots(figsize=(8, 6))  # Define the size of the figure
    ax.axis('tight')
    ax.axis('off')

    # Generate the table
    table = ax.table(cellText=df_results.values, colLabels=df_results.columns, loc='center', cellLoc='center', colColours=["#f1f1f1"] * len(df_results.columns))

    # Adjust the table appearance
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df_results.columns))))

    # Save the table as a PDF
    with PdfPages(filename) as pdf:
        pdf.savefig(fig, bbox_inches="tight")
        plt.close()

def run_comparison_methods():
    """
    This script compares the different private count-sketch methods.

    The purpose of this test is to compare the accuracy of two different private estimation techniques:
    1. **Private Count-Min Sketch (CMS)**
    2. **Private Hadamard Count-Min Sketch (HCMS)**

    These methods are used to estimate frequency distributions while preserving privacy. The test runs each method with different parameters and prints the corresponding error tables.
    - `k`: A list of values determining different sketch sizes.
    - `m`: A list of values controlling the memory allocation for each method.
    - `e`: Privacy parameter (presumably epsilon, controlling differential privacy strength).

    For each combination of `k` and `m`, the script runs the three private sketching methods and prints their respective error tables.
    """
    # Define the parameters
    k_values = [16, 128, 128, 1024, 32768]
    m_values = [16, 16, 1024, 256, 256]
    
    # Privacy parameter
    e = 150

    df = generate_dataset('normal', 50000)

    results = []

    for j in range(len(k_values)):
        k = k_values[j]
        m = m_values[j]

        print(f"\n================== k: {k}, m: {m} ==================")

        print(" \n========= CMS ==========")

        _, _, error_table, _, _= run_private_cms_client(k, m, e, df)
        df_error_table = pd.DataFrame(error_table, columns=["Metric", "Value"])
        df_error_table["Value"] = df_error_table["Value"].str.replace('%', '').astype(float, errors='ignore')
        mean_error_value_1 = df_error_table[df_error_table["Metric"] == "Percentage Error"]["Value"].values[0]
        print(" \n========= HCMS ===========")
        _, _, error_table, _, _ = run_private_hcms_client(k, m, e, df)
        df_error_table = pd.DataFrame(error_table, columns=["Metric", "Value"])
        df_error_table["Value"] = df_error_table["Value"].str.replace('%', '').astype(float, errors='ignore')
        mean_error_value_2 = df_error_table[df_error_table["Metric"] == "Percentage Error"]["Value"].values[0]

        results.append(["CMS", k, m, mean_error_value_1])
        results.append(["HCMS", k, m, mean_error_value_2])
    
    df_results = pd.DataFrame(results, columns=["Method", "k", "m", "Percentage Error"])

    print("\n\n========= Final Results =========")
    print(tabulate(df_results, headers="keys", tablefmt="grid"))

    # Save the results to a PDF file
    save_table_to_pdf(df_results, "comparison_results.pdf")



if __name__ == '__main__':
    run_comparison_methods()