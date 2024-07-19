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

from tensorflow.keras.models import load_model
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

startFWX = datetime.now()

# 25282348, 2022 (good)
# 24449412, 2021 (good)
ID = 25282348
year = 2022
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v12"
ml_pack = "tf"
target_vars = "FRP"
plot_method = "mean"
persist = True
dt = 24
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
# ID = fire_cases[0].astype(int)[10]
# year = fire_cases[1].astype(int)[10]


save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]


########################################################################################################
#####################################       RUN MODEL         ##########################################
########################################################################################################
config["ID"] = ID
config["year"] = year
firep = FIREP(config=config)
firep_df = firep.open_firep()
jj = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[jj : jj + 1]

ds = xr.open_dataset(f"/Volumes/ThunderBay/CRodell/fires/{year}-{ID}.nc")

ds_og = ds
ds_attrs = ds.attrs
ds_attrs["pyproj_srs"] = ds["S"].attrs["pyproj_srs"]

curves_ds = salem.open_xr_dataset(str(data_dir) + "/static/curves-rave-3km.nc")
curves_ds["CLIMO_FRP"] = curves_ds["OFFSET_NORM"] * curves_ds["MAX"]
curves_roi = ds.salem.transform(curves_ds, interp="nearest")
fire_time = ds.time.values
hour_one = pd.Timestamp(fire_time[0]).hour
curves_roi = curves_roi.roll(time=-hour_one, roll_coords=True)

# curves_roi['time'] = fire_time[:24]
OFFSET_NORM = curves_roi["OFFSET_NORM"].values
N = len(fire_time)
ds["OFFSET_NORM"] = (
    ("time", "y", "x"),
    np.tile(OFFSET_NORM, (N // 24 + 1, 1, 1))[:N, :, :],
)

CLIMO_FRP = curves_roi["CLIMO_FRP"].values
N = len(fire_time)
ds["CLIMO_FRP"] = (
    ("time", "y", "x"),
    np.tile(CLIMO_FRP, (N // 24 + 1, 1, 1))[:N, :, :],
)


mlD = MLDATA(config=config)
ds = mlD.get_static(ds)
ds = mlD.get_eng_features(ds)

shape = ds["F"].shape
df_dict = {}
for key in config["feature_vars"]:
    try:
        df_dict[key] = np.ravel(ds[key].values)
    except KeyError:
        df_dict[key] = None

df = pd.DataFrame(df_dict)

X = df[config["feature_vars"]]

# Load the scaler
scaler = joblib.load(f"{model_dir}/feature-scaler.joblib")
X_new_scaled = scaler.transform(X)
# X_new_scaled = X.to_numpy()
X_train_df = pd.DataFrame(X_new_scaled, columns=config["feature_vars"])

# Load the model
model = load_model(f"{model_dir}/model.keras")

startFRP = datetime.now()
# print("Start prediction:", startFRP)
y_out_this_nhn = model(X_new_scaled).numpy()
if config["target_scaler_type"] != None:
    print("rescaling target")
    # y_out_this_nhn = target_scaler.inverse_transform(y_out_this_nhn)
    # y_out_this_nhn = y_out_this_nhn * config['FRP_MAX']
    y_out_this_nhn[:, 0] = y_out_this_nhn[:, 0] * config["FRP_MAX"]
if config["transform"] == True:
    print("retransforming target")
    y_out_this_nhn = np.expm1(y_out_this_nhn)

FRP_FULL = y_out_this_nhn.ravel().reshape(shape)
# FRP_FULL = y_out_this_nhn[:, 0].ravel().reshape(shape)
# FRE_FULL = y_out_this_nhn[:, 1].ravel().reshape(shape)
FRPend = datetime.now() - startFRP
print("Time to predict FRP: ", FRPend)
ds["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
# ds["MODELED_FRE"] = (("time", "y", "x"), FRE_FULL)
for var in list(ds):
    if var == "MODELED_FRP":
        ds[var].attrs = {
            "description": "MEAN FIRE RADIATIVE POWER",
            "pyproj_srs": ds_attrs["pyproj_srs"],
            "units": "(MW)",
        }
    else:
        ds[var].attrs = ds_og[var].attrs
ds.attrs = ds_attrs
print("Time to run FWX: ", datetime.now() - startFWX)
# startWRITE = datetime.now()
# ds, encoding = compressor(ds)
# file_dir = f"/Volumes/ThunderBay/CRodell/fires/v9/{year}-{ID}.nc"
# print(f"WRITING AT: {datetime.now()}")
# ds.to_netcdf(file_dir, encoding=encoding, mode="w")
# print(f"Wrote: {file_dir}")
# print("Time to write: ", datetime.now() - startWRITE)

########################################################################################################
###############################      MOD DS/REMOVE NULL         ########################################
########################################################################################################

# %%
def replace_nan_with_previous(arr):
    # Identify the indices of NaN values
    nan_indices = np.isnan(arr)

    # Traverse the array and replace NaNs with the previous non-NaN value
    for i in range(1, len(arr)):
        if nan_indices[i]:
            arr[i] = arr[i - 1]

    return arr


def scale_frp(frp, norm, curve):
    return (frp * curve) / norm


ds_map = ds  # [["FRP", "FRE", "MODELED_FRP", "ZoneST", "OFFSET_NORM", 'R', 'U', 'hour_sin', '']]
# frp_curve = ds_map['hour_sin'].mean(dim=("x", "y")).values[:24]
# ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)
persist = True
utc_offset = int(ds_map["ZoneST"].mean(dim=("x", "y")).values[0])
LOCAL_TIME = ds_map.time.values - pd.Timedelta(hours=utc_offset)
local_hours = pd.to_datetime(LOCAL_TIME).hour
over_pass_viirs = np.where(local_hours == 13)[0]


dt = 12
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

    ds_active_mean = ds_active.mean(("time"), skipna=True)
    ds_active_sum = ds_active.sum(("time"), skipna=True)
    ds_active_sum = xr.where(
        np.isnan(ds_active_mean["FRP"]) == True, np.nan, ds_active_sum
    ).expand_dims("time")
    ds_active_sum["time"] = ("time", [0])
    active_list = [ds_active]
    sum_list = [ds_active_sum]
    nan_time = []
    for i in range(dt, len(ds_map.time), dt):
        ds_active = ds_map.isel(time=slice(i, i + dt))
        nan_array = np.isnan(ds_active["FRP"]).values
        ds_active["MODELED_FRP"] = xr.where(
            nan_space <= 0, np.nan, ds_active["MODELED_FRP"]
        )
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
    ds_map_sum = xr.combine_nested(sum_list, concat_dim="time").sum("time")
    ds_map_sum = ds_map_sum.salem.roi(shape=fire_i, all_touched=True)

else:
    ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)


frp_curve = ds_map["hour_sin"].mean(dim=("x", "y")).values[:24]
# frp_curve = ds_map['OFFSET_NORM'].mean(dim=("x", "y")).values[:24]
ds_space_avg = ds_map.mean(dim=("x", "y"), skipna=True)


FRP = ds_space_avg["FRP"].values
MODELED_FRP = ds_space_avg["MODELED_FRP"].values

utc_offset = ds_space_avg["ZoneST"].values[0]
LOCAL_TIME = ds_space_avg.time.values - pd.Timedelta(hours=utc_offset)
local_hours = pd.to_datetime(LOCAL_TIME).hour
over_pass_viirs = np.where(local_hours == 13)[0]
frp_1300s = FRP[over_pass_viirs]
frp_1300s = replace_nan_with_previous(frp_1300s)
frp_1300s = np.roll(frp_1300s, 1)
frp_1300s[0] = 0


FRP_PRE = np.ravel(
    [
        scale_frp(frp_1300s[i], frp_curve[over_pass_viirs[0]], frp_curve)
        for i in range(len(frp_1300s))
    ]
)[: len(LOCAL_TIME)]

ds_space_avg["FRP_PRE"] = ("time", FRP_PRE)

FRP_PRE = ds_space_avg["FRP_PRE"].values
ds_space_avg = xr.where(
    np.isnan(ds_space_avg["FRP"].values) == True, np.nan, ds_space_avg
)


###############################################################################################
# %%

ds_space_nan = ds_space_avg.dropna("time").isel(time=slice(24, None))
FRP_NAN = ds_space_nan["FRP"].values
MODELED_FRP_NAN = ds_space_nan["MODELED_FRP"].values
FRP_PRE_NAN = ds_space_nan["FRP_PRE"].values

plt.rcParams.update({"font.size": 14})
# fig = plt.figure(figsize=(12, 4))
# ax = fig.add_subplot(1, 1, 1)
fig = plt.figure(figsize=(16, 12))
# Create a gridspec layout
# The first row (for maps) is twice the height of the second row (for line plots)
gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])

ax = fig.add_subplot(gs[0, 0])
ax.scatter(MODELED_FRP, FRP, color="tab:blue", label="MLP", zorder=10, s=20)
ax.scatter(FRP_PRE, FRP, color="tab:red", label="PERS", zorder=5, s=20)
ax.legend(
    ncol=2,
    fancybox=True,
    shadow=True,
    loc="upper right"
    # bbox_to_anchor=(0.38, 1.25),
)
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.grid(
    True, which="both", linestyle="--", linewidth=0.1, color="grey"
)  # Adding grid with thin lines
ax.set_ylabel("Observed FRP (MW)")
ax.set_xlabel("Modeled FRP (MW)")


ax = fig.add_subplot(gs[0, 1])
frp_vals = [FRP_NAN, MODELED_FRP_NAN, FRP_PRE_NAN]
labels = ["OBS", "MLP", "PERS"]
colors = ["k", "tab:blue", "tab:red"]
ax.set_ylabel("FRP (MW)")
bplot = ax.boxplot(
    frp_vals, patch_artist=True, labels=labels  # fill with color
)  # will be used to label x-ticks

# fill with colors
for patch, color in zip(bplot["boxes"], colors):
    patch.set_facecolor(color)


# plt.rcParams.update({"font.size": 14})
# fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(gs[1, :])
ax.plot(LOCAL_TIME, FRP, color="k", lw=1.8, zorder=1, label="OBS")
ax.plot(LOCAL_TIME, MODELED_FRP, color="tab:blue", label="MLP", lw=1.4, zorder=6)
# ax.scatter(LOCAL_TIME, MODELED_FRP, color="tab:blue", label="MLP", s=1, zorder=10)
ax.plot(LOCAL_TIME, FRP_PRE, color="tab:red", label="PERS", lw=1.4, zorder=5)
# ax.scatter(LOCAL_TIME, FRP_PRE, color="tab:red", label="PERS", s=1, zorder=10)
# ax.plot(LOCAL_TIME, (MODELED_FRP+FRP_PRE)/2, color="tab:red", label="ENS", lw=1, zorder=5)

ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
    # bbox_to_anchor=(0.38, 1.25),
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
# plt.gca().set_xticks(hourly_ds.time.values.astype("datetime64[D]"))
# plt.gca().xaxis.set_major_formatter()
ax.set_xlabel(f"Local DateTime (YYYY-MM-DD)", fontsize=18)
ax.set_ylabel(f"FRP (MW)", fontsize=18)


# print("MODELED FRP V OBS FRP")
# ax.set_title(
#     " Modeled vs Observed "
#     + "\n pearsonr: "
#     + str(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))
#     + "\n r2_score: "
#     + str(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
#     + "\n mbe: "
#     + str(np.round(MBE(FRP_NAN, MODELED_FRP_NAN), 2))
#     + "\n rmse: "
#     + str(np.round(RMSE(FRP_NAN, MODELED_FRP_NAN), 2)),
#     loc="left",
#     color="tab:blue",
# )
# print("===============================================")
# print("PERSISTED FRP V OBS FRP")
# ax.set_title(
#     "Persisted vs Observed"
#     + "\n pearsonr: "
#     + str(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))
#     + "\n r2_score: "
#     + str(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
#     + "\n mbe: "
#     + str(np.round(MBE(FRP_NAN, FRP_PRE_NAN), 2))
#     + "\n rmse: "
#     + str(np.round(RMSE(FRP_NAN, FRP_PRE_NAN), 2)),
#     loc="right",
#     color="tab:red",
# )


# %%
