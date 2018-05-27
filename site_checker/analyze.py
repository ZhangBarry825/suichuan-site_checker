# encoding=utf8
# author=spenly
# mail=i@spenly.com

import pandas as pd
from models import engine, FailedLinks, ColumnsUpdates

def read_data(file_name):
    df = pd.read_csv(file_name)
    grp = df.groupby(["url"])
    ndf = grp.apply(fill_data)
    faileds = get_faileds(ndf)
    updates = get_updates(ndf)
    if updates is not None:
        if len(updates.columns) > 0:
            updates = updates.loc[:, ["purl", "ptitle", "sdate"]]
        updates.to_csv(file_name + ".updates", index=False)
    if faileds is not None:
        faileds.to_csv(file_name + ".faileds", index=False)


def get_faileds(df):
    return df[df["status_code"] != 200]


def get_updates(df):
    df = df.fillna("#")
    df = df[df["sdate"] != '#']
    df.loc[:, "sdate"] = pd.to_datetime(df["sdate"])
    grp = df.groupby(["purl"])
    udf = grp.apply(lambda x: x[x["sdate"] == x["sdate"].max()][0:1])
    return udf


def fill_data(df):
    visited_data = df[df["status_code"] != 0]
    status_code = int(visited_data["status_code"])
    error = visited_data["error"]
    sdate = visited_data["sdate"]
    df.loc[:, "status_code"] = status_code
    df.loc[:, "error"] = error
    df.loc[:, "sdate"] = sdate
    return df


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        file_name = sys.argv[1]
        read_data(file_name)
    else:
        print("invalid args")
