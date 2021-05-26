import pandas as pd
from datetime import datetime
import numpy as np


def create_key_file(input="res/EndstateH.csv"):
    secret = pd.read_csv(input)
    secret.sort_values(by=["1"], inplace=True)
    students = secret["1"].unique()
    counters = {}
    key_file = pd.DataFrame(students, columns=["gynzy_id"])
    key_file["anon_id"] = ""
    key_file["groep"] = ""
    key_file["school"] = ""
    for student in students:
        class_id = secret.loc[secret["1"] == student].iloc[0, 7]
        if class_id not in counters:
            counters[class_id] = 0
        else:
            counters[class_id] += 1
        key_file["anon_id"].loc[key_file["gynzy_id"] == student] = f'{class_id}_{"%03d" % counters[class_id]}'
        key_file["school"] = "Vossenhol" if class_id == "HV7" else "De Hoeven"
        key_file["groep"] = ["H667", "H767", "H77", "H8A", "H8B", "HV7"].index(class_id)
    key_file = key_file[["anon_id", "gynzy_id", "school", "groep"]]
    key_file["voornaam"] = ""
    key_file["achternaam"] = ""
    key_file.to_csv("res/key_file.csv", index=False)
    return key_file


def convert(f_input="res/ru-data-vanaf-1maart-2021.csv"):
    # Read in Gynzy structured dataset
    data_set = pd.read_csv(f_input)
    print(data_set.columns)

    # Read in student data and extract used students and loids
    try:
        key_file = pd.read_csv("res/key_file.csv")
    except Exception as e:
        raise FileNotFoundError("You are missing the key file")
    student_ids = key_file["gynzy_id"].unique()
    loid_ids = [8209, 8216, 10071, 12402, 10488, 8220, 12520, 8234, 8214]  # Hardcoded values
    print(len(student_ids))

    # Order dataset
    data_set.sort_values(by=["createdAt", "exerciseOrderNumber"], inplace=True)

    # Clip out unnecessary data
    print("Converting to Datetime")
    data_set["createdAt"] = pd.to_datetime(data_set["createdAt"])
    data_set = data_set.loc[(data_set["createdAt"].dt.date >= pd.to_datetime("2021-03-29")) &
                            (data_set["createdAt"].dt.date < pd.to_datetime("2021-04-24")) &
                            (data_set["student"].isin(student_ids)) &
                            (data_set["microgoal"].isin(loid_ids))
                            ]

    # Create converted dataset to be processed by pipeline
    converted_set = pd.DataFrame()
    converted_set["LOID"] = data_set["microgoal"]
    converted_set["AbilityAfterAnswer"] = data_set["studentAbility"] + 2 * 25
    converted_set["Correct"] = data_set["isCorrect"].astype(int)
    converted_set["UserId"] = ""
    for student in student_ids:
        converted_set["UserId"].loc[data_set["student"] == student] = key_file[key_file["gynzy_id"] == student].iloc[
            0].anon_id
    converted_set["DateTime"] = data_set["createdAt"]
    converted_set["ExerciseId"] = data_set["exercise"]
    converted_set["phase"] = ""
    converted_set["phase"].loc[converted_set["DateTime"].dt.day.isin([29, 6, 19])] = "day1"
    converted_set["phase"].loc[converted_set["DateTime"].dt.day.isin([30, 7, 20])] = "day2"
    converted_set["phase"].loc[converted_set["DateTime"].dt.day.isin([1, 8, 14, 21])] = "day3"
    converted_set["phase"].loc[converted_set["DateTime"].dt.day.isin([2, 9, 15, 22])] = "day4"
    converted_set["phase"].loc[data_set["lesson"].isin([56186, 56192, 56189])] = "pre"
    converted_set["phase"].loc[data_set["lesson"].isin([56193, 56190, 56187])] = "post"
    converted_set["phase"].loc[data_set["lesson"].isin([56194, 56191, 56188])] = "transfer"
    converted_set["Effort"] = data_set["exerciseDifficulty"]
    converted_set["Lesson"] = data_set["lesson"]
    first_attempts = converted_set.copy()
    first_attempts = converted_set.drop_duplicates(subset=['UserId', 'ExerciseId', 'LOID'])
    return converted_set.loc[converted_set.phase != "transfer"], \
        first_attempts, \
        converted_set.loc[converted_set.phase == "transfer"], \
        pd.read_csv("res/LogdataH.csv", index_col=0, header=0, names=["index", "DateTime", "UserId", "Screen",
                                                                      "Action", "ObjectId", "Info"], parse_dates=[1])


if __name__ == "__main__":
    convert()
