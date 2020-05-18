"""
=====
Saver
=====

Creates and saves the long and short files
"""
import datetime
import os
import pandas as pd
from config import unknown_columns

class Saver:

    def __init__(self, df, data_dir="./output"):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        print(df.LOID.unique())
        self.skills = df['LOID'].drop_duplicates().values
        self.short = self.set_up_short(df)
        self.long = self.set_up_long(df)
        if len(self.short)/3 != len(self.long):
            print(len(self.short), len(self.long), self.long.columns)
            print(self.short['LOID'].drop_duplicates())
            print(self.short.head())
            print(self.short.tail())
            print(len(self.short.loc[self.short['LOID'] == 8232]))
            print(len(self.short.loc[self.short['LOID'] == 8234]))
            print(len(self.short.loc[self.short['LOID'] == 8240]))
            for goal in self.short['LOID'].unique():
                for user in self.long.UserId.values:
                    if user not in \
                            self.short.loc[self.short['LOID'] == goal].values:
                        print(f"missing user {user} in goal {goal}")
            print(self.skills)
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
        print(f"Saving to directory {self.data_dir}")
        datenow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.short.to_csv(f"{self.data_dir}\\{f_name}_short_{datenow}.csv",
                          na_rep=999)
        self.long.to_csv(f"{self.data_dir}\\{f_name}_long_{datenow}.csv",
                         na_rep=999)
        self.short.to_excel(f"{self.data_dir}\\{f_name}_short_{datenow}.xlsx",
                            na_rep=999)
        self.long.to_excel(f"{self.data_dir}\\{f_name}_long_{datenow}.xlsx",
                           na_rep=999)


