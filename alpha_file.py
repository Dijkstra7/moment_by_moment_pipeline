from config import pre_ids, post_ids
import pandas as pd
import numpy as np
from loader import DataLoader

if __name__ == "__main__":
    # Load most recently used data
    loader = DataLoader()
    data, transfer_data = loader.load(quick_loading=True)

    # Construct alpha info data frames.
    pre_alpha = pd.DataFrame(columns=pre_ids)
    post_alpha = pd.DataFrame(columns=post_ids)
    transfer_alpha = pd.DataFrame(columns=transfer_data.ExerciseId.unique())

    # Construct dictionary for column names
    skill_dict = {}

    # Start filling in the data frames
    for user in data.UserId.unique():
        print(f"Processing {user}")
        for exr in pre_alpha.columns:
            # Retrieve correctness of answer for an exercise
            correct = data.loc[(data.UserId == user) &
                               (data.phase.isin(["pre"])) &
                               (data.ExerciseId == exr), "Correct"].values

            # Add descriptive for column name
            if "pre" + str(exr) not in skill_dict:
                loid = data.loc[(data.ExerciseId == exr), "LOID"].values[0]
                skill_dict["pre" + str(exr)] = loid

            # Check if not more than one answer was made for the same exercise.
            if len(correct) > 1:
                print(user, exr, correct)
            # Add first given correctness of answer to data frame.
            if len(correct) > 0:
                correct = correct[0]
                # print(correct)
                pre_alpha.loc[user, exr] = correct

        # Process post test.
        for exr in post_alpha.columns:
            # Retrieve correctness of answer for an exercise
            correct = data.loc[(data.UserId == user) &
                               (data.phase.isin(["post"])) &
                               (data.ExerciseId == exr), "Correct"].values

            # Add descriptive for column name
            if "post" + str(exr) not in skill_dict:
                loid = data.loc[(data.ExerciseId == exr), "LOID"].values[0]
                skill_dict["post"+str(exr)] = loid

            # Check if not more than one answer was made for the same exercise.
            if len(correct) > 1:
                print(user, exr, correct)
            # Add first given correctness of answer to data frame.
            if len(correct) > 0:
                correct = int(correct[0])
                # print(correct)
                post_alpha.loc[user, exr] = correct
            elif len(correct) == 0:
                post_alpha.loc[user, exr] = 999

        # Process transfer test answers.
        for exr in transfer_alpha.columns:
            # Retrieve correctness of answer for an exercise.
            correct = transfer_data.loc[(transfer_data.UserId == user) &
                                        (transfer_data.ExerciseId == exr),
                                        "Correct"].values

            # Check if not more than one answer was made for the same exercise.
            if len(correct) > 1:
                print("alpha error:", user, exr, correct)
            # Add first given correctness of answer to data frame.
            if len(correct) > 0:
                correct = int(correct[0])
                # print(correct)
                transfer_alpha.loc[user, exr] = correct

    # Create correct descriptives of column names.
    pre_alpha.columns = ["pre_" + str(skill_dict["pre" + str(c)]) +
                         "_" + str(c) for c in pre_alpha.columns]
    post_alpha.columns = ["post_" + str(skill_dict["post" + str(c)]) +
                          "_" + str(c) for c in post_alpha.columns]
    transfer_alpha.columns = ["transfer_7579"+str(c) for c in
                              transfer_alpha.columns]

    # Combine and save all alpha data frames.
    alpha = pd.concat((pre_alpha, post_alpha, transfer_alpha), axis=1)
    alpha.to_csv("output/alpha_check.csv", na_rep=999)
