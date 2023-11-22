#!/Users/crodell/miniconda3/envs/fwx/bin/python

"""
Script generates the frp 10 in to 1 hourly resampled figures used in the ams hourly fwi paper
"""
import context
import json
import salem

import numpy as np
import xarray as xr
import pandas as pd
from scipy import stats
from pathlib import Path
from matplotlib.gridspec import GridSpec

from sklearn.neighbors import KDTree

import matplotlib.colors
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import cm
import matplotlib.image as mpimg

from utils.frp import (
    open_fwf,
    open_frp,
    set_axis_postion,
    build_tree,
    get_time_offest,
    normalize,
)
from context import data_dir, root_dir

plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)
plt.rcParams.update({"font.size": 18})

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = False
paper = False
case_study = "caldor_fire"  # ['sparks_lake', 'lytton_creek', 'barrington_lake_fire', 'ewf_031', 'quebec_fire_334', 'donnie_creek', 'wildcat', 'marshall_fire', 'oak_fire', 'caldor_fire', 'fire_east_tulare', 'rossmoore_fire', 'crater_creek', 'mcdougall_creek']
# print(case_study)

if paper == True:
    save_dir = Path("/Users/crodell/ams-fwf/LaTeX/img/fwf/")
    save_dir.mkdir(parents=True, exist_ok=True)
else:
    save_dir = Path(str(data_dir) + f"/images/frp/goes/paper/")
    save_dir.mkdir(parents=True, exist_ok=True)

################## END INPUTS ####################


#################### OPEN FILES ####################
## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

# for case_study in list(case_dict):
for case_study in ["caldor_fire"]:
    print(case_study)
    case_info = case_dict[case_study]
    domain = case_info["domain"]
    filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

    (frp_ds, frp_da, frp_da_og, frp_lats, frp_lons, utc_offset, start, stop) = open_frp(
        case_study, case_info
    )

    ############################## Plot FRP Map and Timeseries ################################
    # %%

    fig = plt.figure(figsize=(16, 4))
    gs = GridSpec(1, 2, width_ratios=[2, 4])  # Adjust width ratios as needed
    ax = plt.subplot(gs[0, 1])

    title_line1 = (
        r"\fontsize{24pt}{22pt}\selectfont " + f"{case_study.replace('_', ' ').title()}"
    )
    title_line2 = r"\fontsize{18pt}{15pt}\selectfont " + f"{case_info['loc']}"
    title = f"{title_line1}\n{title_line2}"
    fig.suptitle(title, fontdict={"usetex": True}, y=1.15)

    ax.set_title(
        "Fire Radiative Power Timeseries",
        loc="left",
        fontdict={"usetex": True},
        fontsize=18,
    )

    ax.plot(frp_da.time, frp_da, color="k", lw=2, label="FRP 1hour")
    ax.scatter(
        frp_ds.time,
        frp_ds["Power"].mean(dim=("x", "y")),
        c=mdates.date2num(pd.to_datetime(frp_ds.time.values)),
        label="FRP 10min",
    )

    set_axis_postion(ax, "FRP (MW)")
    tkw = dict(size=4, width=1.5, labelsize=16)
    ax.tick_params(
        axis="x",
        **tkw,
    )
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
    # plt.gca().xaxis.set_major_formatter()
    ax.set_xlabel("Local DateTime (MM-DD-HH)", fontsize=18)
    ax.legend(
        # loc="upper right",
        bbox_to_anchor=(1.0, 1.2),
        ncol=3,
        fancybox=True,
        shadow=True,
        fontsize=16,
    )
    fig.autofmt_xdate()
    ax.annotate(
        "B)", xy=(-0.05, 1.1), xycoords="axes fraction", fontsize=20, fontweight="bold"
    )

    frp_date_range = frp_ds["time"].values
    keep_dates = np.where((frp_date_range <= pd.to_datetime("2020-01-01")) == False)
    frp_ds = frp_ds.isel(time=keep_dates[0])
    frp_ds = frp_ds.sortby("time")
    df = frp_ds.to_dataframe().reset_index()
    df = df[df["Power"].notna()]
    df = df.set_index(pd.DatetimeIndex(df["time"]))

    df_sample = df

    ax = plt.subplot(gs[0, 0])
    sc = ax.scatter(
        df_sample["lons"],
        df_sample["lats"],
        zorder=9,
        c=mdates.date2num(df_sample.index.values),
        # alpha =0.5
    )

    cbar = plt.colorbar(sc, ax=ax, pad=0.008, alpha=1)
    loc = mdates.AutoDateLocator()
    cbar.ax.yaxis.set_major_locator(loc)
    cbar.ax.tick_params(labelsize=16)

    cbar.ax.yaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
    ax.set_title(f"Fire Hot Spots", fontsize=18, fontdict={"usetex": True}, loc="left")
    cbar.set_label("Datetime", rotation=270, fontsize=16, labelpad=20)
    ax.set_xlabel("Longitude", fontsize=16)
    ax.set_ylabel("Latitude", fontsize=16)

    tkw = dict(size=4, width=1.5, labelsize=16)
    ax.annotate(
        "A)", xy=(-0.1, 1.1), xycoords="axes fraction", fontsize=20, fontweight="bold"
    )
    ax.tick_params(
        **tkw,
    )
    ax.set_xlim(min(df_sample["lons"]) - 0.05, max(df_sample["lons"]) + 0.05)
    ax.set_ylim(min(df_sample["lats"]) - 0.05, max(df_sample["lats"]) + 0.05)

    if save_fig == True:
        if paper == True:
            plt.savefig(
                str(save_dir) + f"/{case_study}-resample.pdf", bbox_inches="tight"
            )
            plt.savefig(
                str(save_dir) + f"/{case_study}-resample.png",
                dpi=250,
                bbox_inches="tight",
            )
        else:
            plt.savefig(
                str(save_dir) + f"/{case_study}-resample.png",
                dpi=250,
                bbox_inches="tight",
            )
# %%
