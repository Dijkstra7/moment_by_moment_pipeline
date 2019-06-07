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
import pandas as pd
import numpy as np
from config import loids
from tqdm import tqdm
import curve
from plotter import Plotter


class Processor:

    def __init__(self, df, att, short, long, phases, logs):
        self.phases = phases
        self.data = df
        self.att = att
        self.short = short
        self.long = long
        self.skills = df['LOID'].drop_duplicates().values
        self.curves = {}
        self.n_peaks = {}
        self.p_peaks = {}
        self.plotter = Plotter()
        self.phase_dict = {"pre": 0, "gui": 1, "nap": 2, "ap": 3, "rap": 4,
                           "post": 5}
        self.phase_curves = {}
        self.phase_ids = {}
        self.logs = logs
        self.real_skill = {8025: 445, 7789: 478, 7771: 479}

    def count_total_correct_phase_exercises(self, phase):
        print(f"Tellen aantal goed {phase}-phase")
        translator = {"pre": "Voormeting", "post": "Nameting"}
        cid = translator[phase]
        self.short[cid] = np.nan
        self.long[cid] = np.nan
        data = self.data.copy()
        if phase == "pre":
            data = self.att.copy()
        for user in data['UserId'].unique():
            if len(data.loc[(data.phase == phase) &
                            (data.UserId == user)]) > 0:
                select = data.loc[(data.phase == phase) &
                                  (data.UserId == user) &
                                  (data.Correct == 1)]
                value = len(select)
            else:
                value = 0
            self.short.loc[self.short.UserId == user, cid] = value
            self.long.loc[self.long.UserId == user, cid] = value


    def count_total_phase_exercises(self, phase, skill):
        print(f"Tellen aantal gemaakt {phase}-phase voor skill {skill}")
        translator = {"pre": "Voormeting", "post": "Nameting"}
        scid = translator[phase]
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.data.copy()
        for user in data['UserId'].unique():
            select_data = data.loc[(data.phase == phase) &
                                   (data.UserId == user) &
                                   (data.LOID == skill)]
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = len(select_data)
            self.long.loc[self.long.UserId == user, lcid] = len(select_data)

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
        print(data.loc[data.UserId == 59491].tail(40).values)
        data = data.drop_duplicates(subset=['UserId', 'ExerciseId', 'LOID', 'phase'])
        print(data.loc[data.UserId == 59491].tail(40).values)
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

    def process_curves_babette(self, skill, do_plot=False, method="biggest"):
        desc = f"Processing curves for skill {skill}"
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            # if user != 3010:
            #     continue
            select = data.loc[(data.UserId == user) &
                              (data.LOID == skill)]

            # ## Testing inspection
            # print(user)
            # print(select.values)
            # dates = select.DateTime.dt.date.unique()
            # for i in range(len(select)):
            #     sselect = select.iloc[:i]
            #     if len(sselect) > 3:
            #         for j in range(len(sselect)):
            #             ssselect = sselect.iloc[j:]
            #             if len(ssselect) > 3:
            #                 ssselect_curve = curve.get_curve(ssselect)
            #                 type_ = curve.get_type(ssselect_curve)
            #                 print(type_, end=" ")
            #                 if type_ == 4:
            #                     print(f"({i}, {j})", end=" ")
            #                     # print(ssselect.values)
            #                     # print(ssselect.Correct.values)
            #
            #         print("")
            #
            # ## End testing

            if len(select) > 3:
                user_curve = curve.get_curve(select)
                key = f"{user}_{skill}"
                self.curves[key] = user_curve
                self.n_peaks[key], self.p_peaks[key] = \
                    curve.get_peaks(user_curve)
                self.phase_curves[f"{user}_{skill}"] = 999
                self.phase_ids[f"{user}_{skill}"] = 999
            else:
                self.curves[f"{user}_{skill}"] = 999
                self.n_peaks[f"{user}_{skill}"] = 999
                self.p_peaks[f"{user}_{skill}"] = 999
                self.phase_curves[f"{user}_{skill}"] = 999
                self.phase_ids[f"{user}_{skill}"] = 999
            if do_plot is True:
                self.plotter.plot_save(
                    [self.curves[f"{user}_{skill}"],
                     select.Correct.values * .05 - 1],
                    f_name=
                    # f"{curve.get_type(curve.get_curve(select))}_"
                    f"babette_total/{user}_{skill}"
                )

    def process_curves(self, skill, do_plot=False, method="biggest",
                       folder="simone"):
        desc = f"Processing curves for skill {skill}"
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            # if user != 3010:
            #     continue
            select = data.loc[(data.UserId == user) &
                              (data.LOID == skill)]

            # ## Testing inspection
            # print(user)
            # print(select.values)
            # dates = select.DateTime.dt.date.unique()
            # for i in range(len(select)):
            #     sselect = select.iloc[:i]
            #     if len(sselect) > 3:
            #         for j in range(len(sselect)):
            #             ssselect = sselect.iloc[j:]
            #             if len(ssselect) > 3:
            #                 ssselect_curve = curve.get_curve(ssselect)
            #                 type_ = curve.get_type(ssselect_curve)
            #                 print(type_, end=" ")
            #                 if type_ == 4:
            #                     print(f"({i}, {j})", end=" ")
            #                     # print(ssselect.values)
            #                     # print(ssselect.Correct.values)
            #
            #         print("")
            #
            # ## End testing

            if len(select) > 3:
                user_curve = curve.get_curve(select)
                key = f"{user}_{skill}"
                self.curves[key] = user_curve
                self.n_peaks[key], self.p_peaks[key] = \
                    curve.get_peaks(user_curve)
                print(select.phase.values)
                user_phases = select.phase.values
                for phase in self.phases:
                    phase_key = f"{key}_{phase}"
                    phase_curve, phase_ids = self.select_slice_curve(
                        user_curve, user_phases, phase, method)
                    self.phase_curves[phase_key] = phase_curve
                    self.phase_ids[phase_key] = phase_ids
            else:
                self.curves[f"{user}_{skill}"] = 999
                self.n_peaks[f"{user}_{skill}"] = 999
                self.p_peaks[f"{user}_{skill}"] = 999
                self.phase_curves[f"{user}_{skill}"] = 999
                self.phase_ids[f"{user}_{skill}"] = 999
            if do_plot is True:
                self.plotter.plot_save(
                    [self.curves[f"{user}_{skill}"],
                     select.Correct.values * .05 - 1],
                    f_name=
                    # f"{curve.get_type(curve.get_curve(select))}_"
                    f"{folder}/{user}_{skill}", phase_data=select.phase.values
                )

    def process_wrong_curves(self, skill, do_plot=False, method="biggest"):
        desc = f"Processing curves for skill {skill}"
        # print(self.data.columns)
        data = self.att.copy()
        data = data.loc[
            # (data.DateTime > pd.datetime(2018, 11, 10))
            # &
            (data.DateTime < pd.datetime(2018, 11, 15))
        ]
        for user in [3011]:  # tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.UserId == user) &
                              (data.LOID == skill)]
            select.loc[select.ExerciseId == 1713996, 'Correct'] = 3
            print(select.loc[:, ['DateTime', 'LOID', 'Correct']].head(40))
            for i in range(len(select), 1, -1):
                print(curve.get_type(curve.get_curve(select.head(i))))
                print(' ', curve.get_type(curve.get_curve(select.tail(i))))

            if len(select) > 3:
                user_curve = curve.get_curve(select)
                key = f"{user}_{skill}"
                self.curves[key] = user_curve
                self.n_peaks[key], self.p_peaks[key] = \
                    curve.get_peaks(user_curve)
                user_phases = select.phase.values
                for phase in self.phases:
                    phase_key = f"{key}_{phase}"
                    phase_curve, phase_ids = self.select_slice_curve(
                        user_curve, user_phases, phase, method)
                    self.phase_curves[phase_key] = phase_curve
                    self.phase_ids[phase_key] = phase_ids
            else:
                self.curves[f"{user}_{skill}"] = 999
                self.n_peaks[f"{user}_{skill}"] = 999
                self.p_peaks[f"{user}_{skill}"] = 999
                self.phase_curves[f"{user}_{skill}"] = 999
                self.phase_ids[f"{user}_{skill}"] = 999
            if do_plot is True:
                self.plotter.plot_save(
                    [self.curves[f"{user}_{skill}"],
                     select.Correct.values * .05 - 1],
                    f_name=
                    # f"{curve.get_type(curve.get_curve(select))}_"
                    f"{user}_{skill}_w", phase_data=select.phase.values
                )

    @staticmethod
    def select_slice_curve(curve, user_phases, phase, method="biggest"):
        # Find start and endpoint of slices
        curve_ends = []
        curve_starts = []
        if user_phases[0] == phase:
            curve_starts = [0]
            if user_phases[1] != phase:
                curve_ends = [0]
        for i in range(1, len(curve) - 1):
            if user_phases[i] == phase:
                if user_phases[i - 1] != phase:
                    curve_starts.append(i)
                if user_phases[i + 1] != phase:
                    curve_ends.append(i)
        if len(curve_ends) < len(curve_starts):
            curve_ends.append(len(curve) - 1)
        # create slices
        slices = []
        ids = []
        complete_slice = []
        complete_ids = []
        for i, j in zip(curve_starts, curve_ends):
            slices.append(curve[i: j + 1])
            ids.append(list(range(i, j + 1)))
            for n, k in enumerate(slices[-1]):
                complete_slice.append(k)
                complete_ids.append(ids[-1][n])

        # Return slices
        if len(slices) == 0:
            return [], []
        if method == "biggest":
            # Return biggest slice
            return max(slices, key=len), max(ids, key=len)
        if method == "first":
            return slices[0], ids[0]
        if method == "all":
            return complete_slice, complete_ids
        if method == "exclude_single_strays":
            if len(slices) == 1:
                return slices[0], ids[0]
            elif all([len(slice) == 1 for slice in slices]):
                return complete_slice, complete_ids
            else:
                ret_slice = []
                ret_ids = []
                for slice, id_ in zip(slices, ids):
                    if len(slice) > 1:
                        for item, i in zip(slice, id_):
                            ret_slice.append(item)
                            ret_ids.append(i)
            return ret_slice, ret_ids

    def calculate_type_curve(self, skill):
        desc = f"Calculating type of curve for skill {skill}"
        scid = "MBML_curve"
        lcid = f"MBML_curve_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            try:
                skill_curve = self.curves[f"{user}_{skill}"]
            except KeyError:
                skill_curve = 999
            if skill_curve == 999:
                value = 999
            else:
                print(f"For user {user} ", end="")
                value = curve.get_type(skill_curve)

            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_phase_of_last_peak(self, skill):
        desc = f"Getting phase of last peak for skill {skill}"
        scid = "Phase_last_peak"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            userdata = data.loc[(data.UserId == user) &
                                (data.LOID == skill)]
            skill_curve = self.curves[f"{user}_{skill}"]
            if skill_curve == 999:
                value = 999
            else:
                if self.n_peaks[f"{user}_{skill}"] == 0:
                    value = -1  # Or 0. Depending on whether you find the
                    # drop the first peak.
                else:
                    last_peak = self.p_peaks[f"{user}_{skill}"][-1]
                    phase = userdata.iloc[last_peak + 1].phase
                    value = self.phase_dict[phase]

            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def count_first_attempts_per_skill(self, phase, skill):
        desc = f"counting amount of first attempts for skill {skill}, " \
               f"phase {phase}"
        scid = f"Total_first_attempts_{phase}_phase"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            userdata = data.loc[(data.UserId == user) &
                                (data.LOID == skill) &
                                (data.phase == phase)]
            value = len(userdata)
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def calculate_general_spikiness(self, skill):
        desc = f"Calculate general spikiness for skill {skill}"
        scid = f"General_spikiness"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            curve = self.curves[f"{user}_{skill}"]
            if curve == 999:
                value = 999
            else:
                # spikiness = max waarde / avg waarde
                value = max(curve) / (sum(curve) / len(curve))
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def calculate_phase_spikiness(self, skill, phases, method="biggest"):
        desc = f"Calculate per phase spikiness for skill {skill}"
        data = self.att.copy()
        for phase in phases:
            scid = f"spikiness_{phase}"
            lcid = f"{scid}_{skill}"
            self.short.loc[self.short.LOID == skill, scid] = np.nan
            self.long[lcid] = np.nan
        for user in tqdm(data['UserId'].unique(), desc=desc):
            curve = self.curves[f"{user}_{skill}"]
            # print('---\n', user, '\n---')
            for phase in phases:
                scid = f"spikiness_{phase}"
                lcid = f"{scid}_{skill}"
                if curve == 999:
                    value = 999
                else:
                    phase_curve = self.phase_curves[f"{user}_{skill}_{phase}"]

                    # print(f"{phase}: {phase_curve}", end="; ")
                    if phase_curve != 999 and sum(phase_curve) > 0:
                        # spikiness = max waarde / avg waarde
                        value = max(phase_curve) / (sum(phase_curve)
                                                    /
                                                    len(phase_curve))
                    else:
                        value = 999
                # print(value)
                self.short.loc[(self.short.UserId == user) &
                               (self.short.LOID == skill), scid] = value
                self.long.loc[self.long.UserId == user, lcid] = value

    def get_total_amount_of_peaks(self, skill):
        desc = f"Count total amount of peaks in curve for skill {skill}"
        scid = f"peaks_total"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            value = self.n_peaks[f"{user}_{skill}"]
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_peaks_per_skill_per_phase(self, skill, phase, method="biggest"):
        desc = f"Count amount of peaks in curve for phase {phase} and " \
               f"for skill {skill} "
        scid = f"peaks_{phase}"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            peaks = self.p_peaks[f"{user}_{skill}"]
            phase_ids = self.phase_ids[f"{user}_{skill}_{phase}"]
            if phase_ids == 999:
                value = 999
            else:
                # Count peaks in the ids of the phases.
                value = 0
                for peak in peaks:
                    if peak + 1 in phase_ids:
                        value += 1
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_total_amount_of_trans_peaks(self, skill):
        desc = f"Count total amount of transition peaks in curve for skill " \
               f"{skill}"
        scid = f"trans_peaks_total"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            peaks = self.p_peaks[f"{user}_{skill}"]
            user_phases = data.loc[(data.UserId == user) &
                                   (data.LOID == skill)].phase.values
            prev_phase = None
            value = 0
            for pos, phase in enumerate(user_phases):
                if phase != prev_phase:
                    prev_phase = phase
                    if pos - 1 in peaks:
                        value += 1

            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_trans_peaks_per_skill_per_phase(self, skill, phase):
        desc = f"Count amount of transition peaks in curve for phase {phase}" \
               f" and for skill {skill} "
        scid = f"trans_peaks_{phase}"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            peaks = self.p_peaks[f"{user}_{skill}"]
            user_phases = data.loc[(data.UserId == user) &
                                   (data.LOID == skill)].phase.values
            prev_phase = None
            value = 0
            if len(peaks)!=0:
                for pos, user_phase in enumerate(user_phases):
                    if user_phase != prev_phase:
                        print(f"\n{user}: {user_phase}, {prev_phase}, {pos}; "
                              f"{peaks}; ", end="")
                        prev_phase = user_phase
                        if pos - 1 in peaks and user_phase == phase:
                            value += 1
                        print(value, end="")

            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_setgoal(self, skill, moment):
        """
        Get the goal set for the first lesson.

        Parameters
        ----------
        skill

        """
        moment_dict = {1: "first", 2: "repeat", 3: "end"}
        desc = f"get the goal set for the {moment_dict[moment]}" \
               f" lessons of skill {skill} "
        scid = f"set_goal_{moment_dict[moment]}"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = pd.read_csv("./res/objectiveinstances.csv", index_col=0)
        for user in tqdm(self.att['UserId'].unique(), desc=desc):
            set_logs = data.loc[
                (data.user_id == user) &
                (data.learning_objective_id == self.real_skill[skill]) &
                (data.phase == moment_dict[moment])].goal.values
            if len(set_logs) > 0 and set_logs[0] >= 0:
                value = set_logs[-1]
            else:
                value = 999
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_shown_path_after_first_lesson(self, skill):
        """
        Get the goal set for the first lesson.

        Parameters
        ----------
        skill

        """
        moment_dict = {1: "first", 2: "repeat", 3: "end"}
        desc = f"get the shown after the first " \
               f"lessons of skill {skill} "
        scid = f"shown_path_first"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.logs.copy()
        for user in tqdm(self.att['UserId'].unique(), desc=desc):
            set_logs = data.loc[
                (data.user_id == user) &
                (data.screen == 3) &
                (data.action == 2)]
            clicked_skill = data.loc[
                (data.user_id == user) &
                (data.screen == 2) &
                (data.action == 1)]
            clicked_skill["skill"] = clicked_skill.object_id
            set_logs = set_logs.append(clicked_skill).sort_index()
            print(set_logs.head(len(set_logs)))
            set_logs.skill = set_logs.skill.fillna(method='ffill')
            set_logs = set_logs.loc[(set_logs.skill == self.real_skill[skill])
                                    & (set_logs.screen == 3)
                                    & (set_logs.object_id == 1)
                                    & (set_logs.index < pd.datetime(
                2018, 11, 15))]
            if len(set_logs) > 0:
                value = set_logs['info'].values[0]
            else:
                value = 999
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def get_shown_path_after_repeat_lesson(self, skill):
        """
        Get the goal set for the first lesson.

        Parameters
        ----------
        skill

        """
        moment_dict = {1: "first", 2: "repeat", 3: "end"}
        desc = f"get the path shown after the repeat" \
               f" lessons of skill {skill} "
        scid = f"shown_path_repeat"
        lcid = f"{scid}_{skill}"
        self.short.loc[self.short.LOID == skill, scid] = np.nan
        self.long[lcid] = np.nan
        data = self.logs.copy()
        for user in tqdm(self.att['UserId'].unique(), desc=desc):
            set_logs = data.loc[
                (data.user_id == user) &
                (data.screen == 3) &
                (data.action == 2)]
            clicked_skill = data.loc[
                (data.user_id == user) &
                (data.screen == 2) &
                (data.action == 1)]
            clicked_skill["skill"] = clicked_skill.object_id
            set_logs = set_logs.append(clicked_skill).sort_index()
            set_logs.skill = set_logs.skill.fillna(method='ffill')
            set_logs = set_logs.loc[(set_logs.skill == self.real_skill[skill])
                                    & (set_logs.screen == 3)
                                    & (set_logs.object_id == 2)]
            if len(set_logs) > 0:
                value = set_logs['info'].values[-1]
            else:
                value = 999
            self.short.loc[(self.short.UserId == user) &
                           (self.short.LOID == skill), scid] = value
            self.long.loc[self.long.UserId == user, lcid] = value

    def estimate_parameters(self, skills, params_min=None, params_max=None,
                            grain=1000):
        extractor = ParameterExtractor(params_min, params_max=[1., 1., .3, .1])
        for skill in skills:
            print(f"Searching for parameters for skill {skill}")
            # Get data from the skill
            data = self.att.copy().loc[self.data.LOID == skill]

            # Sort the data on user, then on time.
            data = data.sort_values(by=['UserId', 'DateTime'])
            print(data.head(100).values)

            # Extract the correctness of the answers
            answers = data.loc[:, 'Correct'].values

            # Extract whether we are viewing the same student (0), or a new one
            diff = data.loc[:, 'UserId'].diff().values  # Extract difference
            diff[0] = 1
            same = [1 if d == 0 else 0 for d in diff]
            extractor.smart_ssr(answers, same, grain=grain)

    def generate_kappa_file(self):
        data = self.data.copy()
        data = data.loc[data.phase.isin(["pre", "post"])]
        kappa = pd.DataFrame(index=data.UserId.unique())
        for _, item in data.iterrows():
            kappa.loc[item.UserId, item.ExerciseId] = item.Correct
        kappa.to_excel("output\kappa_file.xlsx", na_rep=999)


class ParameterExtractor:

    """
    Calculates the pre-calculated parameters.

    Has an option for brute force calculating the parameters or for using a
    heuristic approach.
    """

    def __init__(self, params_min=None, params_max=None):
        # params = [L0, T, G, S, F]
        self.params_min = params_min or [1e-15]*4
        self.params_max = params_max or [1.0, 1.0, 0.3, 0.1]

    def brute_force_params(self, answers, same, grain=100, L0_fix=None,
                           T_fix=None, G_fix=None, S_fix=None, v=0):
        """
        Check for every parameter what the best value is.

        if x_fix is None then the whole range will be tested.
        :param answers: the answers given by the students
        :param same: Whether the answers are switching to a new student.
        :param grain: integer defining the amount of values being checked
        :param L0_fix: integer; value of L0. if None, this will return best L0
        :param T_fix: integer; value of T. if None, this will return best T
        :param G_fix: integer; value of G. if None, this will return best G
        :param S_fix: integer; value of S. if None, this will return best S

        :return: values for L0, T, G and S that result in the lowest SSR.
        """
        # set ranges up
        best_l0 = L0_fix
        best_t = T_fix
        best_g = G_fix
        best_s = S_fix
        best_SSR = len(answers) * 999999999999991
        L0_range = self.get_range(L0_fix, 0, grain)
        T_range = self.get_range(T_fix, 1, grain)
        G_range = self.get_range(G_fix, 2, grain)
        S_range = self.get_range(S_fix, 3, grain)

        # Find best values
        for L0 in L0_range:
            if v:
                print(f'----------------------------------\nL0 is now at:{L0}')
            for T in T_range:
                for G in G_range:
                    for S in S_range:
                        # Get SSR for values
                        new_SSR = self.get_s_s_r(L0, T, G, S, answers,
                                                 same)

                        # check whether new value improves old values
                        if new_SSR <= best_SSR:
                            best_l0, best_t, best_g, best_s, \
                            best_SSR = [L0, T, G, S, new_SSR]
                            if v:
                                print(f'best parameters now at L0:{L0}, T:{T},'
                                      f' G:{G}, S:{S}')
        return best_l0, best_t, best_g, best_s

    def get_range(self, possible_range, par_id, grain):
        """
        helperfunction to get the range for a parameter based on the grain.

        returns either a list of the whole possible values if that value is
        not set (possible_range=None) else it returns a list containing only
        once the value of the set value.
        :param possible_range: Either float with the preset value or None
        :param par_id: the id of the parameter to find the boundaries for it.
        :param grain: integer, how finegrained the range must be.
        :return:
        """
        if possible_range is None:
            return np.linspace(self.params_min[par_id],
                               self.params_max[par_id],
                               int(grain * self.params_max[par_id]+1),
                               endpoint=True)[1:]
        return [possible_range]

    def get_s_s_r(self, L0, T, G, S, answers, sames=None):
        """
        Calculate the Sum Squared Residu.

        This is a method that defines the fit of the parameters.
        :param L0: integer; value of L0
        :param T: integer; value of T
        :param G: integer; value of G
        :param S: integer; value of S
        :param answers: list of answers given by students
        :param sames: list of whether the answer is given by the same student.
        :return: float; Summed squared residu
        """
        SSR = 0.0
        S = max(1E-15, S)
        T = max(1E-15, T)
        G = max(1E-15, G)
        L0 = max(1E-15, L0)
        L = L0
        # Make sure that there is a list with sames.
        if sames is None:
            sames = np.zeros(answers.size)
            sames[0] = 1

        # for every answer update the SSR.
        for same, answer in zip(sames, answers):
            if same == 0:  # New student so reset to initial chance of learning
                L = L0
            # print(L, T, G, S, F)
            SSR += (answer - (L * (1.0 - S) + (1.0 - L) * G)) ** 2
            if answer == 0:
                L_given_answer = (L * S) / ((L * S) + ((1.0 - L) * (1.0 - G)))
            else:
                L_given_answer = (L * (1.0 - S)) / (
                        (L * (1.0 - S)) + ((1.0 - L) * G))
            L = L_given_answer + (1.0 - L_given_answer) * T
        return SSR

    def smart_ssr(self, answers, same, grain=100, iterations=100):
        best_l0 = self.brute_force_params(answers, same, grain,
                                          None, 0.0, 0.0, 0.0)[0]
        best_t = self.brute_force_params(answers, same, grain,
                                         0.0, None, 0.0, 0.0)[1]
        best_g = self.brute_force_params(answers, same, grain,
                                         0.0, 0.0, None, 0.0)[2]
        best_s = self.brute_force_params(answers, same, grain,
                                         0.0, 0.0, 0.0, None)[3]
        all_best = [best_l0, best_t, best_g, best_s]
        for i in range(iterations):
            all_best = [best_l0, best_t, best_g, best_s]
            print("best is ", end=" ")
            best_l0 = self.brute_force_params(answers, same, grain, None,
                                              best_t, best_g, best_s)[0]
            print(f"L0: {round(best_l0, 6)}", end=", ")
            best_t = self.brute_force_params(answers, same, grain, best_l0,
                                             None, best_g, best_s)[1]
            print(f"T: {round(best_t, 6)}", end=", ")
            best_g = self.brute_force_params(answers, same, grain, best_l0,
                                             best_t, None, best_s)[2]
            print(f"G: {round(best_g, 6)}", end=", ")
            best_s = self.brute_force_params(answers, same, grain, best_l0,
                                             best_t, best_g, None)[3]
            print(f"S: {round(best_s, 6)}")
            if all_best == [best_l0, best_t, best_g, best_s]:
                print("Converging on best parameters being: ", all_best)
                break
        return best_l0, best_t, best_g, best_s

    
if __name__ == "__main__":
    import pipeline

    pipeline.run_pipeline(estimate_parameters=True)
