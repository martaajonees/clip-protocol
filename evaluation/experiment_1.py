import pandas as pd
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from clip_protocol.utils.utils import get_real_frequency, load_setup_json
from clip_protocol.utils.errors import compute_error_table
from clip_protocol.count_mean.private_cms_client import run_private_cms_client
from clip_protocol.hadamard_count_mean.private_hcms_client import run_private_hcms_client

privacy_method = "PHCMS"  # or "PCMeS"

def filter_dataframe(df):
    df.columns = ["user", "value"]
    N = len(df)
    return df, N

def run_command(e, k, m, df):
    if privacy_method == "PCMeS":
        _, _, df_estimated = run_private_cms_client(k, m, e, df)
    elif privacy_method == "PHCMS":
        _, _, df_estimated = run_private_hcms_client(k, m, e, df)
    
    error = compute_error_table(get_real_frequency(df), df_estimated, 2)
    return error, df_estimated


def generate_latex_line_plot(error_history, output_path="figures/plot_experiment_1.tex"):
    tikz_lines = [
        r"\begin{figure}[h]",
        r"\centering",
        r"\begin{tikzpicture}",
        r"\begin{axis}[",
        r"    xlabel={$\epsilon$},",
        r"    ylabel={Error},",
        r"    legend style={at={(0.5,-0.15)}, anchor=north,legend columns=-1},",
        r"    xmin=0,",
        r"    grid=major,",
        r"    width=12cm,",
        r"    height=8cm,",
        r"    cycle list name=color list,",
        r"]"
    ]

    for metric, values in error_history.items():
        if metric == "Lρ Norm":
            metric = "Lp Norm"
        tikz_lines.append(r"\addplot coordinates {")
        for epsilon, error in sorted(values):
            tikz_lines.append(f"    ({epsilon}, {error})")
        tikz_lines.append(r"};")
        tikz_lines.append(fr"\addlegendentry{{{metric}}}")

    tikz_lines += [
        r"\end{axis}",
        r"\end{tikzpicture}",
        r"\caption{Evolución del error por métrica en función del parámetro $\epsilon$}",
        r"\end{figure}"
    ]

    with open(output_path, "w") as f:
        f.write("\n".join(tikz_lines))

    print(f"✅LaTeX graph generated in: {output_path}")

def run_experiment1(df):
    k, m,  _, _,  _,  _,  _,  _,  _,  _ = load_setup_json()
    error_history = {}
    df, _ = filter_dataframe(df)

    er = 10
    while er >= 0.5:
        error_table, _ = run_command(er, k, m, df)

        for metric, value in error_table:
            if metric not in error_history:
                error_history[metric] = []
            error_history[metric].append((er, value))

        er -= 0.5
    
    generate_latex_line_plot(error_history)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment 1")
    parser.add_argument("-i", type=str, required=True, help="Path to the input excel file")
    args = parser.parse_args()
    if not os.path.isfile(args.i):
        print(f"❌ File not found: {args.i}")
        sys.exit(1)

    df_temp = pd.read_excel(args.i)

    if any(col.startswith("Unnamed") for col in df_temp.columns):
        df = pd.read_excel(args.i, header=1)  
    else:
        df = df_temp

    run_experiment1(df)