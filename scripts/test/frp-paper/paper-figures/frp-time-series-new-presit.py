#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import os
import context
import salem
import dask
import joblib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime


from utils.ml_data import MLDATA
from utils.firep import FIREP
from utils.plot_fire_case import plot_fire, drop_outside_std
from utils.solar_hour import get_solar_hours
from utils.compressor import compressor
import matplotlib.dates as mdates

from scipy import stats
from utils.stats import MBE, RMSE, MAE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter


from context import root_dir, data_dir


# 25282348 (2022) "Calf Canyon/Hermits Peak Fire" https://go.nasa.gov/4bQXoME
# 24564081 (2021) "Fire ID 24564081 / Northern California"
# 26691009 (2023) "Fire ID 26691009 / Coastal British Columbia"
# 26567967 (2023) "Fire ID 26567967 / Northwest Territories, Canada"
ID = 25282348
year = 20222
fig_title = "Calf Canyon/Hermits Peak Fire"
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
plot_method = "mean"
persist = True
dt = 12
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]
config["ID"] = ID
config["year"] = year
firep = FIREP(config=config)
firep_df = firep.open_firep()
jj = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[jj : jj + 1]


ds_map = xr.open_dataset(
    f"/Volumes/ThunderBay/CRodell/fires/{method[-3:]}/{year}-{ID}.nc"
)[["FRP", "FRE", "MODELED_FRP"]]

if persist == True:
    ds_active = ds_map.isel(time=slice(0, dt))
    nan_array = np.isnan(ds_active["FRP"]).values
    zero_full = np.zeros(nan_array.shape)
    zero_full[nan_array == False] = 1
    nan_space = np.sum(np.stack(zero_full), axis=0)
    # nan_space = np.stack(zero_full)
    ds_active["MODELED_FRP"] = xr.where(
        nan_space <= 0, np.nan, ds_active["MODELED_FRP"]
    )

    # desired_shape = ds_active["FRP"].shape
    # FRP_MEAN_PRES = ds_active["FRP"].mean(dim ='time').values
    # ds_active['FRP_MEAN_PRES'] = (('time', 'y', 'x'), np.tile(FRP_MEAN_PRES, (desired_shape[0], 1, 1)))

    ds_active_mean = ds_active.mean("time", skipna=True)
    ds_active_sum = ds_active.sum(("time"), skipna=True)
    ds_active_sum = xr.where(
        np.isnan(ds_active_mean["FRP"]) == True, np.nan, ds_active_sum
    ).expand_dims("time")
    ds_active_sum["time"] = ("time", [0])
    active_list = [ds_active]
    sum_list = [ds_active_sum]
    nan_time = []
    for i in range(dt, len(ds_map.time), dt):
        # FRP_MEAN_PRES = ds_active["FRP"].mean(dim ='time').values
        ds_active = ds_map.isel(time=slice(i, i + dt))
        nan_array = np.isnan(ds_active["FRP"]).values
        ds_active["MODELED_FRP"] = xr.where(
            nan_space <= 0, np.nan, ds_active["MODELED_FRP"]
        )
        # desired_shape = ds_active["FRP"].shape
        # ds_active['FRP_MEAN_PRES'] = (('time', 'y', 'x'), np.tile(FRP_MEAN_PRES, (desired_shape[0], 1, 1)))

        zero_full = np.zeros(nan_array.shape)
        zero_full[nan_array == False] = 1
        nan_space = np.sum(np.stack(zero_full), axis=0)
        # nan_space = np.stack(zero_full)

        ds_active_mean = ds_active.mean(("time"), skipna=True)
        ds_active_sum = ds_active.sum(("time"), skipna=True)
        ds_active_sum = xr.where(
            np.isnan(ds_active_mean["FRP"]) == True, np.nan, ds_active_sum
        )
        ds_active_sum["time"] = ("time", [i])

        active_list.append(ds_active)
        sum_list.append(ds_active_sum)
    ds_map = xr.combine_nested(active_list, concat_dim="time")
    ds_time_sum = xr.combine_nested(sum_list, concat_dim="time").sum("time")
    ds_time_sum = ds_time_sum.salem.roi(shape=fire_i, all_touched=True)

else:
    ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)


ds_space_avg = ds_map.mean(dim=("x", "y"), skipna=True)
ds_space_sum = ds_map.sum(dim=("x", "y"), skipna=True)


###############################################################################################
# %%

# utc_offset = int(ds_map["ZoneST"].mean(dim=("x", "y")).values[0])
utc_offset = int(7)
LOCAL_TIME = ds_map.time.values - pd.Timedelta(hours=utc_offset)

FRP = ds_space_avg["FRP"].values
MODELED_FRP = ds_space_avg["MODELED_FRP"].values

# pres_days = []
# FRP_PRE = ds_space_avg['FRP'].roll(time =24).interpolate_na(dim ='time').to_dataset()
# for i in range(0, len(FRP_PRE.time), 24):
#     FRP_PRE_DAY = FRP_PRE.isel(time = slice(i, i+24))
#     desired_shape = FRP_PRE_DAY['FRP'].shape
#     FRP_MEAN_PRES = FRP_PRE_DAY['FRP'].mean(dim ='time').values
#     FRP_PRE_DAY['FRP_MEAN_PRES'] = (('time'), np.tile(FRP_MEAN_PRES, (desired_shape[0])))
#     pres_days.append(FRP_PRE_DAY)

FRP_PRE = ds_space_avg["FRP"].roll(time=24).interpolate_na(dim="time").values
FRP_PRE[np.isnan(FRP) == True] = np.nan
ds_space_avg["FRP_PRE"] = (("time"), FRP_PRE)
FRP_PRE = ds_space_avg["FRP_PRE"].values


ds_space_avg_nan = ds_space_avg.isel(time=slice(24, -1)).dropna("time")
FRP_NAN = ds_space_avg_nan["FRP"]
MODELED_FRP_NAN = ds_space_avg_nan["MODELED_FRP"]
FRP_PRE_NAN = ds_space_avg_nan["FRP_PRE"]

# %%
plt.rcParams.update({"font.size": 14})
fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])


ax = fig.add_subplot(gs[0, 0])
ax.scatter(MODELED_FRP, FRP, color="tab:blue", label="MLP", zorder=10, s=20)
ax.scatter(FRP_PRE, FRP, color="tab:red", label="PERS", zorder=5, s=20)
ax.legend(ncol=2, fancybox=True, shadow=True, loc="upper right")
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
ax.set_ylabel("Observed FRP (MW)")
ax.set_xlabel("Modeled FRP (MW)")
ax.set_title(
    "MLP vs OBS \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
    + " MAE: "
    + str(np.round(MAE(FRP_NAN, MODELED_FRP_NAN), 2))
    + " (MW) RMSE: "
    + str(np.round(float(RMSE(FRP_NAN, MODELED_FRP_NAN)), 2))
    + " (MW)",
    loc="left",
    color="tab:blue",
    fontsize=14,
)
# Get the current limits from the AxesSubplot object
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()

# Find the larger range
range_max = max(x_max - x_min, y_max - y_min)

# Set the new limits to ensure both axes have the same range
ax.set_xlim(x_min, x_min + range_max)
ax.set_ylim(y_min, y_min + range_max)


ax = fig.add_subplot(gs[0, 1])
frp_vals = [FRP_NAN, MODELED_FRP_NAN, FRP_PRE_NAN]
labels = ["OBS", "MLP", "PERS"]
colors = ["k", "tab:blue", "tab:red"]
ax.set_ylabel("FRP (MW)")
bplot = ax.boxplot(frp_vals, patch_artist=True, labels=labels)

for patch, color in zip(bplot["boxes"], colors):
    patch.set_facecolor(color)
ax.set_title(
    "PRES. vs OBS \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
    + " MAE: "
    + str(np.round(MAE(FRP_NAN, FRP_PRE_NAN), 2))
    + " (MW) RMSE: "
    + str(np.round(float(RMSE(FRP_NAN, FRP_PRE_NAN)), 2))
    + " (MW)",
    loc="right",
    color="tab:red",
    fontsize=14,
)
ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.1, color="grey")

ax = fig.add_subplot(gs[1, :])
MODELED_FRP[np.isnan(FRP) == True] = np.nan
FRP_PRE[np.isnan(FRP) == True] = np.nan
ax.plot(LOCAL_TIME, FRP, color="k", lw=2.5, zorder=1, label="OBS")
ax.plot(LOCAL_TIME, MODELED_FRP, color="tab:blue", label="MLP", lw=2, zorder=6)
ax.plot(LOCAL_TIME, FRP_PRE, color="tab:red", label="PERS", lw=2, zorder=5)
ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.set_xlabel(f"Local DateTime (YYYY-MM-DD)", fontsize=18)
ax.set_ylabel(f"FRP (MW)", fontsize=18)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")

fig.suptitle(fig_title, fontsize=22)

# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/fireID-{ID}-year-{year}-frp-time-series.png",
    bbox_inches="tight",
    dpi=240,
)

# %%


# %%

###############################################################################################


ds_space_sum["MODELED_FRE"] = ds_space_sum["MODELED_FRP"] * 3600
ds_time_sum["MODELED_FRE"] = ds_time_sum["MODELED_FRP"] * 3600

FRE = ds_space_sum["FRE"].values
MODELED_FRE = ds_space_sum["MODELED_FRE"].values
FRE_PRE = ds_space_sum["FRE"].roll(time=24).interpolate_na(dim="time").values
FRE[np.isnan(FRP) == True] = np.nan
MODELED_FRE[np.isnan(FRP) == True] = np.nan
FRE_PRE[np.isnan(FRP) == True] = np.nan
ds_space_sum["FRE_PRE"] = (("time"), FRE_PRE)

# ds_space_sum_nan = ds_space_sum.dropna('time').isel(time =slice(24,-1))
# FRE_NAN = ds_space_avg_nan['FRE'].values
# MODELED_FRP_NAN = ds_space_avg_nan['MODELED_FRP'].values
# FRP_PRE_NAN = ds_space_avg_nan['FRP_PRE'].values


ds_space_sum = xr.where(
    np.isnan(ds_space_avg["FRP"].values) == True, np.nan, ds_space_sum
)
ds_space_nan = ds_space_sum.isel(time=slice(24, -1)).dropna("time")
FRE_NAN = ds_space_nan["FRE"].values
MODELED_FRE_NAN = ds_space_nan["MODELED_FRE"].values
FRE_PRE_NAN = ds_space_nan["FRE_PRE"].values
###############################################################################################


# %%

# Custom formatter function
def scientific_formatter(x, pos):
    return f"{x/1e7:.1f}e7"


fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])

ax = fig.add_subplot(gs[0, 0])
ax.scatter(MODELED_FRE, FRE, color="tab:blue", label="MLP", zorder=10, s=20)
ax.scatter(FRE_PRE, FRE, color="tab:red", label="PERS", zorder=5, s=20)
ax.legend(ncol=2, fancybox=True, shadow=True, loc="upper right")
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
ax.set_ylabel("Observed FRE (MJ)")
ax.set_xlabel("Modeled FRE (MJ)")
ax.set_title(
    "MLP vs OBS \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRE_NAN, MODELED_FRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRE_NAN, MODELED_FRE_NAN), 2))
    + " MAE: "
    + "{:.1e}".format(np.round(MAE(FRE_NAN, MODELED_FRE_NAN), 2))
    + " (MJ) RMSE: "
    + "{:.1e}".format(np.round(RMSE(FRE_NAN, MODELED_FRE_NAN), 2))
    + " (MJ)",
    loc="left",
    color="tab:blue",
    fontsize=14,
)
# Get the current limits from the AxesSubplot object
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()

# Find the larger range
range_max = max(x_max - x_min, y_max - y_min)

# Set the new limits to ensure both axes have the same range
ax.set_xlim(x_min, x_min + range_max)
ax.set_ylim(y_min, y_min + range_max)

# Setting the formatter for x and y axes
# ax.xaxis.set_major_formatter(FuncFormatter(scientific_formatter))
# ax.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
ax = fig.add_subplot(gs[0, 1])
fre_vals = [FRE_NAN, MODELED_FRE_NAN, FRE_PRE_NAN]
labels = ["OBS", "MLP", "PERS"]
colors = ["k", "tab:blue", "tab:red"]
ax.set_ylabel("FRE (MJ)")
ax.grid(True, which="both", axis="y", linestyle="--", linewidth=0.1, color="grey")
bplot = ax.boxplot(fre_vals, patch_artist=True, labels=labels)

for patch, color in zip(bplot["boxes"], colors):
    patch.set_facecolor(color)
ax.set_title(
    "PRES. vs OBS \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRE_NAN, FRE_PRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRE_NAN, FRE_PRE_NAN), 2))
    + " MAE: "
    + "{:.1e}".format(np.round(MAE(FRE_NAN, FRE_PRE_NAN), 2))
    + " (MW) RMSE: "
    + "{:.1e}".format(np.round(RMSE(FRE_NAN, FRE_PRE_NAN), 2))
    + " (MW)",
    loc="right",
    color="tab:red",
    fontsize=14,
)
# Setting the formatter for x and y axes
# ax.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))

ax = fig.add_subplot(gs[1, :])
# MODELED_FRE[np.isnan(FRP)==True] =np.nan
# FRE_PRE[np.isnan(FRP)==True] =np.nan
ax.plot(LOCAL_TIME, FRE, color="k", lw=2.5, zorder=1, label="OBS")
ax.plot(LOCAL_TIME, MODELED_FRE, color="tab:blue", label="MLP", lw=2, zorder=6)
ax.plot(LOCAL_TIME, FRE_PRE, color="tab:red", label="PERS", lw=2, zorder=5)
ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
)

# Setting the formatter for x and y axes
# ax.xaxis.set_major_formatter(FuncFormatter(scientific_formatter))
# ax.yaxis.set_major_formatter(FuncFormatter(scientific_formatter))

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.set_xlabel(f"Local DateTime (YYYY-MM-DD)", fontsize=18)
ax.set_ylabel(f"FRE (MJ)", fontsize=18)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
fig.suptitle(fig_title, fontsize=22)


# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/fireID-{ID}-year-{year}-fre-time-series.png",
    bbox_inches="tight",
    dpi=240,
)

# %%

# fig = plt.figure(figsize=(16, 12))
# # Create a gridspec layout
# # The first row (for maps) is twice the height of the second row (for line plots)
# gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1])
# g = salem.GoogleVisibleMap(
#     x=[fire_i.min_x, fire_i.max_x],
#     y=[fire_i.min_y, fire_i.max_y],
#     scale=2,  # scale is for more details
#     maptype="satellite",
#     size_x=40,
#     size_y=40,
# )  # try out also: 'terrain'


# model_title = "MODELED FIRE RADIATIVE ENERGY (MJ)"
# obs_title = "OBSERVED FIRE RADIATIVE ENERGY (MJ)"
# vmax = 4e8

# vmax = np.nanpercentile(ds_time_sum["MODELED_FRE"].values,99)
# # np.nanpercentile(ds_time_sum["FRE"].values,95)

# for var in list(ds_map):
#     ds_time_sum[var].attrs = ds.attrs
# ds_time_sum.attrs = ds.attrs

# # First map on the top left
# ax = fig.add_subplot(gs[0, 0])
# ax.set_title(model_title)
# sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmin=0, vmax= vmax)
# sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
# sm.set_data(ds_time_sum["MODELED_FRE"], overplot=True)
# sm.set_scale_bar(
#     location=(0.88, 0.94),
# )
# sm.visualize(ax=ax)
# plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# # Second map on the top right
# ax = fig.add_subplot(gs[0, 1])
# ax.set_title(obs_title)
# sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmin=0, vmax= vmax)
# sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
# sm.set_data(ds_time_sum["FRE"], overplot=True)
# sm.set_scale_bar(location=(0.88, 0.94))
# sm.visualize(ax=ax)
# ax.set_yticklabels([])
# plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


# %%
