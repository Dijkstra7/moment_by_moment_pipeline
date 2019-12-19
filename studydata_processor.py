import math
import pandas as pd
import numpy as np
from tqdm import tqdm

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 775


def to_single_problems(df: pd.DataFrame):
    att_data = pd.DataFrame(columns=df.columns)
    for student in tqdm(df.UserId.unique(), desc="Create single problems"):
        student_data = df.loc[df.UserId == student]
        student_data.drop_duplicate(subset=["exerciseId"])
        pd.concat([att_data, student_data], ignore_index=True, sort=True)
    return att_data


class StudyDataProcessor:
    def __init__(self, df, short_file, long_file):
        self.data = df.copy()
        self.att = df.copy().drop_duplicates(subset=['UserId',
                                                     'ExerciseId',
                                                     'LOID'])
        self.short_file = short_file
        self.long_file = long_file
        self.scaffold_dict = None

    def get_click_changes_week(self, skill, id_, data_type="attempts"):
        """
        Calculate the changes in difficulty level per user and skill

        Return the number of times that the difficulty level is being changed

        Parameters
        ----------
        skill: learning objective ID used
        id_: id_ for processing differences per experiment

        Returns
        -------
        None
        """
        desc = f"counting all changes in difficulty for skill {skill} for " \
               f"all {data_type}"
        scid = f"{data_type}_Total_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy() if data_type == "attempts" else self.att.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            user_data = data.loc[(data.UserId == user) &
                                 (data.LOID == skill)]
            user_data['difficulty_changed'] = user_data.difficulty_level.ne(
                user_data.difficulty_level.shift().bfill()).astype(int)
            value = sum(user_data.difficulty_changed)

            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_click_changes_last_two_days(self, skill, id_,
                                        data_type="attempts"):
        desc = f"counting changes in difficulty for skill {skill} for the " \
               f"third and fourth day for all {data_type}"
        scid = f"{data_type}_day_3_and_4_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy() if data_type == "attempts" else self.att.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            three_four_days = None
            if id_ == "clickdata_jm":
                three_four_days = [13, 14, 20, 21]
            if three_four_days is None:
                raise NotImplementedError
            user_data = data.loc[(data.UserId == user) &
                                 (data.LOID == skill)]
            user_data['difficulty_changed'] = user_data.difficulty_level.ne(
                user_data.difficulty_level.shift().bfill()).astype(int)
            value = sum(user_data.difficulty_changed.loc[
                            user_data.SubmitDate.dt.day.isin(three_four_days)])

            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_click_changes_third_day(self, skill, id_,
                                        data_type="attempts"):
        desc = f"counting changes in difficulty for skill {skill} for the " \
               f"third day for all {data_type}"
        scid = f"{data_type}_day_3_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy() if data_type == "attempts" else self.att.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            three_days = None
            if id_ == "clickdata_jm":
                three_days = [13, 20]
            if three_days is None:
                raise NotImplementedError
            user_data = data.loc[(data.UserId == user) &
                                 (data.LOID == skill)]
            user_data['difficulty_changed'] = user_data.difficulty_level.ne(
                user_data.difficulty_level.shift().bfill()).astype(int)
            value = sum(user_data.difficulty_changed.loc[
                            user_data.SubmitDate.dt.day.isin(three_days)])

            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_click_changes_fourth_day(self, skill, id_,
                                        data_type="attempts"):
        desc = f"counting changes in difficulty for skill {skill} for the " \
               f"fourth day for all {data_type}"
        scid = f"{data_type}_day_4_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy() if data_type == "attempts" else self.att.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            fourth_days = None
            if id_ == "clickdata_jm":
                fourth_days = [14, 21]
            if fourth_days is None:
                raise NotImplementedError
            user_data = data.loc[(data.UserId == user) &
                                 (data.LOID == skill)]
            user_data['difficulty_changed'] = user_data.difficulty_level.ne(
                user_data.difficulty_level.shift().bfill()).astype(int)
            value = sum(user_data.difficulty_changed.loc[
                            user_data.SubmitDate.dt.day.isin(fourth_days)])

            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_difficulty_details(self, skill, id_, day=None, difficulty="easy",
                               info_type="selection", data_type="attempts"):
        if day is None:
            day_string = "all_week"
        else:
            day_string = f"day_{day}"
        if info_type == "selection":
            info_string = "selected"
        else:
            info_string = "sums_made"
        desc = f"counting amount of difficulty {info_type} for skill {skill}" \
               f" for {day_string} and difficulty {difficulty} for all " \
               f"{data_type}"
        scid = f"{data_type}_{day_string}_{difficulty}_difficulty_{info_string}"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy() if data_type == "attempts" else self.att.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            use_days = None
            if id_ == "clickdata_jm":
                if day is not None:
                    use_days = [10 + day, 17 + day]
                else:
                    use_days = [11, 12, 13, 14, 15, 18, 19, 20, 21, 22]
            if use_days is None:
                raise NotImplementedError
            user_data = data.loc[(data.UserId == user) &
                                 (data.LOID == skill) &
                                 (~data.phase.isin(["pre", "post"]))]
            user_data['difficulty_changed'] = user_data.difficulty_level.ne(
                user_data.difficulty_level.shift().bfill()).astype(int)
            selection = user_data.difficulty_changed.loc[
                (user_data.SubmitDate.dt.day.isin(use_days)) &
                (user_data.difficulty_level ==
                 self.get_difficulty_level_value(difficulty))]
            if info_type == "selection":
                value = sum(selection)
            else:
                value = len(selection)
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    @staticmethod
    def get_difficulty_level_value(difficulty):
        if str.lower(difficulty) == "easy":
            return 0.65
        if str.lower(difficulty) == "hard":
            return 0.85
        return 0.75

    def create_scaffold_data(self, skill, id_):
        if id_ not in ["clickdata_jm"]:
            raise NotImplementedError
        if self.scaffold_dict is None:
            self.scaffold_dict = {}
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc="Getting scaffold data"):
            select_data = data.loc[
                (data.UserId == user) &
                (data.LOID == skill)]
            select_data['difficulty_changed'] = select_data.difficulty_level. \
                ne(select_data.difficulty_level.shift().bfill()).astype(int)
            select_data['aaa_difference'] = select_data.AAA.diff(). \
                bfill().shift()
            select_data['scaffold_indication'] = self.get_scaffold_value(
                select_data.aaa_difference)

            self.scaffold_dict[(user, skill)] = select_data[[
                "difficulty_changed",
                "scaffold_indication",
                "difficulty_level"
            ]]

    @staticmethod
    def get_scaffold_value(aaa_difference_series):
        scaffold_values = []
        for index, difference in enumerate(aaa_difference_series):
            x_difference = .9 * math.floor(SCREEN_WIDTH / float(index+1))
            y_difference = (difference/600.)*(SCREEN_HEIGHT-200)
            rotation = math.degrees(math.atan2(y_difference, x_difference))
            if rotation < -10:
                scaffold_values.append(0.65)
            elif rotation > 10:
                scaffold_values.append(0.85)
            else:
                scaffold_values.append(0.75)
        return scaffold_values

    def get_adjusted_like_scaffold(self, skill, difference_type, id_):
        desc = f"counting {difference_type} amount of difficulty adjustments" \
               f" according to the scaffold"
        scid = f"adjusted_like_scaffold_{difference_type}_amount"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            select_data = self.scaffold_dict[(user, skill)]
            correct_changes_amount = len(
                select_data.loc[(select_data.difficulty_changed == 1)
                                & (select_data.difficulty_level ==
                                   select_data.scaffold_indication)])
            total_changes_amount = sum(select_data.difficulty_changed)
            value = correct_changes_amount \
                if difference_type == "absolute" \
                else (np.nan
                      if total_changes_amount == 0
                      else (float(correct_changes_amount)
                            / sum(select_data.difficulty_changed)))
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_adjusted_harder_than_scaffold(self, skill, difference_type, id_):
        desc = f"counting {difference_type} amount of difficulty adjustments" \
               f" harder than according to the scaffold"
        scid = f"adjusted_harder_than_scaffold_{difference_type}_amount"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            select_data = self.scaffold_dict[(user, skill)]
            correct_changes_amount = len(
                select_data.loc[(select_data.difficulty_changed == 1)
                                & (select_data.difficulty_level >
                                   select_data.scaffold_indication)])
            total_changes_amount = sum(select_data.difficulty_changed)
            value = correct_changes_amount \
                if difference_type == "absolute" \
                else (np.nan
                      if total_changes_amount == 0
                      else (float(correct_changes_amount)
                            / sum(select_data.difficulty_changed)))
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_adjusted_easier_than_scaffold(self, skill, difference_type, id_):
        desc = f"counting {difference_type} amount of difficulty adjustments" \
               f" easier than according to the scaffold"
        scid = f"adjusted_easier_than_scaffold_{difference_type}_amount"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            select_data = self.scaffold_dict[(user, skill)]
            correct_changes_amount = len(
                select_data.loc[(select_data.difficulty_changed == 1)
                                & (select_data.difficulty_level
                                   < select_data.scaffold_indication)])
            total_changes_amount = sum(select_data.difficulty_changed)
            value = correct_changes_amount \
                if difference_type == "absolute" \
                else (np.nan
                      if total_changes_amount == 0
                      else (float(correct_changes_amount)
                            / sum(select_data.difficulty_changed)))
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_sums_made_adjusted_easier_than_scaffold(
            self, skill, difference_type, id_):
        desc = f"counting {difference_type} amount of sums made" \
               f" easier than according to the scaffold"
        scid = f"sums_made_easier_than_scaffold_{difference_type}_amount"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            select_data = self.scaffold_dict[(user, skill)]
            correct_changes_amount = len(
                select_data.loc[(select_data.difficulty_level
                                 < select_data.scaffold_indication)])
            value = correct_changes_amount if difference_type == "absolute" \
                else (float(correct_changes_amount) / len(select_data))
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_sums_made_adjusted_like_scaffold(
            self, skill, difference_type, id_):
        desc = f"counting {difference_type} amount of sums made" \
               f" according to the scaffold"
        scid = f"sums_made_with_correct_scaffold_{difference_type}_amount"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            select_data = self.scaffold_dict[(user, skill)]
            correct_changes_amount = len(
                select_data.loc[(select_data.difficulty_level
                                 == select_data.scaffold_indication)])
            value = correct_changes_amount if difference_type == "absolute" \
                else (float(correct_changes_amount) / len(select_data))
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_sums_made_adjusted_harder_than_scaffold(
            self, skill, difference_type, id_):
        desc = f"counting {difference_type} amount of sums made" \
               f" harder than according to the scaffold"
        scid = f"sums_made_harder_than_scaffold_{difference_type}_amount"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            select_data = self.scaffold_dict[(user, skill)]
            correct_changes_amount = len(
                select_data.loc[(select_data.difficulty_level
                                 > select_data.scaffold_indication)])
            value = correct_changes_amount if difference_type == "absolute" \
                else (float(correct_changes_amount) / len(select_data))
            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value
