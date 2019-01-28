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
                self.short.loc[self.short.UserId == user, cid] = len(select)
                self.long.loc[self.long.UserId == user, cid] = len(select)

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

    def process_curves(self, skill, do_plot=False, method="biggest"):
        desc = f"Processing curves for skill {skill}"
        data = self.att.copy()
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.UserId == user) &
                              (data.LOID == skill)]
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
                self.phase_curves = 999
                self.phase_ids = 999
            if do_plot is True:
                self.plotter.plot_save(
                    [self.curves[f"{user}_{skill}"],
                     select.Correct.values * .05 - 1],
                    f_name=
                    # f"{curve.get_type(curve.get_curve(select))}_"
                    f"{user}_{skill}", phase_data=select.phase.values
                )

    def process_wrong_curves(self, skill, do_plot=False, method="biggest"):
        desc = f"Processing curves for skill {skill}"
        # print(self.data.columns)
        data = self.data.copy()
        data = data.loc[
            (self.data.DateTime < pd.datetime(2018, 11, 15))]
        for user in tqdm(data['UserId'].unique(), desc=desc):
            select = data.loc[(data.UserId == user) &
                              (data.LOID == skill)]
            print(select.LOID.head())
            print(select.LOID.tail())
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
            set_logs.skill = set_logs.skill.fillna(method='ffill')
            set_logs = set_logs.loc[(set_logs.skill == self.real_skill[skill])
                                    & (set_logs.screen == 3)
                                    & (set_logs.object_id == 1)]
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


if __name__ == "__main__":
    import pipeline

    pipeline.run_pipeline()
