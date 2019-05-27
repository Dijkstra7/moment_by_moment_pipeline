"""
Making the log outputs from the Leerpaden app readable.
"""

import pandas as pd
from tqdm import tqdm


def color(color_id):
    if color_id == 110:
        return "green"
    if color_id == 111:
        return "green with a hoop"
    if color_id == 112:
        return "green with a ball"
    if color_id == 120:
        return "orange"
    if color_id == 121:
        return "orange with a hoop"
    if color_id == 122:
        return "orange with a ball"
    if color_id == 130:
        return "grey"
    if color_id == 140:
        return "white"
    return f"UNKNOWN - ({color_id})"


def path_(path_id):
    if path_id == 1:
        return "first"
    if path_id == 2:
        return "repeat"
    if path_id == 3:
        return "end"
    return "UNKNOWN"


def run(f_name="./res/logdata.csv", user=None):
    log_data = pd.read_csv(f_name, usecols=[2, 3, 4, 5, 6, 7])
    # print(log_data.head())  # Inspections
    if user is not None:
        log_data = log_data.loc[log_data.user_id == user]
    log_list = []
    log_text = "UNKNOWN LOG"
    # for screen in log_data.screen.unique():
    #     for action in log_data.loc[log_data.screen == screen].action.unique():
    #         print(f"{screen} {action}")
    print(user)
    for label, content in tqdm(log_data.iterrows()):
        if content.screen == 1 and content.action == 4:
            log_text = "Log in"
        if content.screen == 2:
            if content.action == 0:
                log_text = "Log out"
            if content.action == 1:
                log_text = f"Click dolphin for goal {content.object_id} " \
                           f"being {color(content.info)}."
        if content.screen == 3:
            if content.action == 0:
                log_text = "Close goalsetter screen"
            if content.action == 2:
                log_text = f"Click {path_(content.object_id)} path showing " \
                           f"detail page with path type {content.info}"
            if content.action == 3:
                log_text = f"Setting goal for the {path_(content.object_id)}" \
                           f" path at {content.info}"
        if content.screen == 4:
            if content.action == 0:
                "Close detail screen"
        log_list.append([content.user_id, content.date_time, log_text])
    log_text = pd.DataFrame(log_list, columns=["user", "date_time", "logtext"])
    # print(log_text.tail(20))

    for s in log_list:
        if int(s[1][11:13]) < 10:
            print(s)


if __name__ == "__main__":
    for user in range(3010, 3120):
        run(user=user)
