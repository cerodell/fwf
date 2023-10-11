#!/Users/crodell/miniconda3/envs/fwf/bin/python

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
save_fig = True
case_study = "oak_fire"
# print(case_study)
save_dir = Path(str(data_dir) + f"/images/frp/goes/noaa/")
save_dir.mkdir(parents=True, exist_ok=True)
################## END INPUTS ####################

test = xr.open_dataset(
    "/Volumes/WFRT-Ext22/frp/goes/g18/2023/OR_ABI-L2-FDCF-M6_G18_s20232190020203_e20232190029511_c20232190030022.nc"
)
#################### OPEN FILES ####################


## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)
#
# for case_study in list(case_dict)[3:]:
case_info = case_dict[case_study]
domain = case_info["domain"]
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

(
    frp_ds,
    frp_da,
    frp_da_og,
    frp_lats,
    frp_lons,
    utc_offset,
    date_range,
    fwf_range,
) = open_frp(case_study, case_info)
norm_d = xr.open_dataset(str(data_dir) + f"/norm/fwi-daily-{domain}.nc")
norm_h = xr.open_dataset(str(data_dir) + f"/norm/fwi-hourly-{domain}.nc")


Mask = frp_ds["Mask"].values
Power = frp_ds["Power"].values

# Power =  xr.where((frp_ds['Mask'] == 10) | (frp_ds['Mask'] == 30), frp_ds['Power'], np.nan)
Mask_test = Mask[~np.isnan(Power)]
flag_values = np.array(test["Mask"].attrs["flag_values"])
flag_meanings = np.array(test["Mask"].attrs["flag_meanings"].split())
flag_meanings[flag_values == 10]

fwf_range_daily = pd.date_range(
    fwf_range[0] - pd.Timedelta(days=2), fwf_range[-1] + pd.Timedelta(days=2)
)
print(case_study)
yy, xx = build_tree(case_study, case_info, frp_lats, frp_lons)
try:
    hourly_ds = xr.open_dataset(
        str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc"
    )
    daily_ds = xr.open_dataset(
        str(data_dir) + f"/frp/analysis/wrf/{case_study}-daily.nc"
    )
except:
    print("Making FWI netcdf")
    try:
        # hourly_ds = xr.combine_nested([open_fwf(doi, filein, domain, "hourly", yy, xx, utc_offset) for doi in fwf_range], "time")
        daily_ds = xr.combine_nested(
            [
                open_fwf(doi, filein, domain, "daily", yy, xx, utc_offset)
                for doi in fwf_range_daily
            ],
            "time",
        )
    except:
        # hourly_ds = xr.combine_nested([open_fwf(doi, filein, domain, "hourly", yy, xx, utc_offset) for doi in fwf_range[:-1]], "time")
        daily_ds = xr.combine_nested(
            [
                open_fwf(doi, filein, domain, "daily", yy, xx, utc_offset)
                for doi in fwf_range_daily[:-1]
            ],
            "time",
        )
    daily_ds["time"] = daily_ds["Time"]
    daily_ds = daily_ds.resample(time="1H").nearest()
    # hourly_ds.to_netcdf(str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc", mode = 'w')
    daily_ds.to_netcdf(
        str(data_dir) + f"/frp/analysis/wrf/{case_study}-daily.nc", mode="w"
    )
    # hourly_ds = normalize(hourly_ds, yy, xx, norm_h).rename('S').to_dataset()
    # daily_ds = normalize(daily_ds, yy, xx, norm_d).rename('S').to_dataset()
hourly_ds = xr.open_dataset(str(data_dir) + f"/frp/analysis/wrf/{case_study}-hourly.nc")


# %%

non_nan_indices = np.where(~np.isnan(frp_da))[0]
diff_arr = np.diff(non_nan_indices)
indices = np.where(diff_arr == 1)[0]
groups = np.split(indices, np.where(np.diff(indices) != 1)[0] + 1)
result = [group for group in groups if len(group) > 12]

if (case_study == "ewf_031-") or (case_study == "quebec_fire_334-"):
    start = date_range[non_nan_indices[result[1][0]]]
    stop = date_range[non_nan_indices[result[1][0]] + (24 * 4)]
elif (case_study == "marshall_fire") or (case_study == "eagle_bluff_fire-"):
    start = date_range[non_nan_indices[result[0][0]]]
    start = date_range[non_nan_indices[0]]
    stop = date_range[non_nan_indices[-1]]
else:
    start = date_range[non_nan_indices[result[0][0]]]
    stop = date_range[non_nan_indices[result[0][0]] + (24 * 7)]


# %%
# start = date_range[non_nan_indices[0]]
# stop = date_range[non_nan_indices[-1]]
# stop = "2021-09-16-T00"
# stop = "2021-09-29-T00"
frp_ds = frp_ds.sel(t=slice(start, stop))

frp_da_slice = frp_da.sel(t=slice(start, stop))
frp_raw = frp_da_slice.values
frp_da_slice_int = frp_da_slice.interpolate_na(dim="t", method="linear").ffill(
    dim="t"
)  # pchip or linear
frp_da_og_slice = frp_da_og.sel(t=slice(start, stop))
hourly_ds_slice = hourly_ds.sel(time=slice(start, stop))
daily_ds_slice = daily_ds.sel(
    time=slice(hourly_ds_slice["time"][0], hourly_ds_slice["time"][-1])
)

hfwi = hourly_ds_slice["S"].values
hfrp = frp_da_slice_int.values
dfwi = daily_ds_slice["S"].values
study_range = hourly_ds_slice.time.values
unique, counts = np.unique(np.isnan(frp_raw), return_counts=True)
print(f"Precent of values that where observed {round((counts[0]/len(hfrp))*100,2)}")

hfrpp = hfrp[np.isnan(frp_da_slice.values) == False]

# hfwi[np.isnan(hfrp)] = np.nan
# dfwi[np.isnan(hfrp)] = np.nan


# pearsonr_h_interp_final = stats.pearsonr(hfwip, hfrpp)
# pearsonr_d_interp_final = stats.pearsonr(dfwip, hfrpp)
# ################################ Plot Interp NEW FRP vs FWI ################################
start = pd.to_datetime(study_range[0]).strftime("%B %d")
stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
year = pd.to_datetime(study_range[-1]).strftime("%Y")

# %%

fig = plt.figure(figsize=(16, 4))
# fig.suptitle(f"    Fire Radiative Power", fontsize=20, y=1.11)
gs = GridSpec(1, 2, width_ratios=[2, 4])  # Adjust width ratios as needed
ax = plt.subplot(gs[0, 1])

title_line1 = (
    r"\fontsize{18pt}{22pt}\selectfont " + f"{case_study.replace('_', ' ').title()}"
)
title_line2 = r"\fontsize{12pt}{15pt}\selectfont " + f"{case_info['loc']}"
title = f"{title_line1}\n{title_line2}"
fig.suptitle(title, fontdict={"usetex": True}, y=1.1)

ax.set_title(
    "Fire Radiative Power Timeseries",
    loc="left",
    fontdict={"usetex": True},
    fontsize=14,
)


from matplotlib import cm
import matplotlib.image as mpimg

ax.plot(frp_da_slice.time, frp_da_slice, color="k", lw=2, label="FRP 1hour")
# ax.plot(frp_da_slice.time, hfrp, lw=1.1, color="tab:red", ls="dotted", label="FRP ")
ax.scatter(
    frp_da_og_slice.t,
    frp_da_og_slice,
    c=mdates.date2num(pd.to_datetime(frp_da_og_slice.t.values)),
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
ax.set_xlabel("Local DateTime (MM-DD-HH)", fontsize=16)
ax.legend(
    # loc="upper right",
    bbox_to_anchor=(1.0, 1.18),
    ncol=3,
    fancybox=True,
    shadow=True,
    fontsize=12,
)
fig.autofmt_xdate()
ax.annotate(
    "B)", xy=(-0.05, 1.1), xycoords="axes fraction", fontsize=20, fontweight="bold"
)


frp_date_range = frp_ds["t"].values
keep_dates = np.where((frp_date_range <= pd.to_datetime("2020-01-01")) == False)
frp_ds = frp_ds.isel(t=keep_dates[0])
frp_ds = frp_ds.sortby("t")
df = frp_ds.to_dataframe().reset_index()
df = df[df["Power"].notna()]
df = df.set_index(pd.DatetimeIndex(df["t"]))

import matplotlib.image as mpimg

# Filter rows based on the target datetime
# df_sample = df[df.index.date == doi.date()]
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
cbar.ax.tick_params(labelsize=14)

cbar.ax.yaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
ax.set_title(f"Fire Hot Spots", fontsize=14, fontdict={"usetex": True})
cbar.set_label("Datetime", rotation=270, fontsize=14, labelpad=20)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)

tkw = dict(size=4, width=1.5, labelsize=12)
ax.annotate(
    "A)", xy=(-0.05, 1.1), xycoords="axes fraction", fontsize=20, fontweight="bold"
)

ax.tick_params(
    **tkw,
)

ax.set_xlim(min(df_sample["lons"]) - 0.05, max(df_sample["lons"]) + 0.05)
ax.set_ylim(min(df_sample["lats"]) - 0.05, max(df_sample["lats"]) + 0.05)

if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/{case_study}-resample.png",
        dpi=250,
        bbox_inches="tight",
    )


# %%
