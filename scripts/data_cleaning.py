import pandas as pd

class DataFrameCleaner:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with a pandas DataFrame.
        """
        self.df = df

    def clean_null_values(self):
        """
        Replace NaN values with 'no <column name>' in all columns.
        """
        for column in self.df.columns:
            self.df[column] = self.df[column].fillna(f'no {column}')
        return self.df
