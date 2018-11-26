"""
============
Phase finder
============

Set the phase next to the data.
"""

import pandas as pd
import numpy as np
from config import pre_ids, post_ids, nap_ids, gui_ids


class PhaseFinder:

    @staticmethod
    def find_phases(data: pd.DataFrame):
        data["phase"] = ""
        for user in data.UserId.unique():
            print(f"processing {user}")
            user_data = data.loc[data.UserId == user].sort_values("DateTime")\
                .reset_index()
            pre_min_id = len(pre_ids)+1
            post_min_id = len(user_data)-len(post_ids)-1
            ap_day = {}
            for id_, row in user_data.iterrows():

                if row.ExerciseId in pre_ids:
                    if id_ <= pre_min_id:
                        data.phase.loc[row['index']] = "pre"
                    else:
                        # print(f"{id_}: found another pre")
                        pass

                if row.ExerciseId in post_ids:
                    if id_ >= post_min_id:
                        data.phase.loc[row['index']] = "post"
                    else:
                        # print(f"{id_}: found another post")
                        pass

                if row.ExerciseId in gui_ids:
                    data.phase.loc[row['index']] = "gui"

                if row.ExerciseId in nap_ids:
                    data.phase.loc[row['index']] = "nap"

                if row.ExerciseId not in nap_ids + gui_ids:
                    if len(data.phase.loc[row['index']]) > 0:
                        continue
                    if row.LOID not in ap_day:
                        print(row.values, row.index)
                        data.phase.loc[row['index']] = "ap"
                        ap_day[row.LOID] = row.DateTime.day
                    elif row.DateTime.day == ap_day[row.LOID]:
                        data.phase.loc[row['index']] = "ap"
                    else:
                        data.phase.loc[row['index']] = "rap"

                # print(id_, row['index'], row.DateTime, row.DateTime.day,
                #       row.LOID, data.phase.loc[row['index']],
                #       row.ExerciseId, ap_day)

            processed_data = data.loc[data.UserId == user]\
                .reset_index(drop=True)
            pre_data = processed_data.loc[processed_data.phase == 'pre']

            if len(pre_data) < len(pre_ids):
                missing_pre = pre_ids[:]
                for id_ in pre_data.ExerciseId.values[:pre_min_id]:
                    if id_ in missing_pre:
                        missing_pre.remove(id_)
                    else:
                        print(id_)
                print(f"Too short{user}: {len(pre_data)} - [{missing_pre}]")

                for bluh in processed_data.values:
                    print(bluh)
                print(ap_day)
            else:
                pass
                # print(processed_data.loc[
                #           (processed_data.ExerciseId.isin(pre_ids)) &
                #           (processed_data.index > 24)
                #       ].values)
        # Print every data until last 'pre' phase
        max_pre = max(pre_data.index.values)
        print(processed_data.iloc[:max_pre].values)
        return data

if __name__ == "__main__":
    import pipeline
    pipeline.run_pipeline()