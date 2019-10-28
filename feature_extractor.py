"""
=================
feature extractor
=================

Used to extract features from both the elo curves from students and
additional information. These features are used to cluster the ELO curves
into different categories.
"""
# import numpy as np
import pandas as pd
import os

from tqdm import tqdm

from config import filters
from loader import DataLoader
from phase_finder import PhaseFinder


def create_feature_number_exercises(selected_data):
    """
    Create the number of exercises feature

    Parameters
    ----------
    selected_data: pd.DataFrame
        the data from which the feature will be calculated

    Returns
    -------
    int
        the number of exercises in the selected data
    """
    value = len(selected_data)
    return value


def create_feature_pre_post_gain(selected_data):
    """
    Create the feature of gain between pre and post

    Parameters
    ----------
    selected_data: pd.DataFrame
        the data from which the feature will be calculated

    Returns
    -------
    int
        the number of exercises correct gained between pre and post
    """
    pre = selected_data.loc[selected_data.phase == "pre"]
    post = selected_data.loc[selected_data.phase == "post"]
    good_pre = len(pre.loc[pre.Correct != 0])
    good_post = len(post.loc[post.Correct != 0])

    value = good_post - good_pre
    return value


def create_feature_relative_position_highest_elo(selected_data):
    """
    feature of relative position of highest elo

    calculated by (total of exercises made until last highest elo) /
                  (total of exercises made)
    Parameters
    ----------
    selected_data

    Returns
    -------
    float
        relative position of highest elo achieved
    """
    total_exercises_made = create_feature_number_exercises(selected_data)
    highest_elo_id = create_feature_get_highest_elo_id(selected_data)
    return 1. * (highest_elo_id + 1) / total_exercises_made


def create_feature_get_highest_elo_id(selected_data):
    elo_data = selected_data.AbilityAfterAnswer.values
    highest_elo = elo_data[0]
    highest_elo_id = 0
    for elo_id, elo in enumerate(elo_data):
        if elo >= highest_elo:
            highest_elo = elo
            highest_elo_id = elo_id
    return highest_elo_id


def create_feature_highest_elo(selected_data):
    """
    feature of highest elo

    Parameters
    ----------
    selected_data

    Returns
    -------
    float
        highest elo achieved
    """
    elo_data = selected_data.AbilityAfterAnswer.values
    highest_elo = max(elo_data)
    return highest_elo


def create_feature_total_gain_elo_score(selected_data):
    first_elo = selected_data.AbilityAfterAnswer.values[0]
    last_elo = selected_data.AbilityAfterAnswer.values[-1]
    elo_gain = last_elo - first_elo
    return elo_gain


def create_feature_difference_highest_elo_and_last(selected_data):
    highest_reached = max(selected_data.AbilityAfterAnswer.values)
    last_elo = selected_data.AbilityAfterAnswer.values[-1]
    difference = highest_reached - last_elo
    return difference


def create_feature_difference_highest_elo_and_lowest_afterwards(selected_data):
    highest_reached_id = create_feature_get_highest_elo_id(selected_data)
    highest_elo_value = selected_data.AbilityAfterAnswer.values[
        highest_reached_id]
    if highest_reached_id == len(selected_data):
        return 0
    lowest_elo_afterwards = min(selected_data.AbilityAfterAnswer.values[
                                highest_reached_id:])
    return highest_elo_value - lowest_elo_afterwards


def cluster(data: pd.DataFrame, k=5, method=None,
            save_dir="./output/clusters/kb.csv"):
    """
    Cluster the curves

    The features of the curves are extracted for all possible curves.
    Afterwards a selected method to cluster the curves is used.

    Parameters
    ----------
    data: Pandas.DataFrame
        The data contained in a Pandas DataFrame.
    k: int or None
        Number of curves to be clustered
    method: str or None
        Method to be used to cluster the curves
    save_dir: str
        relative path to where the clusters are saved in a csv file.

    """
    implemented_methods = ["K-means", "Agglomarate_clustering"]
    features = extract_features(data)

    # for item, row in features.iterrows():  # Testing: to see progress
    #     print([round(r, 2) for r in row.values])

    if method not in implemented_methods:
        raise NotImplementedError(f"The {method} method is not yet "
                                  f"implemented")

    features["cluster"] = 0
    if k is not None:  # TODO: Start clustering with selected features?
        print(f"TODO: implement clustering method of method {method} with {k} "
              f"clusters")
    else:
        print(f"TODO: implement clustering method of method {method} with an "
              f"undetermined amount of clusters")
    features.to_csv(save_dir)


def extract_features(data: pd.DataFrame) -> pd.DataFrame:
    feature_frame = create_feature_frame(data)
    features = [
        "pre_post_gain",
        "total_gain_elo_score",
        "highest_elo",
        "relative_position_highest_elo",
        "difference_highest_elo_and_last",
        "difference_highest_elo_and_lowest_afterwards",
    ]
    # for feature in featureset:
    #     create_feature(feature)
    feature_funcs = []
    for feature in features:
        feature_frame[feature] = None
        feature_funcs.append(globals()[f"create_feature_{feature}"])

    for user in tqdm(feature_frame.user.unique(), desc="extracting features"):
        for loid in feature_frame.loid.unique():
            for feature, feature_func in zip(features, feature_funcs):
                selected_data = data.loc[(data.UserId == user) &
                                         (data.LOID == loid)]
                feature_frame.loc[(feature_frame.user == user) &
                                  (feature_frame.loid == loid),
                                  feature] = feature_func(selected_data)
    return feature_frame


def create_feature_frame(data):
    """
    Create the pandas.DataFrame that will contain the values of the features.

    Returns
    -------
    pd.DataFrame
        The empty data frame for the feature container.
    """
    triple_users = []
    for user in data.UserId.unique():
        for i in range(3):
            triple_users.append(user)
    loids = list(data.LOID.unique())
    loids_per_user = [loids[i % 3] for i in range(len(triple_users))]
    feature_frame = pd.DataFrame({"user": triple_users,
                                  "loid": loids_per_user})
    return feature_frame


def load_data(data_loc):
    """
    Load the data from amn external excel resource.

    Parameters
    ----------
    data_loc: str
        Path to the data.

    Returns
    -------
    pd.DataFrame
        Data frame containing the data with additional pre and post phases
        added.
    """
    loader = DataLoader(f_name=data_loc, s_name="Blad1")
    loaded_data, _ = loader.load(quick_loading=True)
    if 'phase' in loaded_data.columns:
        loaded_data = loaded_data[['DateTime', 'UserId', 'ExerciseId',
                                   'LOID', 'Correct', 'AbilityAfterAnswer',
                                   'Effort', 'Lesson', 'LessonProgress',
                                   'phase']]
    else:
        loaded_data = loaded_data[['DateTime', 'UserId', 'ExerciseId',
                                   'LOID', 'Correct', 'AbilityAfterAnswer',
                                   'Effort', 'Lesson', 'LessonProgress']]
    loaded_data = loader.filter(filters, df=loaded_data)
    if not loader.quick_loaded:
        loaded_data = PhaseFinder().find_gynzy_phases_with_lesson_info(
            loaded_data, "")
        loader.quick_save(loaded_data)
    return loaded_data


def create_dir_if_not_exists(dir_str):
    """
    Create the directory if it does not exist already

    Checks whether the directory exists. If it does not exist it will create it
    one folder at a time.

    Parameters
    ----------
    dir_str: str
        path that will be created. must start with ./ to indicate that it is a
        relative path.

    Raises
    ------
    ValueError:
        When the given path is not a relative path from the current dir.
    """
    dir_str_split = dir_str.split('/')
    if dir_str_split[0] != ".":
        raise ValueError("New path must start with './' to indicate that it "
                         "is a relative path")
    if ".." in dir_str_split:
        raise ValueError("Path cannot contain '..' as this might change the "
                         "path to a different directory.")
    if not os.path.exists(dir_str):
        for i in range(2, len(dir_str_split)):
            dir_str_joined = "/".join(dir_str_split[:i])
            if not os.path.exists(dir_str_joined):
                os.mkdir(dir_str_joined)
        os.mkdir(dir_str)


if __name__ == "__main__":
    data_location = "./res/data_kb_all_tests_info.xlsx"
    use_data = load_data(data_location)
    cluster(use_data, k=6, method="K-means")
