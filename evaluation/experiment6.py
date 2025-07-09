import subprocess
import sys
import os
import argparse

def run_experiment_6(df_path):
    # Ejecutar 'aggregate'
    print("🚀 Ejecutando 'aggregate' desde consola...")
    result = subprocess.run(["aggregate", "-d", df_path])
    if result.returncode != 0:
        print("❌ Error ejecutando 'aggregate'")
        sys.exit(1)

    # Ejecutar 'estimate' y guardar salida en archivo y por pantalla
    print("📊 Ejecutando 'estimate' y guardando resultados...")
    output_path = "figures/experiment6_estimate.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        process = subprocess.Popen(
            ["estimate"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in process.stdout:
            print(line, end="")  # Imprime en terminal
            f.write(line)        # Guarda en archivo
        process.wait()
        if process.returncode != 0:
            print("❌ Error ejecutando 'estimate'")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Run experiment 6 combining 'aggregate' and 'estimate'")
    parser.add_argument("-d", type=str, required=True, help="Path to the input CSV file")
    args = parser.parse_args()

    if not os.path.isfile(args.d):
        print(f"❌ File not found: {args.d}")
        sys.exit(1)

    run_experiment_6(args.d)

if __name__ == "__main__":
    main()
