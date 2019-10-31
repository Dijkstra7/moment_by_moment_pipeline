"""
=================
feature extractor
=================

Used to extract features from both the elo curves from students and
additional information. These features are used to cluster the ELO curves
into different categories.
"""
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
from matplotlib import pyplot as plt

from sklearn import preprocessing
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth, DBSCAN, \
    AffinityPropagation

from config import filters
from loader import DataLoader
from phase_finder import PhaseFinder


MINIMUM_DIFFERENCE = 5


all_increasing_slopes = {}
all_plateaus = {}
all_decreasing_slopes = {}


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


def create_feature_length_longest_increasing_slope(selected_data):
    user = selected_data.UserId.values[0]
    loid = selected_data.LOID.values[0]
    slopes = all_increasing_slopes[(user, loid)]
    length_slopes = [s[0][1]-s[0][0] for s in slopes]
    if len(length_slopes) < 1:
        return 0
    return max(length_slopes)


def create_feature_height_highest_increasing_slope(selected_data):
    user = selected_data.UserId.values[0]
    loid = selected_data.LOID.values[0]
    slopes = all_increasing_slopes[(user, loid)]
    height_slopes = [s[1][1]-s[1][0] for s in slopes]
    if len(height_slopes) < 1:
        return 0
    return max(height_slopes)


def create_feature_length_longest_decreasing_slope(selected_data):
    user = selected_data.UserId.values[0]
    loid = selected_data.LOID.values[0]
    slopes = all_decreasing_slopes[(user, loid)]
    length_slopes = [s[0][1]-s[0][0] for s in slopes]
    if len(length_slopes) < 1:
        return 0
    return max(length_slopes)


def create_feature_height_highest_decreasing_slope(selected_data):
    user = selected_data.UserId.values[0]
    loid = selected_data.LOID.values[0]
    slopes = all_decreasing_slopes[(user, loid)]
    height_slopes = [s[1][1]-s[1][0] for s in slopes]
    if len(height_slopes) < 1:
        return 0
    return max(height_slopes)


def create_feature_length_longest_plateau(selected_data):
    user = selected_data.UserId.values[0]
    loid = selected_data.LOID.values[0]
    plateaus = all_plateaus[(user, loid)]
    length_plateaus = [s[0][1]-s[0][0] for s in plateaus]
    if len(length_plateaus) < 1:
        return 0
    return max(length_plateaus)


def create_feature_number_of_plateaus(selected_data):
    user = selected_data.UserId.values[0]
    loid = selected_data.LOID.values[0]
    plateaus = all_plateaus[(user, loid)]
    length_plateaus = [s[0][1]-s[0][0] for s in plateaus]
    return len(length_plateaus)


def create_feature_number_of_peaks(selected_data):
    curve = selected_data.AbilityAfterAnswer.values
    peaks = 0
    for i in range(1, len(curve)-1):
        if curve[i-1] < curve[i] - MINIMUM_DIFFERENCE and \
                curve[i+1] < curve[i] - MINIMUM_DIFFERENCE:
            peaks += 1
    return peaks


def create_feature_spikyness(selected_data):
    # spikiness = max waarde / avg waarde
    curve = selected_data.AbilityAfterAnswer.values
    if sum(curve) == 0:
        return 0
    spikyness = max(curve) / (sum(curve)/len(curve))
    return spikyness


def normalize(features):
    for column in features.columns[3:]:
        features[column] = preprocessing.scale(features[column])
    return features


def plot_graph(plot_data, save_name=""):
    for xy_data in plot_data:
        if len(xy_data) > 2:
            plt.plot(xy_data[0], xy_data[1], c=xy_data[2])
        elif len(xy_data) == 2:
            plt.plot(xy_data[0], xy_data[1])
        else:
            plt.plot(xy_data[0])
    plt.gca().set_ylim(-1, 101)
    plt.show()
    if save_name != "":
        plt.gcf().save(f'./{save_name}')


def create_plateaus(elo_curve, diff_max=5, min_len=10):
    """
    Create the plateaus found in this graph

    A plateau is a section of the graph with a minimal length, where the
    difference between all values does not exceed a certain value. Each plateau
    will be returned with the x,y coordinates of the start and end of the
    plateau in the form of ([x_start, x_end], [y_start, y_end])

    Plateaus can overlap each other. Plateaus where the x coordinates fall
    within the x coordinates of bigger plateaus will be removed.

    Parameters
    ----------
    elo_curve: list of float
        curve in which the plateaus will be determined
    diff_max: int or float
        max deviation allowed between values in a plateau
    min_len: int
        minimum length of a plateau

    Returns
    -------
    list of tuple of lists of int
        list of plateaus, which are defined as above.

    """
    plateaus = []
    for elo_id, elo_value in enumerate(elo_curve):
        largest_elo_value = elo_value
        smallest_elo_value = elo_value
        for next_elo_id, next_elo_value in enumerate(elo_curve[elo_id:]):
            if (next_elo_value + diff_max < largest_elo_value or  # ELO too low
                    next_elo_value - diff_max > smallest_elo_value):  # or high
                if (next_elo_id > min_len and
                        (len(plateaus) < 1 or
                         plateaus[-1][0][1] < next_elo_id + elo_id - 1)):
                    plateaus.append(([elo_id, next_elo_id + elo_id - 1],
                                     [elo_value,
                                      elo_curve[elo_id + next_elo_id - 1]]))
                break
            if next_elo_value > largest_elo_value:
                largest_elo_value = next_elo_value
            if next_elo_value < smallest_elo_value:
                smallest_elo_value = next_elo_value
    return plateaus


def create_increasing_slopes(elo_curve: list, diff_max = 5, min_len=3) -> list:
    """
    Create the increasing slopes found in this graph

    An increasing slope is a section of the graph with a minimal length,
    where the degree of the angle is the greatest between two points in the
    graph.

    Each slope will be returned with the x,y coordinates of the start and end
    of the slope in the form of ([x_start, x_end], [y_start, y_end])

    Parameters
    ----------
    elo_curve: list of float
        curve in which the plateaus will be determined
    diff_max: int or float
        max deviation allowed between values in a plateau
    min_len: int
        minimum length of a plateau

    Returns
    -------
    list of tuple of lists of int
        list of increasing slopes, which are defined as above.
    """
    if not isinstance(elo_curve, list):
        raise TypeError(f"elo_curve must be a list instance")

    increasing_slopes = []
    ## This method is based on two rules: when the ELO goes down the first
    # time, the next two values must increase.
    for elo_id, elo_value in enumerate(elo_curve):
        if len(elo_curve[elo_id:]) < 3:  # There are no next values
            continue
        if elo_value >= elo_curve[elo_id+1]:
            # Does not start with increase
            continue
        if elo_curve[elo_id+2] <= elo_curve[elo_id+1]:
            # Increase continues not long enough
            continue
        current_elo_value = elo_value
        current_elo_id = elo_id+1
        for next_elo_id, next_elo_value in enumerate(elo_curve[elo_id+1:-4]):
            if next_elo_value <= current_elo_value:  # value not increasing
                # Slope ends if one of the two next values is not increasing
                do_break = False
                if (elo_curve[current_elo_id + 2] <= next_elo_value or
                        elo_curve[current_elo_id + 3] <=
                        elo_curve[current_elo_id + 2]):
                    do_break = True
                # Slope ends if increase is less than previous increase
                # if elo_curve[current_elo_id + 3]-current_elo_value < \
                #         current_elo_value - elo_curve[current_elo_id-1]:
                #     Unless there is at least three times an increase
                if elo_curve[current_elo_id + 4] <= \
                        elo_curve[current_elo_id+3]:
                    # No need to test previous two, already done above.
                    do_break = True

                if do_break is True:
                    if (len(increasing_slopes) == 0 or
                            increasing_slopes[-1][0][1] != current_elo_id) \
                            and next_elo_id > 2:
                        increasing_slopes.append(
                            ([elo_id, current_elo_id],
                             [elo_value, current_elo_value])
                        )
                    break

            current_elo_id = elo_id + next_elo_id + 1
            current_elo_value = next_elo_value
        else:
            tail = elo_curve[-4:]
            highest_tail_id = tail.index(max(tail))
            tail_end_elo_id = len(elo_curve) - 4 + highest_tail_id
            if len(increasing_slopes) == 0 or \
                    (increasing_slopes[-1][0][1] != tail_end_elo_id and
                     tail_end_elo_id - elo_id > 2):
                increasing_slopes.append(
                    ([elo_id, tail_end_elo_id],
                     [elo_value, elo_curve[tail_end_elo_id]]))
    return increasing_slopes


def select_features(features):
    # Try pca method
    pca = PCA()
    pca.fit_transform(features.values[:, 3:])
    print(pca.explained_variance_ratio_)
    print(np.round(abs(pca.components_), 3))

    # Try correlation method
    print(features.columns)
    print(features.values[:, 2:].T)
    correlations = np.cov(features.values[:, 3:].T.astype(float))
    plt.imshow(correlations, cmap="Paired", interpolation="nearest")
    plt.colorbar()

    plt.xticks([c * 1. for c in range(len(features.columns[3:]))],
               features.columns[3:], rotation=90)
    plt.yticks([c * 1. for c in range(len(features.columns[3:]))],
               features.columns[3:])
    plt.show()


def create_decreasing_slopes(elo_curve, diff_max=5, min_len=3):
    """
    Equal to increasing slopes, but looking at the decreasing slopes

    Because the approach is similar except for the direction of the slopes
    the only thing needed to achieve these slopes is by turning the curve
    upside down and consequently turning the resulting slopes back again.

    Parameters
    ----------
    elo_curve
    diff_max
    min_len

    Returns
    -------

    """
    max_elo = max(elo_curve)
    reversed_curve = [max_elo - elo for elo in elo_curve]
    reversed_slopes = create_increasing_slopes(reversed_curve, diff_max,
                                               min_len)
    decreased_slopes = [([slope[0][0], slope[0][1]],
               [max_elo - slope[1][0], max_elo - slope[1][1]])
              for slope in reversed_slopes]
    return decreased_slopes


def create_clusters(data: pd.DataFrame, k=5, method=None,
                    save_dir="./output/clusters/kb.csv", quick_load=True):
    """
    Cluster the curves

    The features of the curves are extracted for all possible curves.
    Afterwards a selected method to cluster the curves is used.

    Parameters
    ----------
    quick_load
    data: Pandas.DataFrame
        The data contained in a Pandas DataFrame.
    k: int or None
        Number of curves to be clustered
    method: str or None
        Method to be used to cluster the curves
    save_dir: str
        relative path to where the clusters are saved in a csv file.

    """
    implemented_methods = ["K-means", "Agglomerate_clustering", "mean_shift"]
    # for i in range(3, 10):
    #     first_curve = data.loc[(data.UserId == data.UserId.unique()[i]) &
    #                            (data.LOID == data.LOID.values[
    #                                0])].AbilityAfterAnswer.values
    #     first_curve = list(first_curve)
    #     plateaus = create_plateaus(first_curve)
    #     small_plateaus = create_plateaus(first_curve, min_len=4)
    #     inc_slopes = create_increasing_slopes(first_curve)
    #     des_slopes = create_decreasing_slopes(first_curve)
    #     plot_graph([(first_curve,),
    #                 *[(p[0], p[1], "r") for p in small_plateaus],
    #                 *[(p[0], p[1], "g") for p in plateaus],
    #                 *[(s[0], s[1], "k") for s in inc_slopes],
    #                 *[(s[0], s[1], "y") for s in des_slopes],
    #                 ])
    features = extract_features(data, quick_load=quick_load)
    # features = normalize(features)
    # select_features(features)

    if method not in implemented_methods:
        raise NotImplementedError(f"The {method} method is not yet "
                                  f"implemented")

    X = features.values[:, 3:]
    print(X[0], "<-")
    features["cluster"] = 0

    if k is not None:  # TODO: Start clustering with selected features?
        if method == "K-means":
            clusters = KMeans(n_clusters=k,
                              random_state=13121992
                              ).fit_predict(features.values[:, 2:])
            print(len(clusters), len(features["cluster"]))
        if method == "mean_shift":
            bandwidth = estimate_bandwidth(X)
            for i in range(1, 3):
                clusters = AffinityPropagation(preference=-5000*i).fit(
                    X).labels_
                # print(clusters+1)
                print(i, sum([1 if c == -1 else 0 for c in clusters]),
                      max(clusters))
        features["cluster"] = clusters+1
    else:
        # calculate distortion for a range of number of cluster
        distortions = []
        for i in range(1, 19):
            km = KMeans(
                n_clusters=i, init='random',
                n_init=10, max_iter=300,
                tol=1e-04, random_state=0
            )
            km.fit(features.values[:, 2:])
            distortions.append(km.inertia_)

        # plot
        plt.plot(range(1, 1+len(distortions)), distortions, marker='o')
        plt.xlabel('Number of clusters')
        plt.ylabel('Distortion')
        plt.show()
    features.to_csv(save_dir)
    return features


def extract_features(data: pd.DataFrame,
                     save_loc="./output/clusters/features/kb_features.csv",
                     quick_load=False) \
        -> pd.DataFrame:
    if os.path.exists(save_loc) and quick_load is True:
        feature_frame = pd.read_csv(save_loc)
        return feature_frame
    feature_frame = create_feature_frame(data)
    features = [
        # "pre_post_gain",
        # "total_gain_elo_score",
        "highest_elo",
        # "relative_position_highest_elo",
        # "difference_highest_elo_and_last",
        # "difference_highest_elo_and_lowest_afterwards",
        # "length_longest_increasing_slope",
        "height_highest_increasing_slope",
        # "length_longest_decreasing_slope",
        "height_highest_decreasing_slope",
        "length_longest_plateau",
        # "number_of_plateaus",
        # "number_of_peaks",
        # "spikyness",
    ]

    # Create extraction functions
    feature_funcs = []
    for feature in features:
        feature_frame[feature] = None
        feature_funcs.append(globals()[f"create_feature_{feature}"])

    # Create data to be used by extraction functions
    for user in tqdm(feature_frame.user.unique(), desc="preparing data"):
        for loid in feature_frame.loid.unique():
            curve = data.loc[(data.UserId == user) &
                             (data.LOID == loid)].AbilityAfterAnswer.values
            curve = list(curve)
            key = (user, loid)
            all_increasing_slopes[key] = create_increasing_slopes(curve)
            all_plateaus[key] = create_plateaus(curve)
            all_decreasing_slopes[key] = create_decreasing_slopes(curve)

    # Extract the features per user and loid.
    for user in tqdm(feature_frame.user.unique(), desc="extracting features"):
        for loid in feature_frame.loid.unique():
            for feature, feature_func in zip(features, feature_funcs):
                selected_data = data.loc[(data.UserId == user) &
                                         (data.LOID == loid)]
                feature_frame.loc[(feature_frame.user == user) &
                                  (feature_frame.loid == loid),
                                  feature] = feature_func(selected_data)
    create_dir_if_not_exists("/".join(save_loc.split("/")[:-1]))
    feature_frame.to_csv(save_loc)
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
    Load the data from an external excel resource.

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
    # load raw data
    loader = DataLoader(f_name=data_loc, s_name="Blad1")
    loaded_data, _ = loader.load(quick_loading=True)

    # Select columns
    if 'phase' in loaded_data.columns:
        loaded_data = loaded_data[['DateTime', 'UserId', 'ExerciseId',
                                   'LOID', 'Correct', 'AbilityAfterAnswer',
                                   'Effort', 'Lesson', 'LessonProgress',
                                   'phase']]
    else:
        loaded_data = loaded_data[['DateTime', 'UserId', 'ExerciseId',
                                   'LOID', 'Correct', 'AbilityAfterAnswer',
                                   'Effort', 'Lesson', 'LessonProgress']]

    # Sort data
    loaded_data = loader.sort_data_by(loaded_data,
                                      ["DateTime", "LessonProgress"])

    # Filter unneeded
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


def plot_clustered_curves(clustered_data, data,
                          save_dir="./output/clusters/curves"):
    create_dir_if_not_exists(save_dir)
    for row, values in tqdm(clustered_data.iterrows(), desc="plotting curves"):
        user = values.user
        loid = values.loid
        cluster = int(values.cluster)
        curve_save_name = f"{cluster}_{int(user)}_{int(loid)}.png"
        curve_data = data.loc[(data.UserId == user) &
                              (data.LOID == loid)].AbilityAfterAnswer.values
        plt.gcf().clear()
        plt.plot(curve_data)
        plt.title(f"Cluster {cluster}")
        plt.gca().set_ylim(-1, 101)
        plt.gcf().savefig(save_dir+"/"+curve_save_name)


if __name__ == "__main__":
    data_location = "./res/data_kb_all_tests_info.xlsx"
    use_data = load_data(data_location)
    # create_clusters(use_data, k=None, method="K-means", quick_load=True)
    for i in range(4, 12):
        clustered = create_clusters(use_data, k=i, method="K_means",
                                    quick_load=True)
        plot_clustered_curves(clustered,
                              use_data,
                              save_dir=f"./output/clusters/{i}curves2")
