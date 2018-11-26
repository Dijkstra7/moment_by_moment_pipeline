"""
======
Loader
======

Loads the data.
"""
import pandas as pd
from datetime import datetime


class DataLoader:

    def __init__(self, f_name=None, s_name=None):
        self.file_name = f_name or "./res/resultaten-radboud-all_anoniem " \
                                   "samengevoegd_editforfirstattempts.xlsx"
        self.sheetname = s_name or "AllData"
        self.data = None

    def load(self, from_csv=False):
        if from_csv is True:
            data = pd.read_csv(self.file_name, infer_datetime_format=True)
        else:
            data = pd.read_excel(self.file_name, sheet_name=self.sheetname)
        data.rename(columns={"LearningObjectiveId": "LOID"}, inplace=True)
        self.data = data
        return data

    # def read_date(self, lst):
    #     for n, i in enumerate(lst):
    #         if not isinstance(i, datetime):
    #             if i is None:
    #                 continue
    #             hour, minute, second = [int(j) for j in i.split('.')[0].split(
    #                 ":")]
    #             microsecond = int(i.split('.')[1]) * 1000
    #             print("changing:", i)
    #             lst[n] = datetime(2018, 1, 1, hour, minute, second,
    #                               microsecond)
    #             print("into:", lst[n])
    #     print(lst[0].dtype.type)

    def sort_data_by(self, df=None, column="Index"):
        if df is None:
            df = self.data
        if column == "Index":
            self.data = df.copy().sort_index()
            return self.data
        self.data = df
        self.data = self.data.sort_values(by=column)
        return self.data.copy()

    @staticmethod
    def combine_date_time(date, time):
        date = pd.to_datetime(date)
        time = pd.to_datetime(time)
        for i in range(len(time)):
            time.iloc[i] = datetime(date.iloc[i].year,
                                    date.iloc[i].month,
                                    date.iloc[i].day,
                                    time.iloc[i].hour,
                                    time.iloc[i].minute,
                                    time.iloc[i].second,
                                    time.iloc[i].microsecond)
        return time.rename("DateTime")

    def first_attempts_only(self, columns, df=None):
        """
        Deletes all first attempts

        Parameters
        ----------
        df: pandas.DataFrame
            The data where the other attempts have to be filtered out.
        columns: list of strs
            Columns on which we check whether they are duplicated. If yes,
            only keep earliest account

        """
        if df is not None:
            self.data = df.copy()
        self.data.drop_duplicates(subset=columns, inplace=True)
        return self.data.copy()

    def filter(self, filters, df=None):
        """
        Filter out certain data from the current dataframe

        Saves the DataFrame to the loader class if it is not None. Else it
        will use the stored DataFrame

        Parameters
        ----------
        filters: dict of objects
            the data we want to filter out. Keys are the columns, values
            what is to be filtered out
        df: pd.DataFrame
            the data to be filtered

        Returns
        -------
        pd.DataFrame
            the filtered data
        """
        if df is not None:
            self.data = df
        for key in filters:
            self.data = self.data.loc[~self.data[key].isin(
                filters[key])].reset_index(drop=True)
        return self.data.copy()
