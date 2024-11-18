
import pandas as pd

def convertir_excel_a_csv(archivo_excel, archivo_csv):
    df = pd.read_excel(archivo_excel)
    df.to_csv(archivo_csv, index=False) # Guardar archivo

# Preproceso la tabla con los aoi hits para 
# obtener si se ha hecho un hit
def aoi_hits(df):
    rows = []
    for _, row in df.iterrows():
        hit = False
        user_id = row['Participant name']
        for col in df.columns[1:]:
            if row[col] == 1:
                rows.append({'user_id': user_id, 'value': col})
                hit = True
                break
        if not hit:
            rows.append({'user_id': user_id, 'value': 'No hit'})
    return pd.DataFrame(rows)

def filtrar_fixation(df):
    df = df[df['Eye movement type'] == 'Fixation']
    df = df.drop(columns=['Eye movement type']) # Eliminar la columna Eye movement type
    return df

def filtrar_columnas(archivo_csv, columnas):
    df = pd.read_csv(archivo_csv)
    df_filtrado = filtrar_fixation(df[columnas].dropna())
    df_filtrado.to_csv(archivo_csv, index=False) # Guardar df_filtrado
    return aoi_hits(df_filtrado)

if __name__ == '__main__':  
    archivo_excel = '../data/raw/project.xlsx'
    archivo_csv = '../data/processed/project.xlsx'
    output_csv = '../external/DP-Sketching-Algorithms/utils/datasets/filtrado.csv'

    columnas = [
        'Participant name', 
        'Eye movement type',
        'AOI hit [clase prueba - campus]',
        'AOI hit [clase prueba - conceptos]',
        'AOI hit [clase prueba - locutor]',
        'AOI hit [clase prueba - logo uni]',
    ]

    # Convertir archivo de excel a csv
    convertir_excel_a_csv(archivo_excel, archivo_csv)

    # Filtrar columnas
    df_filtrado = filtrar_columnas(archivo_csv, columnas)

    # Cambiar el nombre de las columnas
    df_filtrado.columns = ['user_id', 'value']

    # Guardar el dataframe en un archivo de csv
    df_filtrado.to_csv(output_csv, index=False)
    print(f"Archivo filtrado guardado en: {output_csv}")