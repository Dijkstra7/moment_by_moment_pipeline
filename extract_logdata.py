"""
This file extracts log data.

At the moment only log data from one experiment is extracted, so the
approach is not very general yet.
"""
import os
from datetime import datetime

import pandas as pd
import pickle


identifier = "jm"
students = []


def extract_opened_curve_data(data:pd.DataFrame) -> pd.DataFrame:
    return data.loc[(data.screen == 3) & (data.action == 2)]


def process_opened_data_per_loid_sum(data: pd.DataFrame,
                                     results: pd.DataFrame,
                                     screen="curve") -> \
        pd.DataFrame:
    for loid in [8232, 8234, 8240]:
        results[f"opened_{screen}_{loid}"] = ""
    for student in data.user_id.unique():
        student_data = data.loc[(data.user_id == student)]
        for loid in [8232, 8234, 8240]:
            # info_prev = None
            # print(results.head(1))
            results.loc[student, f"opened_{screen}_{loid}"] = len(
                student_data.loc[
                    (str(loid) == student_data["info"].astype(str).str[-4:])
                    | (str(loid) == student_data["object_id"].astype(str))
            ])
            # loid_data = student_data.loc[str(loid) == student_data[
            #     "loid"]]
            # print(f"Data for student {student} and loid {loid}")
            # for info_part in loid_data["info"]:
            #     if info_prev != info_part:
            #         print(info_part)
            #         info_prev = info_part
    return results


def extract_all_overview_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[((data.screen == 1) & (data.action == 4)) |
                    ((data.screen == 3) & (data.action == 0))]


def extract_opened_overview_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[(data.screen == 1) & (data.action == 4)]


def extract_opened_goal_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[(data.screen == 2) & (data.action == 1)]


def process_all_overview_data(data: pd.DataFrame, results: pd.DataFrame,
                                 screen="overview"):
    results[f"all_{screen}"] = ""
    for student in data.user_id.unique():
        student_data = data.loc[(data.user_id == student)]
        results.loc[student, f"all_{screen}"] = len(student_data)
    return results


def process_opened_overview_data(data: pd.DataFrame, results: pd.DataFrame,
                                 screen="overview"):
    results[f"opened_{screen}"] = ""
    for student in data.user_id.unique():
        student_data = data.loc[(data.user_id == student)]
        results.loc[student, f"opened_{screen}"] = len(student_data)
    return results


def get_users_from_normal_data(students_file):
    try:
        students_data = pd.read_csv(f"{students_file}.csv")
    except Exception:
        students_data = pd.read_excel(f"{students_file}.xlsx")
    return students_data["UserId"].values


def run(quick_load=False, file_name="", students_file=None):
    if file_name is None or len(file_name) == 0:
        file_name = f"res/logdata_{identifier}"
    if students_file is not None:
        students = get_users_from_normal_data(students_file)
    data = load_data(quick_load, file_name)
    print(data.head(), data.info())
    all_overview_data = extract_all_overview_data(data)
    opened_curve_data = extract_opened_curve_data(data)
    opened_overview_data = extract_opened_overview_data(data)
    opened_goal_data = extract_opened_goal_data(data)
    opened_goal_data["loid"] = opened_goal_data["info"].astype(str).str[-4:]
    opened_curve_data["loid"] = opened_curve_data["info"].astype(str).str[-4:]
    # opened_curve_data.to_csv(f"output/seen_data_{identifier}.csv")
    results = pd.DataFrame(data.user_id.unique(), columns=["student"])
    results.set_index("student", inplace=True)
    # print(opened_curve_data.head(20))
    # results = process_all_overview_data(all_overview_data, results,
    #                                        "overview")
    # results = process_opened_data_per_loid_sum(opened_curve_data, results,
    #                                            "curve")
    # results = process_opened_data_per_loid_sum(opened_goal_data, results,
    #                                            "goal")
    # results = process_opened_overview_data(opened_overview_data, results,
    #                                     "overview")
    flag_data = extract_flag_data(data)
    results = process_flag_data(flag_data, results)

    # print(sum_seen_curve_data.head(20))
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    results.to_csv(f"output/sum_seen_data_{identifier}2_{now}.csv")

def load_data(quick_load: bool, file_name: str) -> pd.DataFrame:
    data = None
    if quick_load is True:
        if not os.path.exists(f"quicksaves/{file_name.split('/')[-1]}"):
            try:
                data = pd.read_csv(f"{file_name}.csv")
            except Exception:
                data = pd.read_excel(f"{file_name}.xlsx")
            pickle.dump(data,
                        open(f"./quicksaves/{file_name.split('/')[-1]}.pkl",
                        "wb"))
        else:
            data = pickle.load(open(
                f"./quicksaves/{file_name.split('/')[-1]}.pkl", "rb"))
    else:
        try:
            data = pd.read_csv(f"{file_name}.csv")
        except Exception:
            data = pd.read_excel(f"{file_name}.xlsx")
        pickle.dump(data,
                    open(f"./quicksaves/{file_name.split('/')[-1]}.pkl",
                         "wb"))
    return data


def extract_flag_data(data: pd.DataFrame) -> pd.DataFrame:
    return data.loc[((data.screen == 3) & (data.action == 3)) |
                    ((data.screen == 2) & (data.action == 1))]

def process_flag_data(data, results):
    phases = ["", "first", "repeat", "all"]
    for loid in [8232, 8234, 8240]:
        for i in range(1, 4):
            results[f"flag_{phases[i]}_set_for_{loid}"] = ""
    for student in data.user_id.unique():
        print(student)
        student_data = data.loc[(data.user_id == student)]
        # print(student_data)
        first_screen = student_data.iloc[0].screen
        if first_screen != 2 and student != 15909444:
            raise RuntimeError(f"Niet begonnen met het juiste scherm "
                               f"student: {student}")
        current_loid = student_data.loc[student_data.screen == 2].iloc[
            0].object_id
        for index, row in student_data.iterrows():
            if row.screen == 2:
                current_loid = row.object_id
            else:
                results.loc[student, f"flag_{phases[row.object_id]}_set_for"
                                 f"_{current_loid}"] = row.info
    return results



if __name__ == "__main__":
    run(quick_load=False, file_name=f"res/logdata (4)",
        students_file=f"res/data_jm")
