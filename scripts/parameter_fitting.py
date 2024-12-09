import subprocess
import re
import argparse
import random

# Constants
ALGORITHM_PATHS = {
    1: "../src/private_count_mean/private_cms.py",
    2: "../src/private_hadamard_count_mean/private_hcms.py",
}

def parse_results(output):
    """Parse the output of the command and return the percentage error."""
    percentage_error = 0.0

    # Find the percentage error in the output
    match = re.search(r"Percentage Error\s+\|\s+([\d.]+%)", output)
    if match:
        percentage_error = float(match.group(1).replace("%", ""))
    else:
        print("Error: Percentage error not found in the output.")
        
    return percentage_error

def run_command(k, m, e, data_file, algorithm_option):
    """Run the command with given parameters and return results."""
    
    cmd = ["python3", ALGORITHM_PATHS[algorithm_option], 
           "-k", str(k),
           "-m", str(m),
           "-e", str(e),
           "-d", data_file
          ]

    # Run the command and get the output
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return parse_results(result.stdout)

def adaptive_search(data_file, algorithm_option, tolerance, max_iters=20):
    """Adaptive parameter search to minimize error."""

    valid_m_values = [2**i for i in range(4, 8)]
    best_params = {"-k": random.randint(1, 5), "-m": random.choice([32, 64, 128, 256, 512]), "-e": random.uniform(3, 10)}
    best_error = float('inf')

    for iteration in range(max_iters):
        print(f"\nIteration {iteration + 1} of {max_iters}")

        k = max(1, best_params["-k"] + random.choice([-1, 0, 1]))
        m = random.choice(valid_m_values)
        e = max(0.1, best_params["-e"] + random.uniform(-0.5, 0.5))

        # Run the command and get the output
        print(f"Testing with k={k}, m={m}, e={e}")
        result = run_command(k, m, e, data_file, algorithm_option)
        
        if result is not None:
            percentage_error = float(result)
        else:
            print("Error while executing the command.")
            continue

        # Update the best parameters if needed
        if percentage_error < best_error:
            best_error = percentage_error
            best_params = {"-k": k, "-m": m, "-e": e}
            print(f"New best error: {best_error:.2f} with parameters {best_params}")
            
            if best_error <= tolerance:
                print("Tolerance reached.")
                break
    return best_params, best_error

if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Script to find the best parameters for a given algorithm")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset to use")
    parser.add_argument("-o", type=int, choices=[1, 2], required=True, help="Algorithm to use")
    parser.add_argument("-t", type=float, default=0.5, help="Error tolerance to reach")
    args = parser.parse_args()

    # Run the adaptive search
    best_params, best_error = adaptive_search(args.d, args.o, args.t)
    print("\n === Results ===\n")
    print(f"Best parameters: {best_params}")
    print(f"Lowest percentage error: {best_error:.2f}")
