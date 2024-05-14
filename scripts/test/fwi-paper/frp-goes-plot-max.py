#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import gc

import numpy as np
import xarray as xr
import pandas as pd
from scipy import stats
from pathlib import Path

import matplotlib.colors
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import plotly.express as px


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
# plt.rcParams.update({'font.size': 16})

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################
## define model domain and path to fwf data
save_fig = False
norms = False
int_plot = True
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
#
print(case_study)
case_info = case_dict[case_study]
domain = case_info["domain"]
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

(frp_ds, frp_da, frp_da_og, frp_lats, frp_lons, utc_offset, start, stop) = open_frp(
    case_study, case_info, max_comp=True
)


fwf_range = pd.date_range(
    start.astype("datetime64[D]") - pd.Timedelta(days=1),
    stop.astype("datetime64[D]") + pd.Timedelta(days=1),
)
yy, xx = build_tree(case_study, case_info, frp_lats, frp_lons)


hourly_ds = xr.combine_nested(
    [open_fwf(doi, filein, domain, "hourly", yy, xx, utc_offset) for doi in fwf_range],
    "time",
).sel(
    time=slice(start, stop)
)  # .compute()
fwf_range = pd.date_range(
    start.astype("datetime64[D]") - pd.Timedelta(days=2),
    stop.astype("datetime64[D]") + pd.Timedelta(days=2),
)
daily_ds = xr.combine_nested(
    [open_fwf(doi, filein, domain, "daily", yy, xx, utc_offset) for doi in fwf_range],
    "time",
)  # .compute()
daily_ds["time"] = daily_ds["Time"]
# daily_ds = daily_ds.resample(time="1H").nearest()
# daily_ds["time"] = daily_ds["time"] - np.timedelta64(int(12), "h")
daily_ds = daily_ds.sel(
    time=slice(start.astype("datetime64[D]"), stop.astype("datetime64[D]"))
)
# daily_ds = daily_ds.sel(time=slice(start, stop))


if norms == True:
    norm_d = xr.open_dataset(str(data_dir) + f"/norm/fwi-daily-{domain}.nc")
    norm_h = xr.open_dataset(str(data_dir) + f"/norm/fwi-hourly-{domain}.nc")
    hourly_ds = normalize(hourly_ds, yy, xx, norm_h).rename("S").to_dataset()
    daily_ds = normalize(daily_ds, yy, xx, norm_d).rename("S").to_dataset()


# %%
# start = date_range[0]
# stop = date_range[-1]
# start = "2021-07-24-T00"
# stop = "2021-07-29T00"
# start = date_range[non_nan_indices[result[1][0]]]
# stop = date_range[non_nan_indices[result[0][0]]+(24*10)]


max_frp = frp_da.resample(time="1D").max()
max_fwi = hourly_ds.resample(time="1D").max()["S"]
daily_fwi = daily_ds["S"]
max_fwi = daily_ds["mS"]


# Create a date range with hourly frequency, starting at 8:00 AM, and ending at 8:00 AM the next day
# date_range = pd.date_range(start=start.astype('datetime64[D]'), end=stop.astype('datetime64[D]'), freq='D', normalize=True) + pd.to_timedelta('16H')

# max_fwi = hourly_ds.sel(time = date_range)['S']
# daily_fwi = daily_ds.sel(time = date_range)['S']
# max_frp = frp_da.sel(time = date_range)


study_range = hourly_ds.time.values
unique, counts = np.unique(np.isnan(max_frp), return_counts=True)
print(
    f"Precent of values that where observed {round((counts[0]/len(max_frp.time))*100,2)}"
)
hfwip = max_fwi.values[np.isnan(max_frp) == False]
dfwip = daily_fwi.values[np.isnan(max_frp) == False]
hfrpp = max_frp.values[np.isnan(max_frp) == False]


pearsonr_h_interp_final = stats.pearsonr(hfwip, hfrpp)
pearsonr_d_interp_final = stats.pearsonr(dfwip, hfrpp)


# %%
################################ Plot FRP vs FWI ################################
year = pd.to_datetime(max_fwi.time.values[-1]).strftime("%Y")


fig = plt.figure(figsize=(12, 4))
fig.suptitle(f"    Fire Weather Index vs Fire Radiative Power", fontsize=20, y=1.11)

ax = fig.add_subplot(1, 1, 1)
title_line1 = (
    r"\fontsize{18pt}{22pt}\selectfont " + f"{case_study.replace('_', ' ').title()}"
)
title_line2 = r"\fontsize{12pt}{15pt}\selectfont " + f"{case_info['loc']}" + f", {year}"
title = f"{title_line1}\n{title_line2}"
ax.set_title(title, loc="center", fontdict={"usetex": True})

ax.set_title(
    f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI    \n  Values observed: {round((counts[0]/len(max_frp.time))*100,2)}%",
    loc="right",
    fontsize=12,
)
ax2 = ax.twinx()
ax.plot(max_fwi.time, max_fwi, color="tab:blue", label="Hourly")
ax.plot(daily_fwi.time, daily_fwi, color="tab:blue", ls="--", label="Daily")

ax.plot(max_fwi.time, max_fwi, color="tab:red", lw=1, label="FRP", zorder=0)
set_axis_postion(ax, "FWI", color="tab:blue")

ax2.plot(max_frp.time, max_frp, color="tab:red", label="FRP", zorder=10)
# ax2.plot(frp_da.time, hfrp, lw=1.1, color="tab:red", ls="dotted", label="FRP")

set_axis_postion(ax2, "FRP (MW)", color="tab:red")
tkw = dict(size=4, width=1.5, labelsize=16)
ax.tick_params(
    axis="x",
    **tkw,
)


plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
ax.set_xlabel(f"Local DateTime (MM-DD)", fontsize=16)
ax.legend(
    # loc="upper right",
    bbox_to_anchor=(0.35, 1.18),
    ncol=4,
    fancybox=True,
    shadow=True,
    fontsize=12,
)
fig.autofmt_xdate()


if save_fig == True:
    if paper == True:
        plt.savefig(str(save_dir) + f"/{case_study}-max.pdf", bbox_inches="tight")
        plt.savefig(
            str(save_dir) + f"/{case_study}-max.png", dpi=250, bbox_inches="tight"
        )
    else:
        plt.savefig(
            str(save_dir) + f"/{case_study}-max.png", dpi=250, bbox_inches="tight"
        )

# %%
