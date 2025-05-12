import os

def generate_latex_line_plot(error_history, output_path="figures/error_plot.tex"):
    """
    Generates a LaTeX TikZ/PGFPlots line plot for multiple error metrics.

    Parameters:
        error_history (dict): Dictionary with structure {metric_name: [(epsilon, error), ...]}
        output_path (str): Path where the LaTeX file will be saved.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

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
