import os
import glob
import re
import pandas as pd
import random
import string
import hashlib


# ID único que quieres usar
UNIQUE_USER_ID= ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


# Buscar todos los archivos xlsx en el directorio actual
files = glob.glob("*.xlsx")

for file in files:
    print(f"Procesando {file}...")
    
    # Leer el Excel
    df = pd.read_excel(file)
    
    # 1️⃣ Cambiar todos los user_id a uno único
    if "user_id" in df.columns:
        df["user_id"] = UNIQUE_USER_ID
    else:
        print(f"⚠️  No se encontró columna 'user_id' en {file}")
    
    # 2️⃣ Renombrar la segunda columna a 'events'
    if len(df.columns) >= 2:
        cols = list(df.columns)
        cols[1] = "events"
        df.columns = cols
    else:
        print(f"⚠️  El archivo {file} no tiene al menos 2 columnas")
    
    # 3️⃣ Reemplazar subevent_X → eX dentro de la columna events
    if "events" in df.columns:
        df["events"] = df["events"].astype(str).apply(
            lambda x: re.sub(r"subevent_(\d+)", r"e\1", x)
        )
    
    # Guardar sobrescribiendo el archivo
    df.to_excel(file, index=False)

print("✅ Procesamiento terminado.")
