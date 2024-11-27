
import pandas as pd
import argparse
import os

def convert_excel_to_csv (excel_file, csv_file):
    df = pd.read_excel(excel_file) # Read excel file
    df.to_csv(csv_file, index=False) # Save dataframe to csv

# Preprocess the table with the aoi hits to get 
# if a hit has been made
def aoi_hits(df):
    rows = []
    for _, row in df.iterrows():
        hit = False
        user_id = row['Participant']
        for col in df.columns[1:]:
            if row[col] != "-":
                rows.append({'user_id': user_id, 'value': row[col]})
                hit = True
                break
        if not hit:
            rows.append({'user_id': user_id, 'value': 'No hit'})
    return pd.DataFrame(rows)

# Filter the columns of the csv file
def filter_fixation(df):
    df = df[df['Fixation Position X [px]'] != '-']
    df = df.drop(columns=['Fixation Position X [px]']) 
    df = df.drop(columns=['Fixation Position Y [px]']) 
    return df

# Filter the columns of the csv file
def filter_columns(csv_file, columns):
    df = pd.read_csv(csv_file)
    df_filtered = filter_fixation(df[columns].dropna())
    df_filtered.to_csv(csv_file, index=False) # Save dataframe to csv
    return aoi_hits(df_filtered)

if __name__ == '__main__':  
    parser = argparse.ArgumentParser(description="Preprocess the data")
    parser.add_argument("-d", type=str, required=True, help="Name of the dataset to use")

    args = parser.parse_args()

    fileName = f"{args.d}.xlsx"
    print(f"Preprocessing file: {fileName}")

    excel_file = '../data/raw/' + fileName
    csv_file = '../data/processed/' + fileName.replace('.xlsx', '.csv')
    output_csv = '../data/processed/' + fileName.replace('.xlsx', '_filtered.csv')

    columns = [
        'Participant', 
        'Fixation Position X [px]',
        'Fixation Position Y [px]',
        'AOI Name',
    ]

    # Convert excel to csv
    convert_excel_to_csv(excel_file, csv_file)

    # Filter columns
    df_filtered = filter_columns(csv_file, columns)

    # Change column names
    df_filtered.columns = ['user_id', 'value']

    # Save the filtered file
    df_filtered.to_csv(output_csv, index=False)
    print(f"Filtered file saved in: {output_csv}")