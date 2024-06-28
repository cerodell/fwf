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


ID = 24448308  #  25485086 (2022) 24448308 (2021) 24360611 (2021) 24450415 (2021)
year = "2021"
mlp_test_case = "MLP_64U-Dense_64U-Dense_64U-Dense_64U-Dense_2U-Dense-Decent"
version = "v7"
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

df_curve = pd.read_csv(str(data_dir) + "/frp/FRP_diurnal_climatology.csv")
df_curve.columns = [
    "Land Cover",
    "Ecoregion",
    "hh00",
    "hh01",
    "hh02",
    "hh03",
    "hh04",
    "hh05",
    "hh06",
    "hh07",
    "hh08",
    "hh09",
    "hh10",
    "hh11",
    "hh12",
    "hh13",
    "hh14",
    "hh15",
    "hh16",
    "hh17",
    "hh18",
    "hh19",
    "hh20",
    "hh21",
    "hh22",
    "hh23",
]
df_curve = (
    df_curve.drop(0)
    .drop(columns=["Land Cover", "Ecoregion"])
    .dropna()
    .reset_index(drop=True)
    .astype(float)
)
df_curve = df_curve.mean()

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
# ds_space_avg = ds_map.sel(time = slice('2021-07-08','2021-07-20')).mean(dim=("x", "y"))
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
# [scale_frp(FRP[i], frp_curve[i], frp_curve) for i in over_pass_viirs]

# duplicated_array = np.tile(frp_curve, len(LOCAL_TIME) // len(frp_curve) + 1)[:len(LOCAL_TIME)]


# ds_time_avg = ds_map.mean(dim=("time"))

# FRP_NORM = ds_space_avg['FRP'] / ds_space_avg['FRP'].dropna("time").values.max()
# MODELED_FRP_NORM = ds_space_avg['MODELED_FRP'] /  ds_space_avg['FRP'].dropna("time").values.max()

# FRP_NORM = ds_space_avg['FRP'] / ds_space_avg['FRP'].dropna("time").values.max()
# MODELED_FRP_NORM = ds_space_avg['MODELED_FRP'] /  ds_space_avg['FRP'].dropna("time").values.max()

fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1)
ax.scatter(FRP_PRE, FRP)
ax.scatter(MODELED_FRP, FRP)


fig = plt.figure(figsize=(14, 6))
ax = fig.add_subplot(1, 1, 1)
ax.plot(LOCAL_TIME, FRP, color="k", lw=1.2, zorder=1, label="OBS")
ax.plot(LOCAL_TIME, MODELED_FRP, color="tab:green", label="MLP")
ax.plot(LOCAL_TIME, FRP_PRE, color="tab:orange", label="CLIMO")
ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
    # bbox_to_anchor=(0.38, 1.25),
)
ds_space_nan = ds_space_avg.dropna("time").isel(time=slice(24, None))
FRP_NAN = ds_space_nan["FRP"].values
MODELED_FRP_NAN = ds_space_nan["MODELED_FRP"].values
FRP_PRE_NAN = ds_space_nan["FRP_PRE"].values

print("MODELED FRP V OBS FRP")
print(
    "pearsonr: "
    + str(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))
    + "\n r2_score: "
    + str(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
    + "\n mbe: "
    + str(np.round(MBE(FRP_NAN, MODELED_FRP_NAN), 2))
    + "\n rmse: "
    + str(np.round(RMSE(FRP_NAN, MODELED_FRP_NAN), 2))
)
print("===============================================")
print("PERSISTED FRP V OBS FRP")
print(
    "pearsonr: "
    + str(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))
    + "\n r2_score: "
    + str(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
    + "\n mbe: "
    + str(np.round(MBE(FRP_NAN, FRP_PRE_NAN), 2))
    + "\n rmse: "
    + str(np.round(RMSE(FRP_NAN, FRP_PRE_NAN), 2))
)


# ds_time_avg = ds_time_avg.salem.roi(shape=fire_i, all_touched=True)


# %%
