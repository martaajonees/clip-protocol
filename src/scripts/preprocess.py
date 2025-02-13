
import pandas as pd
import argparse
from tqdm import tqdm

class DataProcessor:
    def __init__(self, dataset_name):
        self.file_name = f"{dataset_name}.xlsx"
        self.excel_file = f"../data/raw/{self.file_name}"
        self.output_csv = f"../data/filtered/{self.file_name.replace('.xlsx', '_filtered.csv')}"
        self.columns = ['Participant', 'Fixation Position X [px]', 'Fixation Position Y [px]', 'AOI Name']
        self.df = None

    def load_excel(self):
        print(f"Loading excel file: {self.excel_file}")
        self.df = pd.read_excel(self.excel_file)
        print("Excel file loaded")

    # Preprocess the table with the aoi hits to get if a hit has been made
    def aoi_hits(self):
        rows = []
        for _, row in tqdm( self.df.iterrows(), total=len(self.df), desc="Processing AOI Hits"):
            hit = False
            user_id = row['Participant']
            for col in self.df.columns[1:]:
                if row[col] != "-":
                    rows.append({'user_id': user_id, 'value': row[col]})
                    hit = True
                    break
            #if not hit:
                #rows.append({'user_id': user_id, 'value': 'No hit'})
        self.df = pd.DataFrame(rows)

    def filter_fixation(self):
        self.df = self.df[self.df['Fixation Position X [px]'] != '-']
        self.df = self.df.drop(columns=['Fixation Position X [px]', 'Fixation Position Y [px]'])

    def filter_columns(self):
        self.df = self.df[self.columns].dropna()
        self.filter_fixation()
        self.aoi_hits()

    def save_filtered_csv(self):
        self.df.columns = ['user_id', 'value']
        self.df.to_csv(self.output_csv, index=False)
        print(f"Filtered file saved in: {self.output_csv}")

def run_data_processor(d):  
    processor = DataProcessor(d)
    processor.load_excel()
    processor.filter_columns()
    processor.save_filtered_csv()
