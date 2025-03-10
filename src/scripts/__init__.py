"""
This module initializes the Local_Privacy package and defines the main imports
required to use the local differential privacy functionalities.

The Local_Privacy package contains implementations of differential privacy algorithms
designed to protect user data privacy while maintaining the utility of aggregated data.
The algorithms are organized into different modules and subpackages for ease of use and extensibility.

Main Modules:
- individual_method.py: Implements the algorithm for single-user datasets.
- general_method.py: Implements the algorithm for multi-user datasets.

Subpackages:
- private_count_mean: Contains algorithms for private count mean calculations.
- private_hadamard_count_mean: Implements private count mean algorithms using the Hadamard transform.
- rappor: Contains the implementation of the RAPPOR algorithm for local differential privacy.

Usage:
    from Local_Privacy import individual_method, general_method
    from Local_Privacy.private_count_mean import PrivateCountMean

Example:
    # To use the individual method
    from Local_Privacy import individual_method
    result = individual_method.process_data(data)

    # To use the general method
    from Local_Privacy import general_method
    result = general_method.aggregate_data(data)
"""