"""
============
Phase finder
============

Set the phase next to the data.
"""

import pandas as pd
import numpy as np
from config import pre_ids, post_ids, nap_ids, gui_ids
all_ids = pre_ids + post_ids + nap_ids + gui_ids

class PhaseFinder:

    def __init__(self):
        self.pre_max_id = len(pre_ids)
        self.pre_num = 0
        self.ap_day = {}
        self.gui_day = {}
        self.post_min_id = 0
        self.gui_len = {}

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
        if row.ExerciseId in pre_ids:
            if self.pre_num < self.pre_max_id:
                self.pre_num += 1
                if "pre" not in self.ap_day:
                    self.ap_day["pre"] = row.DateTime.day
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
            if row['index'] in self.poss_post['index'].values[-24:]:
                return True
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
            print(f"processing {user}")
            user_data = data.loc[data.UserId == user].sort_values("DateTime") \
                .reset_index()
            self.post_min_id = len(user_data)-len(post_ids)-1
            self.poss_post = user_data.loc[user_data.ExerciseId.isin(post_ids)]
            self.pre_num = 0
            if len(self.poss_post > 0):
                self.ap_day = {"post":
                                   self.poss_post.tail(1).iloc[0].DateTime.day}
            else:
                self.ap_day = {"post": user_data.iloc[0].DateTime.day}
            self.gui_day = {}
            for skill in [8025, 7789, 7771]:
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


if __name__ == "__main__":
    import pipeline
    pipeline.run_pipeline(False)
