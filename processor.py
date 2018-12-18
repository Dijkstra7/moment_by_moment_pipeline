"""
=========
processor
=========

Processes the data loaded.

Most functions are a horribly similar to each other, thus violating the DRY
principle. This was done to quickly build the processing functions, while
making sure that the steps followed are correct.
A clean up may and should take place in the future.
"""
from datetime import datetime

import pandas as pd
import numpy as np
from config import loids
from tqdm import tqdm
import curve
from plotter import Plotter

class Processor:

    def __init__(self, df, att, short, long):
        self.data = df
        self.att = att
        self.short = short
        self.long = long
        self.skills = df['LOID'].drop_duplicates().values
        self.curves = {}
        self.n_peaks = {}
        self.p_peaks = {}
        self.plotter = Plotter()

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
            if len(select_data) == 0:
                self.short[cid].loc[self.short.UserId == user] = np.nan
                self.long[cid].loc[self.long.UserId == user] = np.nan

    def calculate_gain(self):
        print("Berekenen gain")
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
        print("Tellen gemaakt totaal first attempts")
        cid = 'Totaal aantal opgaven first attempts'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.att
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[data.UserId == user]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def count_total_exercises_correct_att(self):
        print("Tellen goed first attempts")
        cid = 'Totaal aantal goed first attempts'
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.att
        for user in data['UserId'].drop_duplicates().values:
            select_data = data.loc[(data.UserId == user) & (data.Correct == 1)]
            self.short[cid].loc[self.short.UserId == user] = len(select_data)
            self.long[cid].loc[self.long.UserId == user] = len(select_data)

    def get_transfer_score(self, transfer_data):
        desc = "Tellen goed transfertest"
        cid = "Aantal goed transfertest"
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = transfer_data
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select_data = data.loc[(data.UserId == user) & (data.Correct == 1)]
            self.short.loc[self.short.UserId == user, cid] = len(select_data)
            self.long.loc[self.long.UserId == user, cid] = len(select_data)
            if len(data.loc[(data.UserId == user)]) == 0:
                self.short.loc[self.short.UserId == user, cid] = np.nan
                self.long.loc[self.long.UserId == user, cid] = np.nan

    def skill_count_total_correct_phase_exercise(self, skill, phase):
        desc = f"Tellen aantal goed {phase}-phase voor skill {skill}"
        translator = {"pre": "Voormeting", "post": "Nameting"}
        scid = f"Skill_{translator[phase]}"
        lcid = f"{loids[skill]}_{translator[phase]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            if len(data.loc[(data.phase == phase) &
                            (data.UserId == user) &
                            (data.LOID == skill)]) > 0:
                select = data.loc[(data.phase == phase) &
                                  (data.UserId == user) &
                                  (data.LOID == skill) &
                                  (data.Correct == 1)]
                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = len(select)
                self.long.loc[self.long.UserId == user, lcid] = len(select)

    def calculate_gain_per_skill(self, skill):
        desc = f"Berekenen gain voor skill {skill}"
        print(desc)
        scid = f"Skill_gain"
        lcid = f"{loids[skill]}_gain"
        self.short.loc[self.short.LOID == skill, scid] = \
            self.short.loc[self.short.LOID == skill, "Skill_Nameting"] - \
            self.short.loc[self.short.LOID == skill, "Skill_Voormeting"]
        self.long[lcid] = self.long[f"{loids[skill]}_Nameting"] - \
                          self.long[f"{loids[skill]}_Voormeting"]

    def get_last_ability_of_skill(self, skill):
        desc = f"Vindt laatste vaardigheidsscore van skill {skill}"
        scid = f"Vaardigheidsscore_skill"
        lcid = f"Vaardigheidsscore_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            if len(data.loc[(data.UserId == user) &
                            (data.LOID == skill) &
                            (~np.isnan(data.AbilityAfterAnswer))]) > 0:
                select = data.loc[(data.UserId == user) &
                                  (data.LOID == skill) &
                                  (~np.isnan(data.AbilityAfterAnswer))]
                last_aaa = select["AbilityAfterAnswer"].iloc[-1]
                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = last_aaa
                self.long.loc[self.long.UserId == user, lcid] = last_aaa

    def count_total_exercises_made_per_skill(self, skill):
        desc = f"Tellen totaal gemaakte opgaven voor skill {skill}"
        scid = f"Aantalopgave_skill"
        lcid = f"Aantalopgave_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            if len(data.loc[(data.UserId == user) &
                            (data.LOID == skill)]) > 0:
                select = data.loc[(data.UserId == user) &
                                  (data.LOID == skill)]

                value = len(select)

                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = value
                self.long.loc[self.long.UserId == user, lcid] = value

    def count_total_exercises_correct_per_skill(self, skill):
        desc = f"Tellen totaal correct gemaakte opgaven voor skill {skill}"
        scid = f"Aantalgoed_skill"
        lcid = f"Aantalgoed_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            if len(data.loc[(data.UserId == user) &
                            (data.LOID == skill)]) > 0:
                select = data.loc[(data.UserId == user) &
                                  (data.LOID == skill) &
                                  (data.Correct == 1)]

                value = len(select)

                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = value
                self.long.loc[self.long.UserId == user, lcid] = value

    def count_total_exercises_made_att_per_skill(self, skill):
        desc = f"Tellen totaal gemaakte eerste pogingen voor skill {skill}"
        scid = f"Aantaleerstepoging_skill"
        lcid = f"Aantaleerstepoging_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            if len(data.loc[(data.UserId == user) &
                            (data.LOID == skill)]) > 0:
                select = data.loc[(data.UserId == user) &
                                  (data.LOID == skill)]

                value = len(select)

                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = value
                self.long.loc[self.long.UserId == user, lcid] = value

    def count_total_exercises_correct_att_per_skill(self, skill):
        desc = f"Tellen correct gemaakte eerste pogingen voor skill " \
               f"{skill}"
        scid = f"Goedeerstepoging_skill"
        lcid = f"Goedeerstepoging_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            if len(data.loc[(data.UserId == user) &
                            (data.LOID == skill)]) > 0:
                select = data.loc[(data.UserId == user) &
                                  (data.LOID == skill) &
                                  (data.Correct == 1)]

                value = len(select)

                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = value
                self.long.loc[self.long.UserId == user, lcid] = value

    def calculate_percentage_correct_per_skill(self, skill):
        print(f"Berekenen percentage correct voor skill {skill}")
        scid = f"Percentagegoed_skill"
        lcid = f"Percentagegoed_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = round(
            self.short.loc[self.short.LOID == skill, "Aantalgoed_skill"]
            /
            self.short.loc[self.short.LOID == skill, "Aantalopgave_skill"]
            , 2)
        self.long[lcid] = round(self.long[f"Aantalgoed_{loids[skill]}"]
                                /
                                self.long[f"Aantalopgave_{loids[skill]}"]
                                , 2)

    def calculate_percentage_correct_att_per_skill(self, skill):
        print(f"Berekenen percentage correct eerste pogingen voor "
              f"skill {skill}")
        scid = f"Percentagegoedpoging_skill"
        lcid = f"Percentagegoedpoging_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = round(
            self.short.loc[self.short.LOID == skill,
                           "Goedeerstepoging_skill"]
            /
            self.short.loc[self.short.LOID == skill,
                           "Aantaleerstepoging_skill"]
            , 2)
        self.long[lcid] = round(
            self.long[f"Goedeerstepoging_{loids[skill]}"]
            /
            self.long[f"Aantaleerstepoging_{loids[skill]}"]
            , 2)

    def count_total_adaptive_per_skill(self, skill):
        desc = f"Tellen aantal adaptive-phase voor skill {skill}"
        scid = f"Aantaladaptief_skill"
        lcid = f"Aantaladaptief_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.phase.isin(["ap", "rap"])) &
                              (data.UserId == user) &
                              (data.LOID == skill)]
            value = len(select)
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def count_correct_adaptive_per_skill(self, skill):
        desc = f"Tellen aantal correct adaptive-phase voor skill {skill}"
        scid = f"Goedadaptief_skill"
        lcid = f"Goedadaptief_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.phase.isin(["ap", "rap"])) &
                              (data.UserId == user) &
                              (data.LOID == skill) &
                              (data.Correct == 1)]
            value = len(select)
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def calculate_percentage_correct_adaptive_per_skill(self, skill):
        print(f"Berekenen percentage correct voor adaptive phase voor "
              f"skill {skill}")
        scid = f"Percentagegoedadaptief_skill"
        lcid = f"Percentagegoedadaptief_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = round(
            self.short.loc[self.short.LOID == skill,
                           "Goedadaptief_skill"]
            /
            self.short.loc[self.short.LOID == skill,
                           "Aantaladaptief_skill"]
            , 2)
        self.long[lcid] = round(self.long[f"Goedadaptief_{loids[skill]}"]
                                /
                                self.long[f"Aantaladaptief_{loids[skill]}"]
                                , 2)

    def count_total_adaptive_att_per_skill(self, skill):
        desc = f"Tellen aantal eerste pogingen in de adaptive phase voor " \
               f"skill {skill}"
        scid = f"Aantalpogingadaptief_skill"
        lcid = f"Aantalpogingadaptief_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.phase.isin(["ap", "rap"])) &
                              (data.UserId == user) &
                              (data.LOID == skill)]
            value = len(select)
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def count_correct_adaptive_att_per_skill(self, skill):
        desc = f"Tellen aantal correct eerste pogingen in de adaptive-phase " \
               f"voor skill {skill}"
        scid = f"Goedpogingadaptief_skill"
        lcid = f"Goedpogingadaptief_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.phase.isin(["ap", "rap"])) &
                              (data.UserId == user) &
                              (data.LOID == skill) &
                              (data.Correct == 1)]
            value = len(select)
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def calculate_percentage_correct_adaptive_att_per_skill(self, skill):
        print(f"Berekenen percentage correct eerste pogingen in de adaptive "
              f"phase voor skill {skill}")
        scid = f"Percentagegoedpogingadaptief_skill"
        lcid = f"Percentagegoedpogingadaptief_{loids[skill]}"
        self.short.loc[self.short.LOID == skill, scid] = round(
            self.short.loc[self.short.LOID == skill,
                           "Goedpogingadaptief_skill"]
            /
            self.short.loc[self.short.LOID == skill,
                           "Aantalpogingadaptief_skill"]
            , 2)
        self.long[lcid] = round(
            self.long[f"Goedpogingadaptief_{loids[skill]}"]
            /
            self.long[f"Aantalpogingadaptief_{loids[skill]}"]
            , 2)

    def add_skill_to_long_file(self, skill):
        print("Adding skill representations to long file")
        self.long[f"Skill_{loids[skill]}"] = skill

    def process_curves(self, skill):
        desc = f"Processing curves for skill {skill}"
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.UserId == user) &
                              (data.LOID == skill)]
            if len(select) > 3:
                self.curves[f"{user}_{skill}"] = curve.get_curve(select)

                self.p_peaks[f"{user}_{skill}"], \
                self.n_peaks[f"{user}_{skill}"] = \
                    curve.get_peaks(self.curves[f"{user}_{skill}"])
            else:
                self.curves[f"{user}_{skill}"], \
                self.p_peaks[f"{user}_{skill}"],\
                self.n_peaks[f"{user}_{skill}"] = \
                    (999, 999, 999)

            self.plotter.plot_save(
                [self.curves[f"{user}_{skill}"], select.Correct.values*.05-1],
                f_name=f"{user}_{skill}")

    def calculate_type_curve(self, skill):
        desc = f"Calculating type of curve for skill {skill}"
        scid = "MBML_curve"
        lcid = f"MBML_curve_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            skill_curve = self.curves[f"{user}_{skill}"]
            if skill_curve == 999:
                value = 999
            else:
                value = curve.get_type(skill_curve)

            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_phase_of_last_peak(self, skill):
        desc = f"Calculating type of curve for skill {skill}"
        scid = "MBML_curve"
        lcid = f"MBML_curve_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            skill_curve = self.curves[f"{user}_{skill}"]
            if skill_curve == 999:
                value = 999
            else:
                value = curve.get_type(skill_curve)

            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

