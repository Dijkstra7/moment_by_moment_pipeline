import pandas as pd


def load(f_name=f"./res/LogdataH.csv"):
    return pd.read_csv(f_name, index_col=0, header=0, names=["index", "DateTime", "UserId", "Screen", "Action",
                                                             "ObjectId", "Info"], parse_dates=[1])


if __name__ == "__main__":
    data = load()
    pass