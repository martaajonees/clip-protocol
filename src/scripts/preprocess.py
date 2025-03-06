
import pandas as pd
import argparse
from tqdm import tqdm
import os

class DataProcessor:
    """
    Processes an Excel dataset containing eye-tracking data, filters relevant columns, 
    and extracts fixation and AOI (Area of Interest) hit information.
    
    Attributes:
        file_name (str): Name of the dataset file.
        columns (list): Relevant columns to extract from the dataset.
        df (pd.DataFrame): Dataframe holding the dataset.
        excel_file (str): Path to the input Excel file.
        output_csv (str): Path to save the filtered CSV file.
    """
    def __init__(self, dataset_name):
        """
        Initializes the DataProcessor with the dataset name and determines file paths.
        
        Args:
            dataset_name (str): Name of the dataset file (without extension).
        """
        self.file_name = f"{dataset_name}.xlsx"
        self.columns = ['Participant', 'Fixation Position X [px]', 'Fixation Position Y [px]', 'AOI Name']
        self.df = None

        base_path_1 = os.path.join('..', '..', 'data', 'raw')
        base_path_2 = os.path.join('..', 'data', 'raw')

        self.excel_file = os.path.join(base_path_1, self.file_name) if os.path.exists(base_path_1) else os.path.join(base_path_2, self.file_name)
        self.output_csv = os.path.join(base_path_1.replace('raw', 'filtered'), self.file_name.replace('.xlsx', '_filtered.csv')) if os.path.exists(base_path_1) else os.path.join(base_path_2.replace('raw', 'filtered'), self.file_name.replace('.xlsx', '_filtered.csv'))


    def load_excel(self):
        """
        Loads the Excel file into a Pandas DataFrame.
        """
        self.df = pd.read_excel(self.excel_file)
        print("Excel file loaded")

    def aoi_hits(self):
        """
        Processes the dataset to determine whether an AOI (Area of Interest) hit has been made.
        Extracts relevant user IDs and the first AOI hit for each participant.
        """
        rows = []
        for _, row in tqdm( self.df.iterrows(), total=len(self.df), desc="Processing AOI Hits"):
            hit = False
            user_id = row['Participant']
            for col in self.df.columns[1:]:
                if row[col] != "-":
                    rows.append({'user_id': user_id, 'value': row[col]})
                    hit = True
                    break
            # if not hit:
            #     rows.append({'user_id': user_id, 'value': 'No hit'})
        self.df = pd.DataFrame(rows)

    def filter_fixation(self):
        """
        Removes rows where fixation position data is missing.
        Drops unnecessary fixation position columns after filtering.
        """
        self.df = self.df[self.df['Fixation Position X [px]'] != '-']
        self.df = self.df.drop(columns=['Fixation Position X [px]', 'Fixation Position Y [px]'])

    def filter_columns(self):
        """
        Filters and preprocesses the dataset by keeping only relevant columns,
        removing missing values, filtering fixation positions, and processing AOI hits.
        
        Returns:
            pd.DataFrame: Processed and filtered DataFrame.
        """
        self.df = self.df[self.columns].dropna()
        self.filter_fixation()
        self.aoi_hits()
        return self.df

def run_data_processor(d):
    """
    Runs the data processing pipeline for a given dataset.
    
    Args:
        dataset_name (str): Name of the dataset file (without extension).
    
    Returns:
        pd.DataFrame: The filtered dataset.
    """
    processor = DataProcessor(d)
    processor.load_excel()
    df = processor.filter_columns()
    return df
