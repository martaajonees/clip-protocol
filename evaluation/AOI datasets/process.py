import pandas as pd
import glob
import os

# Carpeta actual donde está el script
current_folder = os.getcwd()

# Buscar todos los archivos .xlsx en la carpeta actual
xlsx_files = glob.glob(os.path.join(current_folder, "*.xlsx"))

for file_path in xlsx_files:
    try:
        # Leer el archivo
        df_temp = pd.read_excel(file_path)

        if any(col.startswith("Unnamed") for col in df_temp.columns):
            df = pd.read_excel(file_path, header=1)  
        else:
            df = df_temp

        # --- MEJORA: Limpiar nombres de columnas ---
        # Eliminamos espacios en blanco extra y pasamos a minúsculas para comparar fácilmente
        df.columns = [str(c).strip() for c in df.columns]
        cols_lower = [c.lower() for c in df.columns]

        # Buscamos los índices de las columnas que necesitamos (sin importar mayúsculas)
        target_p = 'participant'
        target_a = 'aoi hit'

        if target_p in cols_lower and target_a in cols_lower:
            # Identificar los nombres reales de las columnas en este archivo específico
            real_col_p = df.columns[cols_lower.index(target_p)]
            real_col_a = df.columns[cols_lower.index(target_a)]

            # Obtener el nombre del archivo sin extensión para el participante
            participant_name = os.path.splitext(os.path.basename(file_path))[0]

            # Reemplazar valores y filtrar
            df[real_col_p] = participant_name
            
            # Mantener solo las dos columnas y limpiar nulos
            df = df[[real_col_p, real_col_a]]
            df = df[df[real_col_a].notna()]

            # Renombrar a los nombres finales deseados
            df.columns = ['Participant', 'AOI hit']

            # Sobrescribir el archivo original
            df.to_excel(file_path, index=False)
            print(f"✅ Procesado: {os.path.basename(file_path)}")
        else:
            print(f"❌ Columnas no encontradas en {os.path.basename(file_path)}. Columnas detectadas: {list(df.columns)}")

    except Exception as e:
        print(f"⚠️ Error procesando {os.path.basename(file_path)}: {e}")

print("\nProceso finalizado.")