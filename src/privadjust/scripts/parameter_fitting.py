
import optuna
from colorama import Fore, Style
from tabulate import tabulate

from privadjust.count_mean.private_cms_client import run_private_cms_client
from privadjust.hadamard_count_mean.private_hcms_client import run_private_hcms_client

class PrivacyUtilityOptimizer:
    """
    Optimizes the privacy-utility tradeoff by tuning the privacy parameter `e`.
    
    Attributes:
        df (pd.DataFrame): Input dataset containing values to be privatized.
        algorithm (str): Selected privacy algorithm (1 for CMS, 2 for HCMS).
        k (int): Parameter k for the selected algorithm.
        m (int): Parameter m for the selected algorithm.
        real_frequency (pd.DataFrame): True frequency distribution of elements in `df`.
        N (int): Total count of elements in `df`.
        headers (list): Column headers for displaying tabular results.
    """
    def __init__(self, df, k, m, algorithm):
        """
        Initializes the PrivacyUtilityOptimizer class with dataset and algorithm parameters.

        Args:
            df (pd.DataFrame): Input dataset.
            k (int): Parameter k for the selected algorithm.
            m (int): Parameter m for the selected algorithm.
            algorithm (str): Algorithm choice (1 for CMS, 2 for HCMS).
        """
        self.df = df
        self.algorithm = algorithm
        self.k = k
        self.m = m

        self.real_frequency = self.get_real_frequency()
        self.N = self.real_frequency['Frequency'].sum()
        self.headers =[ "Element", "Real Frequency", "Real Percentage", "Estimated Frequency", "Estimated Percentage", "Estimation Difference", "Percentage Error"]
    

    def function_LP(self, f_estimated, f_real, p):
        """
        Computes the Lp norm error between estimated and real frequencies.
        
        Args:
            f_estimated (pd.DataFrame): Estimated frequency distribution.
            f_real (pd.DataFrame): Real frequency distribution.
            p (float): Order of the Lp norm.
        
        Returns:
            float: Computed Lp error.
        """
        merged = f_estimated.merge(f_real, on="Element", suffixes=("_estimated", "_real"))
        return (1 / self.N) * sum(abs(row["Frequency_estimated"] - row["Frequency_real"]) ** p for _, row in merged.iterrows())

    def run_command(self, e):
        """
        Runs the selected privacy algorithm with a given privacy budget `e`.
        
        Args:
            e (float): Privacy parameter.
        
        Returns:
            tuple: Containing result, data table, error table, privatized data, and estimated frequencies.
        """
        if self.algorithm == '1':
            result, data_table, error_table, privatized_data, df_estimated = run_private_cms_client(self.k, self.m, e, self.df)
        elif self.algorithm == '2':
            result, data_table, error_table, privatized_data, df_estimated = run_private_hcms_client(self.k, self.m, e, self.df)
        
        self.frequency_estimation = df_estimated
        return result, data_table, error_table, privatized_data

    def get_real_frequency(self):
        """
        Computes the real frequency distribution from the dataset.
        
        Returns:
            pd.DataFrame: DataFrame with element frequencies.
        """
        count = self.df['value'].value_counts().reset_index()
        return count.rename(columns={'value': 'Element', 'count': 'Frequency'})

    def frequencies(self):
        """
        Returns both the estimated and real frequency distributions.
        
        Returns:
            tuple: Estimated frequency and real frequency DataFrames.
        """
        return self.frequency_estimation, self.get_real_frequency()

    def optimize_e_with_optuna(self, target_error, p, metric, n_trials):
        """
        Optimizes the privacy parameter `ϵ` using Optuna to reach a target error.
        
        Args:
            target_error (float): Desired error value.
            p (float): Order of the Lp norm.
            metric (str): Metric type (1 = MSE, 2 = Lp norm, 3 = Percentage Error).
        
        Returns:
            tuple: Best `ϵ`, privatized data, error table, result, and data table.
        """
        def objective(trial):
            e = trial.suggest_float('e', 0.01, 20, step = 0.01)
            result, data_table, error_table, privatized_data = self.run_command(e)

            trial.set_user_attr('result', result)
            trial.set_user_attr('privatized_data', privatized_data)
            trial.set_user_attr('error_table', error_table)
            trial.set_user_attr('data_table', data_table)

            print(tabulate(data_table, headers=self.headers, tablefmt="grid"))
    
            if metric == "1" or metric == "2":
                Lp_target = self.function_LP(self.frequency_estimation, self.get_real_frequency(), p)
            elif metric == "3":
                Lp_target = (self.function_LP(self.frequency_estimation, self.get_real_frequency(), p) / self.N) * 100
            
            # Minimize the diference: LP - target_error
            return abs(Lp_target - target_error)

        study = optuna.create_study(direction='minimize') # minimize the difference
        study.optimize(objective, n_trials=n_trials)

        best_e = study.best_params['e']
        privatized_data = study.best_trial.user_attrs['privatized_data']
        error_table = study.best_trial.user_attrs['error_table']
        result = study.best_trial.user_attrs['result']
        data_table = study.best_trial.user_attrs['data_table']

        print("\n================ e Optimization finished ====================")
        print(f"Best value of ϵ: {best_e}")
        print(f"Closest error (LP - target_error): {study.best_value}")
        
        return best_e, privatized_data, error_table, result, data_table

    def utility_error(self, Lp, p, metric, n_trials=20):
        """
        Optimizes the privacy parameter `ϵ` for utility preservation.
        
        Args:
            Lp (float): Target error value.
            p (float): Order of the Lp norm.
            metric (str): Metric type (1 = MSE, 2 = Lp norm, 3 = Percentage Error).
        
        Returns:
            tuple: Optimized `ϵ`, result, and privatized data.
        """
        e, privatized_data, error_table, result, data_table = self.optimize_e_with_optuna(Lp, p, metric, n_trials) # Adjust the value of e to reach the desired error

        print(tabulate(data_table, headers=self.headers, tablefmt="fancy_grid")) # Show database with the e

        option = input("Are you satisfied with the results? (yes/no): ") # Ask the user if he is satisfied with the results
        if option == "no":
            self.utility_error(Lp, p, metric)
        else:
            print(f"\nError metrics for parameters k={self.k}, m={self.m} and ϵ={e}")
            print(tabulate(error_table, tablefmt="fancy_grid"))

        return e, result, privatized_data, data_table

    def privacy_error(self):
        """
        Optimizes the privacy parameter `e` for privacy preservation.
        
        Returns:
            tuple: Optimized `e`, result, and privatized data.
        """
        from privadjust.main.individual_method import run_individual_method
        
        p = float(input("\n→ Enter the type of error ρ: "))

        error_table = []
        error_table_fav = []
        privatized_fav = None

        while True:
            e_min = input(f"→ Enter the {Style.BRIGHT}minimum{Style.RESET_ALL} value of ϵ: ")
            e_max = input(f"→ Enter the {Style.BRIGHT}maximum{Style.RESET_ALL} value of ϵ: ")
            step = input(f"→ Enter the {Style.BRIGHT}step{Style.RESET_ALL} value: ")

            saved_e = 0

            for e in range(int(e_min), int(e_max), int(step)): # Optimize e
                result, data_table, error_table, privatized_data = self.run_command(e)
                f_estimated, f_real = self.frequencies()
                error = self.function_LP(f_estimated, f_real, p)

                print(f"\nError for ϵ = {e}: {error}")
                print(tabulate(data_table, headers=self.headers, tablefmt="grid"))

                save = input("Do you want to save this privatized values? (yes/no): ")
                if save == "yes":
                    saved_e = e
                    H_fav = result
                    error_table_fav = error_table
                    privatized_fav = privatized_data
            print(f"\nOptimization finished:{Fore.RED} What do you want to do?{Style.RESET_ALL}")
            choice = input("\n1. Change e\n2. Change k or m\n3. Continue\nSelect: ")
            if choice == "2":
                run_individual_method(self.df, 2)
                break
            elif choice == "3":
                break
        
        if saved_e == 0:
            e = input("Enter the value of ϵ to use: ")
            
            H_fav, data_table, error_table_fav, privatized_fav = self.run_command(e)
            print(tabulate(data_table, headers=self.headers, tablefmt="fancy_grid")) # Show database with the e
        else:
            print(f"Using the saved value of ϵ: {saved_e}")

        option = input("Are you satisfied with the results? (yes/no): ")
        if option == "no":
            self.privacy_error()
        else:
            print(f"\nError metrics for k={self.k}, m={self.m}, e={saved_e}")
            print(tabulate(error_table_fav, tablefmt="pretty"))

            print("\nSending database to server ...")
        return saved_e, H_fav, privatized_fav

    def run(self):
        """
        Main execution function. Asks the user to choose between utility and privacy optimization.
        
        Returns:
            tuple: Optimized `e`, result, and privatized data.
        """
        e = 0
        choice = input("Enter the optimization:\n1. Utility\n2. Privacy\nSelect: ")
        if choice == "1":
            print(f"\n{Fore.GREEN}🔎 Optimizing ϵ for utility ...{Style.RESET_ALL}")
            metric = input("Enter the metric to optimize \n1. MSE\n2. LP\n3. Porcentual Error \nSelect: ")
            if metric == "1":
                Lp = float(input("Enter the MSE to reach: "))
                p = 2
            elif metric == "2":
                Lp = float(input("Enter the Lp to reach: "))
                p = float(input("Enter the type of error (p): "))
            elif metric == "3":
                Lp = float(input("Enter the Porcentual Error to reach: "))
                p = 1
            n_trials = int(input("Enter the number of trials: "))
            e, result, privatized_data, _ = self.utility_error(Lp, p, metric, n_trials)
        elif choice == "2":
            print(f"\n{Fore.GREEN}🔎 Optimizing ϵ for privacy ...{Style.RESET_ALL}")
            e, result, privatized_data = self.privacy_error()
        else:
            print("Invalid choice. Please try again.")
        return e, result, privatized_data

    
def run_parameter_fitting(df, k, m, algorithm):
    """
    Initializes and runs the PrivacyUtilityOptimizer with the given parameters.
    
    Args:
        df (pd.DataFrame): Input dataset.
        k (int): Parameter k for the selected algorithm.
        m (int): Parameter m for the selected algorithm.
        algorithm (str): Algorithm choice (1 for CMS, 2 for HCMS).
    
    Returns:
        tuple: Optimized `e`, result, and privatized data.
    """
    optimizer = PrivacyUtilityOptimizer(df, k, m, algorithm)
    e, result, privatized_data = optimizer.run()
    return e, result, privatized_data

    

