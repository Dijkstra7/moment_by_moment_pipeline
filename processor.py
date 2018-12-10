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

    def count_total_correct_phase_exercises(self, phase):
        print(f"Tellen aantal goed {phase}-phase")
        translator = {"pre": "Voormeting", "post": "Nameting"}
        cid = translator[phase]
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data.copy()
        for user in data['UserId'].unique():
            if len(data.loc[(data.phase == phase) &
                            (data.UserId == user)]) > 0:
                select = data.loc[(data.phase == phase) &
                                  (data.UserId == user) &
                                  (data.Correct == 1)]
                self.short[cid].loc[self.short.UserId == user] = len(select)
                self.long[cid].loc[self.long.UserId == user] = len(select)

    def count_total_phase_exercises(self, phase):
        print(f"Tellen aantal goed {phase}-phase")
        translator = {"pre": "Voormeting", "post": "Nameting"}
        cid = translator[phase]
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data.copy()
        for user in data['UserId'].unique():
            select_data = data.loc[(data.phase == phase) &
                                   (data.UserId == user)]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def calculate_gain(self):
        print("calculating gain")
        self.short["Gain"] = self.short["Nameting"] - self.short["Voormeting"]
        self.long["Gain"] = self.long["Nameting"] - self.long["Voormeting"]
            
    def count_total_exercises_made(self):
        print("Tellen gemaakt totaal")
        cid = 'Totaal aantal opgaven'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[data.UserId == user]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def count_total_exercises_correct(self):
        print("Tellen goed totaal")
        cid = 'Totaal aantal goed'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[(data.UserId == user) & (data.Correct == 1)]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def count_total_exercises_made_att(self):
        print("Tellen gemaakt totaal first ")
        cid = 'Totaal aantal opgaven'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.att
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[data.UserId == user]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def count_total_exercises_correct_att(self):
        print("Tellen goed first attempts")
        cid = 'Totaal aantal goed'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.att
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[(data.UserId == user) & (data.Correct == 1)]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)
