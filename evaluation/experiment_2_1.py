
import pandas as pd
import os
import sys
from tabulate import tabulate
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import load_setup_json, display_results, get_real_frequency
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

privacy_method = "PHCMSrec" 

def filter_dataframe(df):
    df.columns = ["user", "value"]
    return df

def run_command(e, k, m, df):
    if privacy_method == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)
    
    error = compute_error_table(get_real_frequency(df), df_estimated, 2)
    table = display_results(get_real_frequency(df), df_estimated)
    return error, df_estimated, table


def run_experiment_2(datasets):
    k = 348
    m = 128
    e_r = 10

    headers=[
                "Element", "Real Frequency", "Real Percentage", 
                "Estimated Frequency", "Estimated Percentage", "Estimation Difference", 
                "Percentage Error"
            ]

    tables = []
    
    for data in datasets:
        data.columns = ["user", "value"]
        data = filter_dataframe(data)
        error, _, table = run_command(e_r, k, m, data)
        tables.append(table)
        print(f"Dataset size: {len(data)}")
        print(tabulate(table, headers=headers, tablefmt="fancy_grid"))
    

def plot_relative_errors_multiple_tables(tables, dataset_sizes, output_path="figures/plot_experiment_2.tex"):
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Extraer labels y errores
    all_errors = {}  # {AOI_label: {dataset_size: error_value}}

    for table, size in zip(tables, dataset_sizes):
        for row in table:
            aoi_index = row[0].split("_")[-1]
            aoi_label = f"$AOI_{{{aoi_index}}}$"
            error_percent = float(row[-1].strip('%'))
            if aoi_label not in all_errors:
                all_errors[aoi_label] = {}
            all_errors[aoi_label][size] = error_percent

    # Generar código TikZ
    tikz_lines = [
        r"\begin{figure}[h]",
        r"\centering",
        r"\begin{tikzpicture}",
        r"\begin{axis}[",
        r"    ybar,",
        r"    bar width=10pt,",
        r"    ylabel={Error porcentual (\%)},",
        r"    xlabel={Áreas de Interés},",
        r"    symbolic x coords={" + ", ".join(all_errors.keys()) + "},",
        r"    xtick=data,",
        r"    x tick label style={rotate=45, anchor=east},",
        r"    ymin=0,",
        r"    enlarge x limits=0.15,",
        r"    legend style={at={(0.5,-0.2)}, anchor=north,legend columns=-1},",
        r"    legend cell align={left}",
        r"]"
    ]

    # Añadir un \addplot por cada dataset
    for size in dataset_sizes:
        tikz_lines.append(r"\addplot coordinates {")
        for aoi_label in all_errors:
            value = all_errors[aoi_label].get(size, 0)
            tikz_lines.append(f"({aoi_label}, {value})")
        tikz_lines.append("};")

    legend_entries = [f"{size} muestras" for size in dataset_sizes]
    tikz_lines.append(r"\legend{" + ", ".join(legend_entries) + "}")
    tikz_lines.append(r"\end{axis}")
    tikz_lines.append(r"\end{tikzpicture}")
    tikz_lines.append(r"\caption{Errores porcentuales por AOI en distintos tamaños de dataset}")
    tikz_lines.append(r"\end{figure}")

    with open(output_path, "w") as f:
        f.write("\n".join(tikz_lines))

    print(f"Gráfico LaTeX generado en: {output_path}")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 3")
    parser.add_argument("-d1", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()

    data_path = args.d1 # folder

    datasets = []
    for file in os.listdir(data_path):
        if file.endswith(".xlsx"):
            filepath = os.path.join(data_path, file)
            print(f"File: {filepath}")
            df = pd.read_excel(os.path.join(data_path, file))
            datasets.append(df)

    run_experiment_2(datasets)