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


def run_pipeline():
    print("Loading data")
    loader = DataLoader()
    data = loader.load()
    print("Organizing data")
    data["DateTime"] = loader.combine_date_time(data["SubmitDate"],
                                                data["Time"])
    data = data[['DateTime', 'UserId', 'ExerciseId',
                 'LOID', 'Correct', 'AbilityAfterAnswer']]
    print("Preprocessing data")
    data = loader.sort_data_by(data, "DateTime")
    data = loader.filter(filters)
    data = PhaseFinder.find_phases(data)
    return  # Test until here
    first_att_data = loader.first_attempts_only(['UserId', 'ExerciseId',
                                                 'LOID'])
    print("Processing data")
    saver = Saver(data)
    print(saver.short.head())
    processor = Processor(data, first_att_data, saver.short, saver.long)
    processor.count_total_exercises()
    processor.count_pre_exercises()
    print(processor.short.head())
    print("saving data")
    saver.short = processor.short
    saver.long = processor.long
    saver.save(f"test")


if __name__ == "__main__":
    run_pipeline()
