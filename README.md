# Privacidad_Local
This repository contains an adaption of differential privacy algorithms on learning analitics

## Repository Structure
```
Local_Privacy
│
├── data/                # Data Archive
│   ├── raw/             # Original Data (Excel, CSV without processing)
│   ├── processed/       # Processed Data
│
├── scripts/             # Scripts para análisis y preprocesamiento
│   ├── preprocess.py    # Preprocesa datos y genera archivo filtrado
│   ├── algorithms.py    # Ejecuta algoritmos importados
│
├── sketching-algorithms/  # Privacy code
│   ├── Private Count Mean/   # Código del repositorio original
|   ├── Private Hadmard Count Mean/
|   ├── RAPPOR/
│
├── requirements.txt     # Project dependencies
```
