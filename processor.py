"""
=========
processor
=========

Processes the data loaded.
"""
from datetime import datetime

import pandas as pd
import numpy as np


class Processor:

    def __init__(self, df, att, short, long):
        self.data = df
        self.att = att
        self.short = short
        self.long = long
        self.skills = df['LOID'].drop_duplicates().values

    def count_total_exercises(self):
        print("Tellen gemaakt totaal")
        cid = 'Totaal aantal opgaven'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[data.UserId == user]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def count_pre_exercises(self):
        print("Tellen goed pre-test")
        cid = "Voormeting"
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data.sort_values(by='UserId')
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[(data.UserId == user) &
                                   (data.ExerciseId.isin(pre_ids))]
            select_data["day"] = np.nan
            no_dup = select_data.copy().drop_duplicates(subset='ExerciseId',
                                                        )
            for n, date_time in enumerate(select_data['DateTime'].values):
                select_data["day"].iloc[n] = pd.to_datetime(date_time).day

            select_data_day = select_data.loc[select_data.day ==
                                          select_data.iloc[0].day]
            print(user, len(select_data), sum(select_data.Correct.values),
                  len(no_dup), sum(no_dup.Correct.values),
                  len(select_data_day), sum(select_data_day.Correct.values)
                  )
            # print("============\n", select_data[['day', 'ExerciseId']],
            #       "\n============\n")
