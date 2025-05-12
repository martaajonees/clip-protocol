import pandas as pd
import os

csv_path = 'datasets/aoi-hits-2500.xlsx'
df = pd.read_excel(csv_path)
num_aois = 5

aoi_counts = df['aoi_hit'].value_counts().sort_index()

# Generar líneas del código TikZ
tikz_lines = [
    r"\begin{figure}[h]",
    r"\centering",
    r"\begin{tikzpicture}",
    r"\begin{axis}[",
    r"    x tick label style={rotate=45, anchor=east},",
    r"    ylabel=Frecuencia,",
    r"    xlabel=Áreas de interés,",
    r"    enlargelimits=0.05,",
    r"    legend style={at={(0.5,-0.1)}, anchor=north,legend columns=-1},",
    r"    ybar,",
    r"    bar width=15pt,",
    "    symbolic x coords={" + ",".join([f"$\\text{{AOI}}_{{{i}}}$" for i in range(num_aois)]) + "},",
    r"    xtick=data",
    r"]",
    r"\addplot coordinates {"
]

# Añadir coordenadas
for i, count in zip(range(num_aois), aoi_counts.values):
    tikz_lines.append(f"    ($\\text{{AOI}}_{{{i}}}$, {count})")

tikz_lines.append(r"};")
tikz_lines.append(r"\end{axis}")
tikz_lines.append(r"\end{tikzpicture}")
tikz_lines.append(r"\end{figure}")

# Guardar en archivo
output_dir = 'figures'
os.makedirs(output_dir, exist_ok=True)
with open(os.path.join(output_dir, 'aoi_hits_distribution.tex'), 'w') as f:
    f.write("\n".join(tikz_lines))

print("Archivo LaTeX generado en: figures/aoi_hits_distribution.tex")
