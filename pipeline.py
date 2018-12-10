"""
========
Pipeline
========

The main file which specifies which steps will be taken to reach the final
long and short files.
"""
from loader import DataLoader
from processor import Processor
from saver import Saver
from config import filters
from phase_finder import PhaseFinder
import numpy as np


def run_pipeline(ql=True):
    data, first_att_data = load(ql)
    # inspect(data)
    print("Processing data")
    saver = Saver(data)
    processor = Processor(data, first_att_data, saver.short, saver.long)
    for phase in ["pre", "post"]:
        processor.count_total_correct_phase_exercises(phase)
    processor.calculate_gain()
    processor.count_total_exercises_made()
    processor.count_total_exercises_correct()
    processor.count_total_exercises_made_att()
    processor.count_total_exercises_correct_att()


    save(saver, processor)


def load(ql):
    print("Loading data")
    loader = DataLoader()
    data = loader.load(quick_loading=ql)
    if loader.quick_loaded is False:
        print("Organizing data")
        data["DateTime"] = loader.combine_date_time(data["SubmitDate"],
                                                    data["Time"])
        data = data[['DateTime', 'UserId', 'ExerciseId',
                     'LOID', 'Correct', 'AbilityAfterAnswer']]
        print("Preprocessing data")
        loader.sort_data_by(data, "DateTime")
        data = loader.filter(filters)
        data = PhaseFinder().find_phases(data)
        data = correct(data)
        loader.quick_save(data)
    first_att_data = loader.first_attempts_only(['UserId', 'ExerciseId',
                                                 'LOID'])
    return data, first_att_data


def correct(data):
    correct_phases_dict = {2106: {7789: "ap",  # on pre-day
                                  7771: "ap"},  # on rap-day
                           2011: {7789: "ap"},  # on rap-day
                           2091: {8025: "ap"},  # on rap-day
                           }
    data = PhaseFinder.correct_phases(data, correct_phases_dict)
    return data


def save(saver, processor):
    print("saving data")
    saver.short = processor.short
    saver.long = processor.long
    saver.save(f"test")


def inspect(data):
    print("Inspecting data")
    inspect_users = []
    # inspect_users = [2036]
    allowed_same_phase_next = {"pre": ["gui", "pre", "ap"],
                               "gui": ["gui", "nap", "ap", "rap", "post",
                                       "pre"],
                               "nap": ["gui", "nap", "ap", "rap", "post"],
                               "ap": ["rap", "ap", "post", "gui"],
                               "rap": ["rap", "post"],
                               "post": ["rap", "post"]}
    allowed_other_phase_next = {"pre": ["gui", "pre", "ap"],
                                "gui": ["gui", "nap", "ap", "rap", "post",
                                        "pre"],
                                "nap": ["gui", "nap", "ap", "rap", "post"],
                                "ap": ["rap", "ap", "post", "gui", "nap"],
                                "rap": ["rap", "post"],  # <- unsure
                                "post": ["rap", "post"],
                                "": ["pre", "gui"]}
    for user in data.UserId.unique():
        print ('==========\n', user)
        p = ""
        l = ""
        t = 0
        wrong_next_phase = False
        for id_, row in data.loc[(data.UserId == user)].iterrows():
            if row.LOID != l:
                checker = allowed_other_phase_next
            else:
                checker = allowed_same_phase_next
            if row.phase not in checker[p]:
                wrong_next_phase = True
            p = row.phase
            l = row.LOID

        if wrong_next_phase is True:
            for id_, row in data.loc[(data.UserId == user)
                                     &
                                     (~data.phase.isin(["pre", "post"]))
                                     ].iterrows():
                if row.phase != p:
                    if not p == "":
                        print(t+1)
                    p = row.phase
                    row = row.drop("AbilityAfterAnswer")
                    row = row.drop("Correct")
                    print(row.values, end=" ")
                    t = 0
                else:
                    t += 1
            print(t+1)
        if user in inspect_users:
            for id_, row in data.loc[(data.UserId ==
                                                user)].iterrows():
                print(row.values)


if __name__ == "__main__":
    quick_loading = True
    run_pipeline(quick_loading)
