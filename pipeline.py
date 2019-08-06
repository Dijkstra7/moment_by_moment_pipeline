"""
========
Pipeline
========

The main file which specifies which steps will be taken to reach the final
long and short files.
"""
import os

from loader import DataLoader
from processor import Processor
from saver import Saver
from config import filters, transfer_filters, GYNZY
from phase_finder import PhaseFinder, pre_ids as pi


def run_pipeline(ql=True, estimate_parameters=False, id_="simone",
                 file_name=None):
    """
    Main program that runs the pipeline processing all data.

    Loads the data and cleans it, then processes the data for the pipeline.
    Different sources need some methods to be different, their source is
    indicated with the id_ tag. Quick loading is possible to decrease the
    read-in and cleaning of the file. Needs to be set to False to load a new
    source_file.
    Is able to also estimate the parameters for the file.

    Parameters
    ----------
    ql: bool
        whether the data should be reloaded from a preprocessed file.
    estimate_parameters: bool
        whether the parameters for the curves should be estimated.
    id_: str
        The identifier for the source
    file_name: str
        Path to the file.

    Returns
    -------
    None
    """
    # Set up variables.
    phases = ["pre", "gui", "nap", "ap", "rap", "post"]
    if file_name is None:
        file_name = "./res/simone_all_data_all_attempts.xlsx"

    # Load and preprocess data.
    data, first_att_data, transfer_data, log_data = load(
        ql, file_name, id_)
    skills = data.LOID.unique()

    # Inspect the data to determine whether preprocessing was performed correct
    # inspect(data)
    # return None
    print(transfer_data.LOID.head())
    print("Processing data")

    # Initiate creation of save file
    saver = Saver(data)
    processor = Processor(data, first_att_data, saver.short, saver.long,
                          phases, log_data)
    if estimate_parameters is True:
        parameters = processor.estimate_parameters(skills, grain=1000)

    # Start the processing of the different variables.
    # General stuff
    for skill in skills:
        processor.add_skill_to_long_file(skill)

    # Pre/post stuff
    for phase in ["pre", "post"]:
        processor.count_total_correct_phase_exercises(phase)
    processor.calculate_gain()

    processor.get_transfer_score(transfer_data)

    # Total exercises stuff
    processor.count_total_exercises_made()
    processor.count_total_exercises_correct()
    processor.count_total_exercises_made_att()
    processor.count_total_exercises_correct_att()

    # Per skill stuff
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

    # Curve stuff
    # # FOR TESTING ONLY
    # # for skill in skills:
    # #     processor.process_wrong_curves(skill,
    # #         method="exclude_single_strays", do_plot=True)
    # # FOR TESTING ONLY
    for skill in skills:
        if not os.path.exists(f'./plots/{id_}'):
            os.mkdir(f'./plots/{id_}')
        processor.process_curves(skill, method="exclude_single_strays",
                                 do_plot=True, folder=id_, add_elo=True)
    for skill in skills:
        processor.calculate_type_curve(skill)
    for skill in skills:
        processor.get_phase_of_last_peak(skill)
    for skill in skills:
        processor.get_phase_of_last_peak(skill)
    for phase in phases:
        for skill in skills:
            processor.count_first_attempts_per_skill(phase, skill)
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

    # Per lesson stuff
    try:
        for skill in skills:
            processor.get_last_ability_first_lesson_of_skill(skill, id_)
        for skill in skills:
            processor.get_total_exercises_made_first_lesson(skill, id_)
        for skill in skills:
            processor.get_total_exercises_correct_first_lesson(skill, id_)
        for skill in skills:
            processor.calculate_percentage_correct_first_lesson_total(skill,
                                                                      id_)
    except NotImplementedError:
        pass
    try:
        for skill in skills:
            processor.get_unique_exercises_made_first_lesson(skill, id_)
        # for skill in skills:
        #     processor.get_unique_exercises_correct_first_lesson(skill, id_)
        for skill in skills:
            processor.calculate_percentage_correct_first_lesson_unique(skill,
                                                                       id_)
        for skill in skills:
            processor.get_total_exercises_made_second_lesson(skill, id_)
        for skill in skills:
            processor.get_total_exercises_correct_second_lesson(skill, id_)
        for skill in skills:
            processor.calculate_percentage_correct_second_lesson_total(skill,
                                                                       id_)
    except NotImplementedError:
        pass
    try:
        for skill in skills:
            processor.get_unique_exercises_made_second_lesson(skill, id_)
        for skill in skills:
            processor.get_unique_exercises_correct_second_lesson(skill, id_)
        for skill in skills:
            processor.calculate_percentage_correct_second_lesson_unique(skill,
                                                                        id_)
        for skill in skills:
            processor.detect_missing_skill_first_lesson(skill, id_)
        for skill in skills:
            processor.detect_missing_skill_repeat_lesson(skill, id_)
    except NotImplementedError:
        pass

    if id_ in ["kb"]:
        for skill in skills:
            processor.calculate_average_effort(skill, id_)
        for skill in skills:
            processor.calculate_total_effort(skill, id_)
    # for skill in skills:
    #     for moment in [1, 2, 3]:
    #         processor.get_setgoal(skill, moment)
    # for skill in skills:
    #     processor.get_shown_path_after_first_lesson(skill)
    #     processor.get_shown_path_after_repeat_lesson(skill)

    save(saver, processor, f_name=id_)


def load(ql, f_name="./res/leerpaden_app.xlsx", id_="simone"):
    print("Loading data")
    loader = DataLoader(f_name=f_name, s_name="Blad1")
    data, transfer_data = loader.load(quick_loading=ql)
    log_data = loader.load_log()
    if loader.quick_loaded is False:
        print("Organizing data")
        # data["DateTime"] = loader.combine_date_time(data["SubmitDate"],
        #                                             data["Time"])

        data = data[['DateTime', 'UserId', 'ExerciseId',
                     'LOID', 'Correct', 'AbilityAfterAnswer', 'Effort']]
        print("Preprocessing data")
        if not id_ in ["kb"]:
            unfiltered = loader.sort_data_by(data, "DateTime")
        else:
            unfiltered = data
        transfer_data = loader.first_attempts_only(['UserId', 'ExerciseId',
                                                    'LOID'],
                                                   df=transfer_data,
                                                   copy_df=False)
        data = loader.filter(filters, df=unfiltered)
        print(data.head())
        if id_ in ["karlijn_en_babette", "kb"]:
            data = PhaseFinder().find_gynzy_phases(data, id_)
        else:
            data = PhaseFinder().find_phases(data)
            data = correct(data)
        loader.quick_save(transfer_data, f_name="quicktransfer.pkl")
        loader.quick_save(data)
    first_att_data = loader.first_attempts_only(['UserId', 'ExerciseId',
                                                 'LOID'], df=data)
    print(data.loc[data.UserId == 59491].tail(40).values)
    return data, first_att_data, transfer_data, log_data


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
    inspect_users = [118472]
    inspect_users = data.UserId.unique()
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
    for user in inspect_users:  # data.UserId.unique():
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
            d = row.DateTime.day
            l = row.LOID
        len_pre = len(data.loc[(data.phase == "pre") & (data.UserId == user)])
        len_post = len(data.loc[(data.phase == "post") &
                                (data.UserId == user)])
        if len_post != 24 or len_pre != 24:  # or wrong_next_phase is True:

            len_all_pre = len(data.loc[(data.ExerciseId.isin(pi))
                                        & (data.UserId == user)])
            print(f"Total pre-ids:{len_pre}")
            print(f"Total post-ids:{len_post}")
            for id_, row in data.loc[(data.UserId == user)
                                     # &
                                     # (~data.phase.isin(["pre", "post"]))
                                     ].iterrows():
                if row.phase != p or row.DateTime.day != d:
                    row = row.drop("AbilityAfterAnswer")
                    row = row.drop("Correct")
                    if row.phase != p:
                        if not p == "":
                            print(t+1)
                        p = row.phase
                        print(row.values, end=" ")
                        t = 0
                    else:
                        t += 1
                    if row.DateTime.day != d:
                        d = row.DateTime.day
                        print(f"[{d} {row.LOID} '{row.phase}']", end=" ")
            print(t+1)
        if user in [3112] or (len_pre != 24 and len_pre > 0):
            for id_, row in data.loc[(data.UserId == user)].iterrows():
                print(row.values)


if __name__ == "__main__":
    quick_loading = False
    estimate_parameters = False
    run_pipeline(quick_loading, estimate_parameters, id_="kb",
                 file_name="./res/data_kb.xlsx")
