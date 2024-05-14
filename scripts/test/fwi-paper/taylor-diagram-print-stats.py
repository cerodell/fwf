import context

import numpy as np
import pandas as pd
from pathlib import Path


import skill_metrics as sm
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from context import data_dir

model = "wrf"
trail_name = "04"

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/{model}/taylor/")
save_dir.mkdir(parents=True, exist_ok=True)

# var_list = [
#     "ffmc",
#     "dmc",
#     "dc",
#     "bui",
#     "isi",
#     "fwi",
#     "temp",
#     "td",
#     "rh",
#     "ws",
#     "wdir",
#     "rh",
# ]
var_list = [
    "temp",
    "rh",
    "ws",
    "precip",
]
# var_list = ["fwi"]
for var in var_list:
    print(f"+++++++===========  {var} =============++++++++")
    day1_df = pd.read_csv(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/{var}-stats.csv"
    )
    day1_df["domain"] = day1_df["domain"].str.strip()
    stdev_obs = float(day1_df[day1_df["domain"] == "obs"]["std_dev"].iloc[0])

    # day2_df = pd.read_csv(
    #     str(data_dir) + f"/intercomp/{trail_name}/{model}_day2/{var}-stats.csv"
    # )
    # day2_df["domain"] = day2_df["domain"].str.strip()
    # stdev_obs2 = float(day2_df[day2_df["domain"] == "obs"]["std_dev"].iloc[0])
    # if stdev_obs != stdev_obs2:
    #     raise ValueError("We have an issue! The day1 and day2 std dont match")

    def get_mbe(df, domain):
        mbe = round(float(df[df["domain"] == domain]["mbe"].iloc[0]), 2)
        if mbe < 0:
            mbe = "{:.2f}".format(mbe)
        else:
            mbe = " " + "{:.2f}".format(mbe)
        return mbe

    def print_stats(df, domain):
        dfi = df[df["domain"] == domain]
        print(f"-----------  {domain} -------------")
        print("r:         ", round(float(dfi["r"].iloc[0]), 2))
        # print("RMS:       ", round(float(dfi["rms"].iloc[0]), 2))
        print("mbe:       ", get_mbe(df, domain))
        print("RMSD:      ", round(float(dfi["rmse"].iloc[0]), 2))
        print("STD DIFF:  ", round(float(dfi["std_dev"].iloc[0] - stdev_obs), 2))

        return

    print_stats(day1_df, "d03-daily")
    print_stats(day1_df, "d02-daily")

    # print_stats(day1_df, "d03-h1200")
    # print_stats(day1_df, "d02-h1200")

    # print_stats(day1_df, "d03-h1600")
    # print_stats(day1_df, "d02-h1600")

    # print_stats(day1_df, "d03-max")
    # print_stats(day1_df, "d02-max")
