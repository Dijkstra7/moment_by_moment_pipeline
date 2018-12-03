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
        data = loader.sort_data_by(data, "DateTime")
        data = loader.filter(filters)
        data = PhaseFinder().find_phases(data)
        loader.quick_save(data)
    # PhaseFinder.inspect_phases(data)
    # print(data.head())
    # return  # Test until here
    first_att_data = loader.first_attempts_only(['UserId', 'ExerciseId',
                                                 'LOID'])
    print("Processing data")
    saver = Saver(data)
    print(saver.short.head())
    processor = Processor(data, first_att_data, saver.short, saver.long)
    processor.count_total_exercises()
    for phase in ["pre", "post"]:
        processor.count_total_correct_phase_exercises(phase)

    # print("Inspecting data")
    # for user in processor.data.UserId.unique():
    #     print ('==========\n', user)
    #     for id_, row in processor.data.loc[processor.data.UserId ==
    #                                        user].iterrows():
    #         print(row.values)
    print("saving data")
    saver.short = processor.short
    saver.long = processor.long
    saver.save(f"test")


if __name__ == "__main__":
    quick_loading = True
    run_pipeline(quick_loading)
