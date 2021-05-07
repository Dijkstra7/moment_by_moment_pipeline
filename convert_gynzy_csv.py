import pandas as pd
from datetime import datetime
import numpy as np


def create_key_file(input="res/EndstateH.csv"):
    secret = pd.read_csv(input)
    secret.sort_values(by=["1"], inplace=True)
    students = secret["1"].unique()
    counters={}
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


def convert(f_input="res/ru-data-vanaf-1maart-2021.csv", student_data="res/EndstateH.csv"):
    # Read in Gynzy structured dataset
    data_set = pd.read_csv(f_input)
    print(data_set.columns)

    # Read in student data and extract used students and loids
    try:
        key_file = pd.read_csv("res/key_file.csv")
    except Exception as e:
        raise FileNotFoundError("You are missing the key file")
    student_ids = key_file["gynzy_id"].unique()
    loid_ids = [8209, 8216, 10071, 12402, 10488, 8220, 12520]  # Hardcoded values
    print(len(student_ids))

    # Order dataset
    data_set.sort_values(by=["createdAt", "exerciseOrderNumber"], inplace=True)

    # Clip out unnecessary data
    print("Converting to Datetime")
    data_set["createdAt"] = pd.to_datetime(data_set["createdAt"])
    data_set = data_set.loc[(data_set["createdAt"].dt.date >= pd.to_datetime("2021-03-29")) &
                            (data_set["createdAt"].dt.date < pd.to_datetime("2021-04-22")) &
                            (data_set["student"].isin(student_ids)) &
                            (data_set["microgoal"].isin(loid_ids))
    ]

    # Create converted dataset to be processed by pipeline
    converted_set = pd.DataFrame()
    converted_set["LOID"] = data_set["microgoal"]
    converted_set["AbilityAfterAnswer"] = data_set["studentAbility"]
    converted_set["Correct"] = data_set["isCorrect"] == "TRUE"
    converted_set["UserId"] = ""
    for student in student_ids:
        converted_set["UserId"] = key_file[key_file["gynzy_id"] == student].iloc[0].anon_id
    converted_set["DateTime"] = data_set["createdAt"]
    converted_set["phase"] = ""
    converted_set["phase"].loc[data_set["lesson"].isin([56186])] = "pre"  # TODO Find out other lessons matching pre-test
    converted_set["phase"].loc[data_set["lesson"].isin([56186])] = "post"
    return converted_set



if __name__ == "__main__":
    convert()