import numpy as np
from tqdm import tqdm


class StudyDataProcessor:

    def __init__(self, df, short_file, long_file):
        self.data = df
        self.short_file = short_file
        self.long_file = long_file

    def get_click_changes_week(self, skill, id_):
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
        desc = f"counting all changes in difficulty for skill {skill}"
        scid = f"Total_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            user_data = data.loc[(data.UserId == user) &
                                 (data.LOID == skill)]
            user_data['difficulty_changed'] = user_data.difficulty_level.ne(
                user_data.difficulty_level.shift().bfill()).astype(int)
            value = sum(user_data.difficulty_changed)

            self.short_file.loc[(self.short_file.UserId == user) &
                                (self.short_file.LOID == skill), scid] = value
            self.long_file.loc[self.long_file.UserId == user, lcid] = value

    def get_click_changes_last_two_days(self, skill, id_):
        desc = f"counting changes in difficulty for skill {skill} for the " \
               f"third and fourth day"
        scid = f"day_3_and_4_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            three_four_days = None
            if id_ == "studydata_jm":
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

    def get_click_changes_third_day(self, skill, id_):
        desc = f"counting changes in difficulty for skill {skill} for the " \
               f"third day"
        scid = f"day_3_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            three_days = None
            if id_ == "studydata_jm":
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

    def get_click_changes_fourth_day(self, skill, id_):
        desc = f"counting changes in difficulty for skill {skill} for the " \
               f"fourth day"
        scid = f"day_4_difficulty_changes"
        lcid = f"{scid}_{skill}"
        self.short_file.loc[self.short_file.LOID == skill, scid] = np.nan
        self.long_file[lcid] = np.nan
        data = self.data.copy()
        for user in tqdm(data.UserId.unique(), desc=desc):
            fourth_days = None
            if id_ == "studydata_jm":
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
