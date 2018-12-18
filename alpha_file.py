from config import pre_ids, post_ids
import pandas as pd
import numpy as np
from loader import DataLoader

if __name__ == "__main__":
    pre_alpha = pd.DataFrame(columns=pre_ids)
    post_alpha = pd.DataFrame(columns=post_ids)
    loader = DataLoader()
    data = loader.load(quick_loading=True)
    for user in data.UserId.unique():
        print(f"Processing {user}")
        for exr in pre_alpha.columns:
            correct = data.loc[(data.UserId == user) &
                               (data.phase.isin(["pre"])) &
                               (data.ExerciseId == exr), "Correct"].values
            if len(correct) > 1:
                print(user, exr, correct)
            if len(correct)> 0:
                correct = correct[0]
                # print(correct)
                pre_alpha.loc[user, exr] = correct
        for exr in post_alpha.columns:
            correct = data.loc[(data.UserId == user) &
                               (data.phase.isin(["post"])) &
                               (data.ExerciseId == exr), "Correct"].values
            if len(correct) > 1:
                print(user, exr, correct)
            if len(correct)> 0:
                correct = int(correct[0])
                # print(correct)
                post_alpha.loc[user, exr] = correct
    alpha = pd.concat((pre_alpha, post_alpha), axis=1)
    alpha.to_csv("output/alpha_check.csv", na_rep=" ")
    print(alpha.head())


