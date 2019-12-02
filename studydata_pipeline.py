import pickle

import pandas as pd
import os

from saver import Saver
from studydata_processor import StudyDataProcessor

PICKLE_QUICK_LOAD = "studydata_quicksave.pkl"

def run_studydata_pipeline(ql=True, estimate_parameters=False, id_="simone",
                           file_name=None, skipping=None, plotting=True):
    if file_name is None:
        file_name = "./res/simone_all_data_all_attempts.xlsx"
    if skipping is None:
        skipping = []
    # Load data
    data = load_studydata(ql, file_name, id_)

    # Prepare saving
    saver = Saver(data)

    # Process data
    processor = StudyDataProcessor(data, saver.short, saver.long)
    skills = data.LOID.unique()
    # Get click data
    if "click data" not in skipping:
        for skill in skills:
            processor.get_click_changes_week(skill, id_)
        for skill in skills:
            processor.get_click_changes_last_two_days(skill, id_)
        for skill in skills:
            processor.get_click_changes_third_day(skill, id_)
        for skill in skills:
            processor.get_click_changes_fourth_day(skill, id_)

    # Do saving stuff
    if "saving" not in skipping:
        save_studydata_output(saver, processor, f_name=id_)


def clean_data(data: pd.DataFrame, id_) -> pd.DataFrame:
    data.rename(columns={"learning_objective_id": "LOID",
                         "user_id": "UserId",
                         "submit_date": "SubmitDate",
                         }, inplace=True)
    print(data.columns)
    data.SubmitDate = pd.to_datetime(data.SubmitDate)
    data = data.loc[~data.LOID.isin(["8181", "7579", 8181, 7579])]
    print(data.head().values)
    return data


def load_studydata(ql, file_name, id_):
    if ql is True:
        if os.path.exists(PICKLE_QUICK_LOAD):
            data = pickle.load(open(PICKLE_QUICK_LOAD, "rb"))
            return data
    data = clean_data(pd.read_csv(file_name, index_col=1), id_)
    pickle.dump(data, open(PICKLE_QUICK_LOAD, "wb"))
    return data


def save_studydata_output(saver, processor, f_name="studydata_jm"):
    saver.short = processor.short_file
    saver.long = processor.long_file
    saver.save(f_name)


if __name__ == "__main__":
    do_skipping = [
        # "click data"
        # "saving"
    ]
    do_quick_loading = False
    do_estimate_parameters = False
    do_plotting = False
    run_studydata_pipeline(do_quick_loading, do_estimate_parameters,
                           id_="clickdata_jm",
                           file_name="./res/clickdata_jm.csv",
                           skipping=do_skipping,
                           plotting=do_plotting)
