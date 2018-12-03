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
        self.ap_day = {}
        self.post_min_id = 0

    def process_gui(self, row):
        if row.ExerciseId in gui_ids:
            if row.LOID not in self.ap_day:
                return True
        return False

    def process_nap(self, row):
        if row.ExerciseId in nap_ids:
            if row.LOID not in self.ap_day:
                return True
        return False

    def process_pre(self, data, row, id_):
        if row.ExerciseId in pre_ids:
            if id_ < self.pre_max_id:
                if "pre" not in self.ap_day:
                    self.ap_day["pre"] = row.DateTime.day
                return True
            elif id_ == self.pre_max_id:
                if data.phase == 'gui':
                    return True
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
        if row.LOID not in self.ap_day:
            if ("pre" not in self.ap_day or
                    self.ap_day["pre"] == row.DateTime.day) and \
                    row.ExerciseId in all_ids:
                return True  # Skip saving the first adaptive day
            self.ap_day[row.LOID] = row.DateTime.day
            return True
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
            self.ap_day = {"post": self.poss_post.tail(1).iloc[0].DateTime.day}
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
                    data.loc[row['index'], 'phase'] = "rap"

                # print(data.head())

            if verbose == 0:
                continue

            processed_data = data.copy().loc[data.UserId == user] \
                .reset_index(drop=True)
            pre_data = processed_data.loc[processed_data.phase == 'pre']
            post_data = processed_data.loc[processed_data.phase == 'post']
            if verbose == 1:
                print(len(pre_data), len(post_data))
                continue
            if len(pre_data) < len(pre_ids):
                missing_pre = pre_ids[:]
                for id_ in pre_data.ExerciseId.values[:self.pre_max_id]:
                    if id_ in missing_pre:
                        missing_pre.remove(id_)
                    else:
                        print(id_)
                print(f"Too short{user}: {len(pre_data)} - [{missing_pre}]")

                print(self.ap_day)
            else:
                pass
                # print(processed_data.loc[
                #           (processed_data.ExerciseId.isin(pre_ids)) &
                #           (processed_data.index > 24)
                #       ].values)
            for bluh in processed_data.values:
                print(bluh)

            # Print every data until last 'pre' and after first 'post' phase
            max_pre = 0
            min_post = len(processed_data)
            if len(processed_data.loc[processed_data.phase == 'pre']) > 0:
                max_pre = max(pre_data.index.values)
                print(processed_data.iloc[:max_pre].values)
            print('---------')
            if len(processed_data.loc[processed_data.phase == 'post']) > 0:
                min_post = min(post_data.index.values)
                print(processed_data.iloc[min_post:].values)
            print('===========')
            if len(processed_data.iloc[:max_pre].loc[(processed_data.phase !=
                                                      'pre')]) > 0:
                print("pre:")
                print(processed_data.iloc[:max_pre].loc[
                          processed_data.phase != 'pre'].values)
            if len(processed_data.iloc[min_post:].loc[processed_data.phase
                                                      != 'post']) > 0:
                print("post:")
                print(processed_data.iloc[min_post:].loc[
                          processed_data.phase != 'post'].values)
                print(len(pre_data), len(post_data))
        print(data.loc[data.UserId == 2009].head())
        return data

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
    pipeline.run_pipeline()
