import os
import pandas as pd
from collections import Counter
from glob import glob

def filter_databases(excel_files, field):
    excels = []
    for excel_file in excel_files:
        try:
            df_temp = pd.read_excel(excel_file)
            if any(col.startswith("Unnamed") for col in df_temp.columns):
                df = pd.read_excel(excel_file, header=1)  
            else:
                df = df_temp

            matching_columns = [col for col in field if col in df.columns]
            if not matching_columns:
                print(f"⚠️ Ninguna de las columnas especificadas está en {excel_file}")
                continue
            
            df = df[matching_columns].copy()
            df.columns = ["value"]

            df['value'] = df['value'].astype(str).apply(lambda x: x.strip())
            df = df[df['value'] != '-']
            df = df[df['value'].str.contains(r'\w', na=False)]
            filename = os.path.basename(excel_file)

            excels.append((df, filename))

        except Exception as e:
            print(f"❌ Error leyendo {excel_file}: {e}")
        print(f"✅ Procesado {excel_file} correctamente.")
    return excels

def compute_real_frequencies(df: pd.DataFrame):
    counter = Counter(df['value'])
    freq_df = pd.DataFrame(counter.items(), columns=["Element", "Frequency"]).sort_values(by="Frequency", ascending=False)
    return freq_df.reset_index(drop=True)

if __name__ == "__main__":
    carpeta_excel = "/Users/martajones/Downloads/Databases"
    campos_a_contar = ["AOI Name", "AOI name", "AOI_Name"]  # por si varía el nombre

    archivos_excel = glob(os.path.join(carpeta_excel, "*.xlsx"))
    dfs = filter_databases(archivos_excel, campos_a_contar)

    if not dfs:
        print("No se han encontrado datos válidos.")
        exit()

    all_freqs = []
    for df, filename in dfs:
        counts = df['value'].value_counts()
        for value, freq in counts.items():
            all_freqs.append({
                "Archivo": filename,
                "Campo": value,
                "Frecuencia": freq
            })

    df_all_freqs = pd.DataFrame(all_freqs)
    df_all_freqs = df_all_freqs.sort_values(by=["Archivo", "Frecuencia"], ascending=[True, False])
    df_all_freqs.to_csv("frecuencias_por_archivo.csv", index=False)


