import pandas as pd
import numpy as np
from convert_gynzy_csv import convert

pre_ids = [[
    56186, [933256, 933374, 933476, 933418, 933457, 933397, 933401, 933442, 887942, 1360995, 1361110, 887911, 1361000,
            1361220, 1361230, 1361055, 1447393, 1361545, 1361355, 1361465, 1361390, 1447403, 1361290, 1361510, ]],
    [
        56189, [1631348, 1630957, 1631400, 1632441, 1631361, 1631025, 1632503, 1630988, 934426, 934493, 934473, 934502,
                934422, 934418, 934463, 934477, 933281, 933476, 933416, 933284, 933399, 933401, 933397, 933258]],
    [
        56192, [894377, 894386, 894413, 893553, 1669843, 1668498, 1668500, 1668519, 902124, 902557, 902327, 902519]]]

post_ids = [
    [
        56187, [
        1361305, 1361505, 1447443, 1361400, 1361495, 1361290, 1447417, 1361490, 1360990, 1361165, 1361115, 887911,
        887972, 1361145, 1360995, 887996, 933419, 933418, 933472, 933264, 933398, 933384, 933408, 933452]
    ],
    [
        56190, [

        1631488, 1632265, 1632363, 1630971, 1631456, 1631469, 1631020, 1631541, 933268, 933252, 933256, 933272, 933287,
        933434, 933452, 933419, 934487, 934498, 934427, 934436, 934413, 934443, 934426, 934502]
    ],
    [
        56193, [
        1669843, 1669656, 1668580, 1668695, 1668533, 1669459, 1669868, 1668857, 902900, 902311, 902315, 902329, 902917,
        902938, 902554, 902893, 893321, 893073, 893125, 894135, 893174, 893167, 894188, 894438]]
]

trans_ids = [
    [
        56188, [934451, 934422, 934443, 934418, 934413, 934504, 934499, 934427, 934493, 934487, 934498, 934463, 934477,
                934436, 934426, 934473]],
    [
        56191, [894438, 894226, 894433, 893553, 893285, 893174, 893127, 894377, 894386, 893570, 894431, 894237, 893131,
                893119, 893073, 894204]],
    [56194, [926885, 1657183, 926937, 1657163, 1656988, 926942, 926872, 1657023, 1657174, 926924, 1657044, 1657068,
             926877, 1657003, 1657168, 926972]]
]

if __name__ == "__main__":
    # Load most recently used data
    data, _, transfer_data, _ = convert()

    for lesson_id in range(3):
        # Construct alpha info data frames.
        pre_alpha = pd.DataFrame(columns=pre_ids[lesson_id][1])
        post_alpha = pd.DataFrame(columns=post_ids[lesson_id][1])
        transfer_alpha = pd.DataFrame(columns=trans_ids[lesson_id][1])

        # Construct dictionary for column names
        skill_dict = {}

        # Start filling in the data frames
        for user in data.UserId.unique():
            if pre_ids[lesson_id][0] in data.loc[(data.UserId == user), "Lesson"].values or \
                    post_ids[lesson_id][0] in data.loc[(data.UserId == user), "Lesson"].values:

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
                        skill_dict["post" + str(exr)] = loid

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
        transfer_alpha.columns = ["transfer_" + str(c) for c in
                                  transfer_alpha.columns]

        # Combine and save all alpha data frames.
        alpha = pd.concat((pre_alpha, post_alpha, transfer_alpha), axis=1)
        alpha.to_csv(f"output/alpha_check_{lesson_id}.csv", na_rep=999)
