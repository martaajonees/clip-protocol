
import pandas as pd
from rich.progress import Progress
from colorama import Style
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
    def __init__(self, df, type="individual"):
        """
        Initializes the DataProcessor with the dataset name and determines file paths.
        
        Args:
            dataset_name (str): Name of the dataset file (without extension).
        """
        self.columns = ['Participant', 'Fixation Position X [px]', 'Fixation Position Y [px]', 'AOI Name']
        self.df = df
        self.type = type

    def aoi_hits(self):
        """
        Processes the dataset to determine whether an AOI (Area of Interest) hit has been made.
        Extracts relevant user IDs and the first AOI hit for each participant.
        """
        rows = []
        with Progress() as progress:
            task = progress.add_task("[cyan]🔍 Processing AOI Hits...", total=len(self.df))
            for _, row in self.df.iterrows():
                user_id = row['Participant']
                for col in self.df.columns[1:]:
                    if row[col] != "-":
                        if self.type == "general":
                            rows.append({'user_id': user_id, 'values': row[col]})
                        else:
                            rows.append({'user_id': user_id, 'value': row[col]})
                        break
                progress.update(task, advance=1)
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

def run_data_processor(df):
    """
    Runs the data processing pipeline for a given dataset.
    
    Args:
        dataset_name (str): Name of the dataset file (without extension).
    
    Returns:
        pd.DataFrame: The filtered dataset.
    """
    processor = DataProcessor(df)
    df = processor.filter_columns()
    return df

def run_data_processor_general(df):
    """
    Runs the data processing pipeline for a given dataset.
    
    Args:
        dataset_name (str): Name of the dataset file (without extension).
    
    Returns:
        pd.DataFrame: The filtered dataset.
    """
    processor = DataProcessor(df, "general")
    df = processor.filter_columns()
    return df
