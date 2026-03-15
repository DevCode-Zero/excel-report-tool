import pandas as pd


def aggregate_files(file_paths):

    all_data = []

    for file in file_paths:

        df = pd.read_excel(file, sheet_name="Archer Search Report")

        all_data.append(df)

    combined_df = pd.concat(all_data, ignore_index=True)

    return combined_df