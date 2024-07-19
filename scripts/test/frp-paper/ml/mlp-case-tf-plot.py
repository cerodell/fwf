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

from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from context import root_dir, data_dir

import warnings

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)

import numpy as np


ID = 26418461  #  25485086 (2022) 24448308 (2021) 24360611 (2021) 24450415 (2021) 26418461 (2023)
year = "2023"
mlp_test_case = "MLP_64U-Dense_64U-Dense_64U-Dense_2U-Dense"
version = "v11"
method = f"averaged-{version}"
ml_pack = "tf"
target_vars = "FRP_FRE"


# model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
# with open(f"{model_dir}/config.json", "r") as json_data:
#     config = json.load(json_data)['user_config']

# config["year"] = year
firep = FIREP(config={"year": year})
firep_df = firep.open_firep()
jj = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[jj : jj + 1]


# %%
ds = xr.open_dataset(f"/Volumes/ThunderBay/CRodell/fires/{version}/{year}-{ID}.nc")


def replace_nan_with_previous(arr):
    # Identify the indices of NaN values
    nan_indices = np.isnan(arr)

    # Traverse the array and replace NaNs with the previous non-NaN value
    for i in range(1, len(arr)):
        if nan_indices[i]:
            arr[i] = arr[i - 1]

    return arr


# ds_map = ds[["FRP","FRE", "MODELED_FRP", "MODELED_FRE", 'ZoneST']]
ds_map = ds[["FRP", "MODELED_FRP", "ZoneST"]]
ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)
ds_map = ds_map.salem.roi(shape=fire_i, all_touched=True)

# ds_space_avg = ds_map.isel(time = slice(72,128)).mean(dim=("x", "y"))
test = ds_map.sel(time=slice("2023-06-03-T00", "2023-06-06-T23"))
test["FRP"].isel(time=slice(0, 72, 4)).plot(
    x="x", y="y", col="time", col_wrap=3, cmap="YlOrRd"
)
quant_ds = test["FRP"].quantile(
    [0, 0.25, 0.5, 0.75, 0.90, 0.95, 1],
    dim=("x", "y"),
    skipna=True,
)  # .dropna("time")

fig = plt.figure(figsize=(8, 4))
ax = fig.add_subplot(1, 1, 1)
ax.plot(quant_ds["time"], quant_ds.isel(quantile=0), label="0")
ax.plot(quant_ds["time"], quant_ds.isel(quantile=1), label="25")
ax.plot(quant_ds["time"], quant_ds.isel(quantile=2), label="50")
ax.plot(quant_ds["time"], quant_ds.isel(quantile=3), label="75")
ax.plot(quant_ds["time"], quant_ds.isel(quantile=4), label="90")
ax.plot(quant_ds["time"], quant_ds.isel(quantile=5), label="95")
ax.plot(quant_ds["time"], quant_ds.isel(quantile=6), label="100")
ax.legend()

fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(1, 1, 1)
test.mean(dim=("x", "y"))["FRP"].plot(ax=ax, color="tab:orange")
fig.savefig(
    str(data_dir) + f"/images/frp-paper/{ID}-time-series-frp-only.png",
    bbox_inches="tight",
    dpi=240,
)


ds_space_avg = ds_map.mean(dim=("x", "y"))
FRP = ds_space_avg["FRP"].values
MODELED_FRP = ds_space_avg["MODELED_FRP"].values

utc_offset = ds_space_avg["ZoneST"].values[0]
LOCAL_TIME = ds_space_avg.time.values - pd.Timedelta(hours=utc_offset)
local_hours = pd.to_datetime(LOCAL_TIME).hour
over_pass_viirs = np.where(local_hours == 13)[0]
frp_1300s = FRP[over_pass_viirs]  # [FRP[idx] for idx in over_pass_viirs]
frp_1300s = replace_nan_with_previous(frp_1300s)
frp_1300s = np.roll(frp_1300s, 1)
frp_1300s[0] = 0
bias = MODELED_FRP[over_pass_viirs[1]] - frp_1300s[1]
# MODELED_FRP = MODELED_FRP - bias


# start_hour = pd.Timestamp(LOCAL_TIME[0]).hour
frp_curve = df_curve.values
frp_curve = np.roll(frp_curve, int(utc_offset))


def scale_frp(frp, norm, curve):
    return (frp * curve) / norm


FRP_PRE = np.ravel(
    [
        scale_frp(frp_1300s[i], frp_curve[over_pass_viirs[0]], frp_curve)
        for i in range(len(frp_1300s))
    ]
)[: len(LOCAL_TIME)]

ds_space_avg["FRP_PRE"] = ("time", FRP_PRE)
ds_space_avg = xr.where(
    np.isnan(ds_space_avg["FRP"].values) == True, np.nan, ds_space_avg
)
FRP_PRE = ds_space_avg["FRP_PRE"].values


# ds_slice = ds_space_avg.sel(time=slice('2021-07-13', '2021-08-05'))
# FRP = ds_slice["FRP"].values
# MODELED_FRP = ds_slice["MODELED_FRP"].values
# FRP_PRE = ds_slice["FRP_PRE"].values
# LOCAL_TIME = ds_slice.time.values - pd.Timedelta(hours=utc_offset)

# [scale_frp(FRP[i], frp_curve[i], frp_curve) for i in over_pass_viirs]

# duplicated_array = np.tile(frp_curve, len(LOCAL_TIME) // len(frp_curve) + 1)[:len(LOCAL_TIME)]


# ds_time_avg = ds_map.mean(dim=("time"))

# FRP_NORM = ds_space_avg['FRP'] / ds_space_avg['FRP'].dropna("time").values.max()
# MODELED_FRP_NORM = ds_space_avg['MODELED_FRP'] /  ds_space_avg['FRP'].dropna("time").values.max()

# FRP_NORM = ds_space_avg['FRP'] / ds_space_avg['FRP'].dropna("time").values.max()
# MODELED_FRP_NORM = ds_space_avg['MODELED_FRP'] /  ds_space_avg['FRP'].dropna("time").values.max()

# fig = plt.figure(figsize=(6, 6))
# ax = fig.add_subplot(1, 1, 1)
# ax.scatter(FRP_PRE, FRP)
# ax.scatter(MODELED_FRP, FRP)
# ax.set_xlim(-10,3000)
# ax.set_ylim(-10,3000)


# ds_slice = ds_space_avg.sel(time=slice('2021-07-01', '2021-08-01'))
# FRP = ds_slice["FRP"].values
# MODELED_FRP = ds_slice["MODELED_FRP"].values
# FRP_PRE = ds_slice["FRP_PRE"].values
# LOCAL_TIME = ds_slice.time.values - pd.Timedelta(hours=utc_offset)

# %%
plt.rcParams.update({"font.size": 14})
fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(1, 1, 1)
ax.plot(LOCAL_TIME, FRP, color="k", lw=1.4, zorder=1, label="OBS")
ax.plot(LOCAL_TIME, MODELED_FRP, color="tab:green", label="MLP", lw=1, zorder=10)
ax.plot(LOCAL_TIME, FRP_PRE, color="tab:orange", label="CLIMO", lw=1, zorder=5)
ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
    # bbox_to_anchor=(0.38, 1.25),
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
# plt.gca().set_xticks(hourly_ds.time.values.astype("datetime64[D]"))
# plt.gca().xaxis.set_major_formatter()
ax.set_xlabel(f"Local DateTime (MM-DD)", fontsize=18)
ax.set_ylabel(f"FRP (MW)", fontsize=18)

ds_space_nan = ds_space_avg.dropna("time").isel(time=slice(24, None))
FRP_NAN = ds_space_nan["FRP"].values
MODELED_FRP_NAN = ds_space_nan["MODELED_FRP"].values
FRP_PRE_NAN = ds_space_nan["FRP_PRE"].values

print("MODELED FRP V OBS FRP")
ax.set_title(
    "Modeled vs Observed "
    + "\n pearsonr: "
    + str(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))
    # + "\n r2_score: "
    # + str(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
    + "\n mbe: "
    + str(np.round(MBE(FRP_NAN, MODELED_FRP_NAN), 2))
    + "\n rmse: "
    + str(np.round(RMSE(FRP_NAN, MODELED_FRP_NAN), 2)),
    loc="left",
    color="tab:green",
)
print("===============================================")
print("PERSISTED FRP V OBS FRP")
ax.set_title(
    "Persisted vs Observed"
    + "\n pearsonr: "
    + str(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))
    # + "\n r2_score: "
    # + str(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
    + "\n mbe: "
    + str(np.round(MBE(FRP_NAN, FRP_PRE_NAN), 2))
    + "\n rmse: "
    + str(np.round(RMSE(FRP_NAN, FRP_PRE_NAN), 2)),
    loc="right",
    color="tab:orange",
)
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/{ID}-time-series.png",
#     bbox_inches="tight",
#     dpi=240,
# )

# ds_time_avg = ds_time_avg.salem.roi(shape=fire_i, all_touched=True)


# %%
