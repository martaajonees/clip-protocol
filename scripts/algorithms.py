import os
import subprocess

def ejecutar_algoritmos(opcion, datosfiltrados):
    directorios = {
        '1': '../external/DP-Sketching-Algorithms/Private Hadmard Count Mean',
        '2': '../external/DP-Sketching-Algorithms/Private Count Mean',
        '3': '../external/DP-Sketching-Algorithms/RAPPOR'
    }

    comandos = {
        '1': ['python3', '-u', 'private_hcms.py', '-k', '10', '-m', '64', '-e', '5.0', '-d', datosfiltrados],
        '2': ['python3', '-u', 'private_cms.py', '-k', '3', '-m', '64', '-e', '0.0001', '-d', datosfiltrados],
        '3': ['python3', '-u', 'rappor.py', '-k', '16', '-h', '4', '-f', '0.25', '-p', '0.4', '-q', '0.6' ,'-d', datosfiltrados]
    }

    # Cambiar al directorio
    os.chdir(directorios[opcion])  

    result = subprocess.run(comandos[opcion], capture_output=True, text=True)  # Ejecutar el comando
    print("Salida del comando:", result.stdout)
    
    if result.stderr:
        print("Error:", result.stderr)

if __name__ == '__main__':
    print("Seleccione el algoritmo:")
    print("1. Private Hadmard Count Mean")
    print("2. Private Count Mean")
    print("3. RAPPOR")
    opcion = input("Opción (1, 2 o 3): ")
    ejecutar_algoritmos(opcion, 'filtrado')