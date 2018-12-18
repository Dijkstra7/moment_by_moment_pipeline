"""
=====
Saver
=====

Creates and saves the long and short files
"""
import os
import pandas as pd
from config import unknown_columns

class Saver:

    def __init__(self, df, data_dir="./output"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        self.skills = df['LOID'].drop_duplicates().values
        self.short = self.set_up_short(df)
        self.long = self.set_up_long(df)
        if len(self.short)/3 != len(self.long):
            print(len(self.short), len(self.long))
            print(self.short['LOID'].drop_duplicates())
            raise ValueError

    def set_up_short(self, df):
        """
        Set up the skeleton for the short file
        Parameters
        ----------
        df: pandas.DataFrame
            Will be the basis of the short file

        Returns
        -------
        pandas.DataFrame
            The basis for the short file
        """
        short = df[['UserId', 'LOID']].copy()
        short.drop_duplicates(inplace=True)
        short = short.sort_values(by=["LOID", "UserId"])
        short.reset_index(drop=True, inplace=True)
        return short

    def set_up_long(self, df):
        """
        Set up the skeleton for the long file
        Parameters
        ----------
        df: pandas.DataFrame
            Will be the basis of the long file

        Returns
        -------
        pandas.DataFrame
            The basis for the long file
        """
        long = df[['UserId']].copy()
        long.drop_duplicates(inplace=True)
        long = long.sort_values(by='UserId')
        long.reset_index(drop=True, inplace=True)
        return long

    def save(self, f_name):
        self.short.to_excel(f"{self.data_dir}\{f_name}_short.xlsx", na_rep=999)
        self.long.to_excel(f"{self.data_dir}\{f_name}_long.xlsx", na_rep=999)
        self.short.to_csv(f"{self.data_dir}\{f_name}_short.csv", na_rep=999)
        self.long.to_csv(f"{self.data_dir}\{f_name}_long.csv", na_rep=999)
        

