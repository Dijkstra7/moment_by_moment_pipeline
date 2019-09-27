"""
======
Loader
======

Loads the data.
"""
import os
import pickle

import pandas as pd
from datetime import datetime

import xlrd

import config


class DataLoader:

    def __init__(self, f_name=None, s_name=None):
        self.file_name = f_name or "./res/leerpaden_app.xlsx"
        self.sheetname = s_name or "AllData"
        self.data = None
        self.log_data = None
        self.quick_loaded = False

    def load(self, from_csv=False, quick_loading=True):
        transfer_data = None
        if quick_loading is True:
            print("Quick loading")
            if os.path.exists("quicksave.pkl"):
                self.data = pickle.load(open("quicksave.pkl", "rb"))
                if os.path.exists("quicktransfer.pkl"):
                    transfer_data = pickle.load(open("quicktransfer.pkl",
                                                     "rb"))
                    self.quick_loaded = True
                    print("Quickload succesfull")
                    return self.data.copy(), transfer_data
                else:
                    print("Quickloading failed, go for long version")
            else:
                print("Quickloading failed, go for long version")
        if from_csv is True:
            data = pd.read_csv(self.file_name, infer_datetime_format=True)
        else:
            try:
                data = pd.read_excel(self.file_name)
            except xlrd.biffh.XLRDError:
                data = pd.read_excel(self.file_name)
        data.rename(columns={"LearningObjectiveId": "LOID"}, inplace=True)
        data.Correct.loc[data.Correct > 1] = 1
        print("converting to datetime")
        data.DateTime = pd.to_datetime(data.DateTime)
        transfer_data = data.loc[data.LOID.isin([7579, 8181])]
        # Remove double entries in transfer test
        for user in transfer_data.UserId.unique():
            if len(transfer_data.loc[transfer_data.UserId == user]) > 16 \
                    and "Nadine" not in self.file_name:
                count = 0
                max_count = 16
                if user in [15909524, 383791]:
                    max_count = 15
                for index, item in transfer_data.loc[
                        transfer_data.UserId == user].iterrows():
                    print(count, index)
                    if count >= max_count:
                        print(index)
                        transfer_data = transfer_data.drop(index)
                    count += 1
                # print(transfer_data.loc[user==transfer_data.UserId].head(20))
        data = data.loc[(data.LOID.isin(config.LEARNING_GOALS))]
        self.data = data.copy()
        return data, transfer_data

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

    def quick_save(self, data, f_name="quicksave.pkl"):
        pickle.dump(data, open(f_name, "wb"))

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

    def first_attempts_only(self, columns, df=None, copy_df=True):
        """
        Deletes all first attempts

        Parameters
        ----------
        df: pandas.DataFrame
            The data where the other attempts have to be filtered out.
        columns: list of strs
            Columns on which we check whether they are duplicated. If yes,
            only keep earliest account
        copy_df: bool
            Whether to update the data dataframe or not.

        """
        data = self.data.copy()
        if df is not None:
            data = df

        att_data = data.drop_duplicates(subset=columns)
        # if copy_df is True:
        #     self.data = data
        return att_data

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
                filters[key])]
        # self.data.loc[self.data.Correct > 1, "Correct"] = 1
        return self.data.copy()

    def load_log(self, f_name="./res/logdata.csv"):
        """
        Load the log data from the csv file containing all logs from the app.

        Returns
        -------
        pandas DataFrame:
            The log data.
        """

        self.log_data = pd.read_csv(f_name, index_col=2, parse_dates=[
            "date_time"])
        self.log_data.drop(self.log_data.columns[[0, 1]], axis=1,
                           inplace=True)
        self.log_data = self.log_data.loc[self.log_data.user_id > 2999]
        self.log_data = self.log_data.loc[self.log_data.index <
                                          pd.datetime(2018, 11, 17)]
        return self.log_data

    def load_jorieke_data(self, f_name=None, s_name="AllData"):
        data = pd.read_excel(f_name or config.nadine_file_name,
                             sheet_name=s_name)
        data.rename(columns={"LearningObjectiveId": "LOID"}, inplace=True)
        return data

    def load_jorieke_pilot_data(self, f_name=None, s_name="pilot1",
                               s_name2="pilot2"):
        data = pd.read_excel(f_name or config.nadine_file_name,
                             sheet_name=s_name)
        data.rename(index=str, columns={"SubmitDate": "Date"})
        data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
        other_sheet = pd.read_excel(f_name or config.nadine_file_name,
                                    sheet_name=s_name2)
        print(data.info())
        print(other_sheet.info())
        print(data.tail())
        print(other_sheet.tail())
        data = data.append(other_sheet)
        data.rename(columns={"LearningObjectiveId": "LOID"}, inplace=True)
        return data

    def load_simone_data(self, f_name=None, s_name=""):
        pass


if __name__ == "__main__":
    print(DataLoader().load_simone_data().info())

