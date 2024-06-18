import pandas as pd

def get_metadata_of_df(df):
    # Function to get dataframe containing the metadata of the input dataframe
    # should be of type columnname, datatype, count_of_unique_values
    metadata = []
    for col in df.columns:
        metadata.append([col, df[col].dtype, len(df[col].unique())])
    return pd.DataFrame(
        metadata, columns=["Column Name", "Data Type", "Count of Unique Values"]
    )
