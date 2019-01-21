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
from config import filters, transfer_filters
from phase_finder import PhaseFinder, pre_ids as pi
import numpy as np


def run_pipeline(ql=True):
    data, first_att_data, transfer_data = load(ql)
    # inspect(data)
    print(transfer_data.LOID.head())
    print("Processing data")
    saver = Saver(data)
    phases = ["pre", "gui", "nap", "ap", "rap", "post"]
    skills = data.LOID.unique()
    processor = Processor(data, first_att_data, saver.short, saver.long,
                          phases)
    for phase in ["pre", "post"]:
        processor.count_total_correct_phase_exercises(phase)
    processor.calculate_gain()
    processor.get_transfer_score(transfer_data)
    processor.count_total_exercises_made()
    processor.count_total_exercises_correct()
    processor.count_total_exercises_made_att()
    processor.count_total_exercises_correct_att()
    for phase in ["pre", "post"]:
        for skill in skills:
            processor.skill_count_total_correct_phase_exercise(skill, phase)
    for skill in skills:
        processor.calculate_gain_per_skill(skill)
    for skill in skills:
        processor.get_last_ability_of_skill(skill)
    for skill in skills:
        processor.count_total_exercises_made_per_skill(skill)
    for skill in skills:
        processor.count_total_exercises_correct_per_skill(skill)
    for skill in skills:
        processor.calculate_percentage_correct_per_skill(skill)
    for skill in skills:
        processor.count_total_exercises_made_att_per_skill(skill)
    for skill in skills:
        processor.count_total_exercises_correct_att_per_skill(skill)
    for skill in skills:
        processor.calculate_percentage_correct_att_per_skill(skill)
    for skill in skills:
        processor.count_total_adaptive_per_skill(skill)
    for skill in skills:
        processor.count_correct_adaptive_per_skill(skill)
    for skill in skills:
        processor.calculate_percentage_correct_adaptive_per_skill(skill)
    for skill in skills:
        processor.count_total_adaptive_att_per_skill(skill)
    for skill in skills:
        processor.count_correct_adaptive_att_per_skill(skill)
    for skill in skills:
        processor.calculate_percentage_correct_adaptive_att_per_skill(skill)
    for skill in skills:
        processor.add_skill_to_long_file(skill)
    for skill in skills:
        processor.process_curves(skill, method="exclude_single_strays",
                                 do_plot=True)
    for skill in skills:
        processor.calculate_type_curve(skill)
    for skill in skills:
        processor.get_phase_of_last_peak(skill)
    for skill in skills:
        processor.get_phase_of_last_peak(skill)
    for phase in phases:
        for skill in skills:
            processor.count_first_attempts_per_skill(phase, skill)
    # FOR TESTING ONLY<- DO REMOVE
    # for phase in ["pre", "post"]:
    #     for skill in skills:
    #         processor.count_total_phase_exercises(phase, skill)
    # END TESTING
    for skill in skills:
        processor.calculate_general_spikiness(skill)
    for skill in skills:
        processor.calculate_phase_spikiness(skill, phases)
    for skill in skills:
        processor.get_total_amount_of_peaks(skill)
    for phase in phases:
        for skill in skills:
            processor.get_peaks_per_skill_per_phase(skill, phase)
    for skill in skills:
        processor.get_total_amount_of_trans_peaks(skill)
    for phase in phases:
        for skill in skills:
            processor.get_trans_peaks_per_skill_per_phase(skill, phase)

    save(saver, processor, f_name="leerpaden")


def load(ql):
    print("Loading data")
    loader = DataLoader(f_name="./res/leerpaden_app.xlsx", s_name="Blad1")
    data, transfer_data = loader.load(quick_loading=ql)
    if loader.quick_loaded is False:
        print("Organizing data")
        # data["DateTime"] = loader.combine_date_time(data["SubmitDate"],
        #                                             data["Time"])
        data = data[['DateTime', 'UserId', 'ExerciseId',
                     'LOID', 'Correct', 'AbilityAfterAnswer']]
        print("Preprocessing data")
        unfiltered = loader.sort_data_by(data, "DateTime")
        transfer_data = loader.filter(transfer_filters)
        data = loader.filter(filters, df=unfiltered)
        data = PhaseFinder().find_phases(data)
        # data = correct(data)
        loader.quick_save(transfer_data, f_name="quicktransfer.pkl")
        loader.quick_save(data)
    first_att_data = loader.first_attempts_only(['UserId', 'ExerciseId',
                                                 'LOID'], df=data)
    return data, first_att_data, transfer_data


def correct(data):
    correct_phases_dict = {3013: {7789: "ap",  # on pre-day
                                  7771: "ap"},  # on rap-day
                           2011: {7789: "ap"},  # on rap-day
                           2091: {8025: "ap"},  # on rap-day
                           }
    data = PhaseFinder.correct_phases(data, correct_phases_dict)
    return data


def save(saver, processor, f_name="test"):
    print("saving data")
    saver.short = processor.short
    saver.long = processor.long
    saver.save(f_name)


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
        len_pre = len(data.loc[(data.phase == "pre") & (data.UserId == user)])
        len_post = len(data.loc[(data.phase == "post") &
                                (data.UserId == user)])
        if wrong_next_phase is True or len_post != 24 or len_pre != 24:
            len_all_pre = len(data.loc[(data.ExerciseId.isin(pi))
                                        & (data.UserId == user)])
            print(f"Total pre-ids:{len_all_pre}")
            for id_, row in data.loc[(data.UserId == user)
                                     # &
                                     # (~data.phase.isin(["pre", "post"]))
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
            for id_, row in data.loc[(data.UserId == user)].iterrows():
                print(row.values)


if __name__ == "__main__":
    quick_loading = True
    run_pipeline(quick_loading)
