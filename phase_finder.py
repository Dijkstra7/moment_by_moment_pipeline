"""
============
Phase finder
============

Set the phase next to the data.
"""

import pandas as pd
import numpy as np
from tqdm import tqdm

from config import pre_ids, post_ids, nap_ids, gui_ids, gynzy_pre_ids, \
    gynzy_post_ids, LEARNING_GOALS
all_ids = pre_ids + post_ids + nap_ids + gui_ids

class PhaseFinder:

    def __init__(self):
        self.pre_max_id = len(pre_ids)
        self.pre_num = 0
        self.ap_day = {}
        self.gui_day = {}
        self.post_min_id = 0
        self.gui_len = {}
        self.posts_seen = []
        self.pre_seen = []

    def process_gui(self, row):
        if "rap" in self.ap_day:
            return False
        if "pre" in self.ap_day:
            if self.ap_day["pre"] == row.DateTime.day:
                return False
        if row.UserId == 3013:
            print(self.gui_len, row.DateTime)
        if self.gui_len[row.LOID] < 3:
            if row.LOID in self.ap_day:
                return False
        if row.ExerciseId in gui_ids:
            if row.LOID not in self.ap_day:
                if row.LOID not in self.gui_day:
                    self.gui_day[row.LOID] = row.DateTime.day
                return True
        return False

    def process_nap(self, row):
        if "rap" in self.ap_day:
            return False
        if "pre" in self.ap_day:
            if self.ap_day["pre"] == row.DateTime.day:
                return False
        if row.ExerciseId in nap_ids:
            if row.LOID not in self.ap_day:
                return True
        return False

    def process_pre(self, data, row, id_):
        if "rap" in self.ap_day or row.LOID in self.ap_day:
            return False
        if row.DateTime.day == self.ap_day["post"]:
            return False
        if row.ExerciseId in pre_ids:
            if self.pre_num < self.pre_max_id:
                self.pre_num += 1
                if "pre" not in self.ap_day:
                    self.ap_day["pre"] = row.DateTime.day
                if row.ExerciseId not in self.pre_seen:
                    self.pre_seen.append(row.ExerciseId)
                    return True
            ### When the pre-ids return in other ids, we have to change how
            ### they are processed, for example as below:
            # if id_ < self.pre_max_id:
            #     if "pre" not in self.ap_day:
            #         self.ap_day["pre"] = row.DateTime.day
            #     return True
            # elif id_ == self.pre_max_id:
            #     if data.phase == 'gui':
            #         return True
        return False

    def process_post(self, row, id_):
        if len(self.poss_post) < 10:
            return False
        if self.ap_day["post"] != row.DateTime.day:
            return False
        if row.ExerciseId in post_ids:
            if row.ExerciseId in self.posts_seen:
                return False
            self.posts_seen.append(row.ExerciseId)
            return True  # Also including not double attempts
        return False

    def process_ap(self, row):
        if "rap" in self.ap_day:
            return False
        if row.LOID not in self.ap_day:
            if "pre" not in self.ap_day:
                if row.ExerciseId in all_ids:
                    return True # Skip saving for the first adaptive day
            elif self.ap_day["pre"] == row.DateTime.day:
                return True  # Skip saving the first adaptive day
            if row.LOID not in self.gui_day:
                return True  # Skip saving the first adaptive day
            if self.gui_day[row.LOID] == row.DateTime.day:
                self.ap_day[row.LOID] = row.DateTime.day
                return True
            return False
        if row.DateTime.day == self.ap_day[row.LOID]:
            return True
        return False

    def find_phases(self, data: pd.DataFrame, verbose=1):
        data["phase"] = ""
        for user in data.UserId.unique():
            user_data = data.loc[data.UserId == user].sort_values("DateTime") \
                .reset_index()
            self.post_min_id = len(user_data)-len(post_ids)-1
            self.poss_post = user_data.loc[user_data.ExerciseId.isin(post_ids)]
            self.pre_num = 0
            self.posts_seen = []
            self.pre_seen = []
            if len(self.poss_post > 0):
                self.ap_day = {"post":
                                   self.poss_post.tail(1).iloc[0].DateTime.day}
            else:
                self.ap_day = {"post": user_data.iloc[0].DateTime.day}
            self.gui_day = {}
            for skill in LEARNING_GOALS:
                self.gui_len[skill] = len(data.loc[
                                              (data.UserId == user) &
                                              (data.ExerciseId.isin(gui_ids)) &
                                              (data.LOID == skill)
                                          ])
            for id_, row in user_data.iterrows():
                if self.process_gui(row):
                    data.loc[row['index'], 'phase'] = "gui"
                elif self.process_nap(row):
                    data.loc[row['index'], 'phase'] = "nap"

                elif self.process_pre(data.loc[user_data.iloc[0]['index']],
                                      row, id_):
                    data.loc[row['index'], 'phase'] = "pre"

                elif self.process_post(row, id_):
                    data.loc[row['index'], 'phase'] = "post"

                elif self.process_ap(row):
                    data.loc[row['index'], 'phase'] = "ap"

                else:
                    if "rap" not in self.ap_day:
                        self.ap_day["rap"] = row.DateTime.day
                    data.loc[row['index'], 'phase'] = "rap"

        return data

    @staticmethod
    def correct_phases(df: pd.DataFrame, user_loid_to_dict: dict):
        """
        change for certain users the non-post and -pre phases of certain
        learning objectives into another phase
        Parameters
        ----------
        df: pd.DataFrame
        user_loid_to_dict: dict of dicts

        Returns
        -------

        """
        for user, loids_to in user_loid_to_dict.items():
            for loid, to in loids_to.items():
                df.loc[(df.UserId == user) &
                       (df.LOID == loid) &
                       (~df.phase.isin(["post", "pre"])), "phase"] = to
        return df

    @staticmethod
    def inspect_phases(df: pd.DataFrame):
        for user in df.UserId.unique():
            u_data = df.copy().loc[df.UserId == user]
            # u_data['in_pre'] = ""
            pre_data = u_data.loc[u_data.phase == "pre"]
            gui_data = u_data.loc[u_data.phase == "gui"]
            nap_data = u_data.loc[u_data.phase == "nap"]
            ap_data = u_data.loc[u_data.phase == "ap"]
            rap_data = u_data.loc[u_data.phase == "rap"]

            post_data = u_data.loc[u_data.phase == "post"]
            all_post = u_data.loc[(u_data.phase != 'pre') &
                                  (u_data.ExerciseId.isin(post_ids))]
            all_gui = u_data.loc[(u_data.ExerciseId.isin(gui_ids))]
            all_nap = u_data.loc[(u_data.ExerciseId.isin(nap_ids))]
            all_ap = u_data.loc[(u_data.phase != "rap") &
                                (~u_data.ExerciseId.isin(all_ids))]
            all_rap = u_data.loc[(u_data.phase != "ap") &
                                 (~u_data.ExerciseId.isin(all_ids))]

            if len(post_data) != -1:
                print('---------')
                for id_, row in u_data.iterrows():
                    # if not np.isnan(row.AbilityAfterAnswer):
                    #     row.AbilityAfterAnswer = int(row.AbilityAfterAnswer)
                    if row.ExerciseId in post_ids and row.phase != "pre":
                        print(row.values, '<-')
                    else:
                        print(row.values)
                        # row.in_pre = "<-"

                print(user, len(pre_data), len(post_data), len(all_post))
                print('=========')
        for user in ['2031']:
            u_data = df.loc[df.UserId == user]
            pre_data = u_data.loc[u_data.phase == "pre"]
            gui_data = u_data.loc[u_data.phase == "gui"]
            nap_data = u_data.loc[u_data.phase == "nap"]
            ap_data = u_data.loc[u_data.phase == "ap"]
            rap_data = u_data.loc[u_data.phase == "rap"]

            post_data = u_data.loc[u_data.phase == "post"]
            all_post = u_data.loc[(u_data.phase != 'pre') &
                                  (u_data.ExerciseId.isin(post_ids))]
            all_pre = u_data.loc[(u_data.phase != 'post') &
                                  (u_data.ExerciseId.isin(pre_ids))]
            all_gui = u_data.loc[(u_data.ExerciseId.isin(gui_ids))]
            all_nap = u_data.loc[(u_data.ExerciseId.isin(nap_ids))]
            all_ap = u_data.loc[(u_data.phase != "rap") &
                                (~u_data.ExerciseId.isin(all_ids))]
            all_rap = u_data.loc[(u_data.phase != "ap") &
                                 (~u_data.ExerciseId.isin(all_ids))]
            if len(post_data) > -1:
                print(user)
                print("pre", len(pre_data), len(all_pre))
                print("post", len(post_data), len(all_post))
                print("gui", len(gui_data), len(all_gui))
                print("nap", len(nap_data), len(all_nap))
                print("ap", len(ap_data), len(all_ap))
                print("rap", len(rap_data), len(all_rap))

    def get_experiment_day(self, row_datetime, first_day):
        # Set up dictionary to match experiment dates to days
        experiment_day = {"day0": [(3, 29), (4, 5), (5, 10), (5, 29)],
                          "day1": [(4, 1), (4, 8), (5, 13), (6, 3)],
                          "day2": [(4, 2), (4, 9), (5, 14), (6, 4)],
                          "day3": [(4, 3), (4, 10), (5, 15), (6, 5)],
                          "day4": [(4, 4), (4, 11), (5, 16), (6, 6)],
                          "day5": [(4, 5), (4, 12), (5, 17), (6, 7)]}
        if isinstance(row_datetime, str):
            row_month = row_datetime[5:7]
            row_day = row_datetime[8:10]
        else:
            assert isinstance(row_datetime, pd.datetime)
            row_month = row_datetime.month
            row_day = row_datetime.day
        for key in experiment_day.keys():
            if (row_month, row_day) in experiment_day[key]:

                if row_month == 4 and row_day == 5 and first_day in ["29", 29]:
                    return "day5"
                return key

    def find_gynzy_phases_with_lesson_info(self, data: pd.DataFrame, id_):
        """
        Find phases of the data in Gynzy. Filter on days instead of phase.
        Additionally use the info from the lesson given by the raw data from
        Gynzy.

        Parameters
        ----------
        data: Pandas.DataFrame
            The data to be processed
        id_: str
            identifier of what file is processed. For small differences in
            processing

        Returns
        -------
        Pandas.Dataframe
            the data with added phases.
        """
        # Create phase column
        data["phase"] = ""
        # Process every user
        for user in tqdm(data.UserId.unique(), desc="Setting phases "):
            # Select user data
            user_data = data.loc[data.UserId == user]
            # Process the data
            for index, row in user_data.iterrows():
                if row.Lesson == 51582:
                    data.loc[index, 'phase'] = "pre"
                if row.Lesson == 51583:
                    data.loc[index, 'phase'] = "post"
                if row.DateTime.hour >= 12:
                    data.loc[index, "phase"] = "out of school"
            for index, row in user_data.iterrows():
                if data.loc[index, 'phase'] == "":
                    # Set phase to indicate the day of training
                    data.loc[index, 'phase'] = self.get_experiment_day(
                        row.DateTime, user_data.iloc[0].DateTime.day)
        return data

    def find_gynzy_phases(self, data, id_):
        """
        Find phases of the data in Gynzy. Filter on days instead of phase.

        Parameters
        ----------
        data: Pandas.DataFrame
            The data to be processed
        id_: str
            identifier of what file is processed. For small differences in
            processing

        Returns
        -------
        Pandas.Dataframe
            the data with added phases.
        """
        # Set up list of id's that slip through the detection of non-pre and
        # post ids
        exclude_post_ids = []
        exclude_pre_ids = []
        if id_ in ["karlijn_en_babbete"]:
            exclude_post_ids = [13862, 5471, 5472, 13599, 13634, 13655, 13668,
                                13844, 14109, 14208, 14215, 14065, 14556,
                                14557, 14568, 13737, 13833, 13835, 13880,
                                14323, 14331, 14543, 13744, 14116, 14326,
                                13727, 13936, 14002, 13768, 14273, 15503,
                                15461, 15911, 15610, 15614, 16195, 16216,
                                15483, 15961, 16099, 16103, 16124, 15613,
                                16208, 15834, 15838, 15939, 15944, 15524,
                                16108, 16109, 15814, 15912, 15889, 15900,
                                15926, 15995, 16000, 16031, 16130, 16136,
                                15924, 16065, 15692, 15436, 15751, 16201,
                                15502, 15611, 15640, 15643, 15930, 15931,
                                16072, 16085, 16764, 16765, ]
            for i in range(16702, 16726):
                exclude_post_ids.append(i)
        elif id_ in ["kb_all"]:
            exclude_pre_ids = [31686, 32189, 32145, 32279, 31605, 32067,
                               32027, 7842, 7650, 7645, 9053, 9062, 9318,
                               9411, 9421]
            exclude_post_ids = [33662, 14313, 10479, 16727, 16726, 16439,
                                16437, 16407, 16282, 17596, 17602, 17646,
                                14089, ]

        # Create phase column
        data["phase"] = ""
        print(data.head())
        # Process every user
        for user in tqdm(data.UserId.unique()):
            # print(f"processing {user}")
            # Select user data
            user_data = data.loc[data.UserId == user]
            # print(f"id: {id_}")

            if id_ not in ["kb", "kb_all", "kb_all_attempts_curve",
                           "kb_smoothed_curves"]:
                user_data = user_data.sort_values("DateTime").reset_index()

            # Set up what days are available for processing
            num_pre = 0
            if id_ == "karlijn_en_babbete":
                pre_days = ['29', '05']
                post_days = ['05', '12']

                first_day = user_data.iloc[0].DateTime[8:10]
                last_day = user_data.iloc[-1].DateTime[8:10]
                if last_day == '12':
                    post_days = ['12']

                if last_day in ['04', '05']:
                    pre_days = ['29']

                if first_day == '08':
                    pre_days = ['08']

            if id_ == "kb":
                pre_days = ['10', '29']
                post_days = ['17', '07']
                first_day = user_data.iloc[0].DateTime[8:10]
                last_day = user_data.iloc[-1].DateTime[8:10]

            if id_ in ["kb_all", "test", "kb_all_attempts_curve",
                       "kb_smoothed_curves"]:
                pre_days = ['29', '05', '10', '29']
                post_days = ['05', '12', '17', '07']
                if isinstance(user_data.iloc[0].DateTime, str):
                    first_day = user_data.iloc[0].DateTime[8:10]
                    last_day = user_data.iloc[-1].DateTime[8:10]
                    last_month = user_data.iloc[-1].DateTime[5:7]
                else:
                    first_day = user_data.iloc[0].DateTime.day
                    last_day = user_data.iloc[-1].DateTime.day
                    last_month = user_data.iloc[-1].DateTime.month
                if last_day in ['04', '05', 4, 5]:
                    pre_days = ['29', 29]

                if first_day in ['08', 8]:
                    pre_days = ['08', 8]

                if last_month in ['06', 6]:
                    post_days = ['07', 7]
                    pre_days = ['29', 29]

                if last_month in ['05', 5]:
                    post_days = ['17', 17]
                    pre_days = ['10', 10]

                if last_month in ['04', 4]:
                    post_days = ['05', '12', 5, 12]
                    if last_day in ['12', 12]:
                        pre_days = ['05', 5]
                        post_days = ['12', 12]
                    if last_day in ['05', 5]:
                        pre_days = ['29', 29]
                        post_days = ['05', 5]

            # Process the data
            for index, row in tqdm(user_data.iterrows(),
                                   desc="Setting pre and post phases"):
                if isinstance(row.DateTime, str):
                    row_day = row.DateTime[8:10]
                    row_hour = row.DateTime[11:13]
                else:
                    row_day = row.DateTime.day
                    row_hour = row.DateTime.hour
                if row.ExerciseId in gynzy_pre_ids and \
                        row_day in pre_days and index \
                        not in exclude_pre_ids:
                    data.loc[index, 'phase'] = "pre"
                    num_pre += 1
                if row.ExerciseId in gynzy_post_ids and \
                        row_day in post_days and \
                        index not in exclude_post_ids:
                    data.loc[index, 'phase'] = "post"

                if int(row_hour) >= 15:
                    data.loc[index, "phase"] = "out of school"
            if id_ not in ["kb", "kb_all", "kb_all_attempts_curve",
                           "kb_smoothed_curves"]:
                user_data = data.loc[data.UserId == user] \
                    .sort_values("DateTime").reset_index()
            post_data = data.loc[(data.phase == 'post') &
                                 (data.UserId == user)]
            pre_data = data.loc[(data.phase == 'pre') &
                                (data.UserId == user)]

            post_times = len(post_data.DateTime.unique())
            pre_times = len(pre_data.DateTime.unique())

            print(f"total pre ids: {len(pre_data)}; "
                  f"total post ids: {len(post_data)}; \n"
                  f"first day: {first_day}; last day: {last_day}")

            if post_times > 1 or pre_times > 1:
                for time in post_data.DateTime.unique():
                    print(time, ':',
                          len(post_data.loc[post_data.DateTime == time]))
                    if len(post_data.loc[post_data.DateTime == time]) == 24:
                        data.loc[(data.UserId == user) &
                                 (data.DateTime != time) &
                                 (data.phase == 'post'), 'phase'] = ""
                        break

                for time in pre_data.DateTime.unique():
                    print(time, ':',
                          len(pre_data.loc[pre_data.DateTime == time]))
                    if len(pre_data.loc[pre_data.DateTime == time]) == 24:
                        data.loc[(data.UserId == user) &
                                 (data.DateTime != time) &
                                 (data.phase == 'pre'), 'phase'] = ""
                        break

                printing = data.loc[(data.UserId == user) &
                                    (data.phase.isin(["pre", "post"]))].head(
                    len(user_data))
                if len(printing.DateTime.unique()) > len(
                        printing.phase.unique()):
                    print(printing)
                    print("post and pre adjusted")
            for index, row in tqdm(user_data.iterrows(),
                                   desc="Setting other phases"):
                if data.loc[index, 'phase'] == "":
                    # Set phase to indicate the day of training
                    data.loc[index, 'phase'] = self.get_experiment_day(
                        row.DateTime, first_day)
                    # # check for ambiguity on april 5th
                    # if first_day in ['05', 5]:
                    #     if data.loc[index, 'phase'] == "day5":
                    #         data.loc[index, 'phase'] = key

            original_max_columns = pd.options.display.max_columns
            original_max_colwidth = pd.options.display.max_colwidth
            pd.options.display.max_columns = 30
            # pd.options.display.max_rows = 400

            pd.options.display.max_colwidth = 300
            pd.options.display.width = 120
            print(data.loc[data.UserId == user])

            pd.options.display.max_columns = original_max_columns
            pd.options.display.max_colwidth = original_max_colwidth
        return data


if __name__ == "__main__":
    import pipeline
    pipeline.run_pipeline(False)
