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

# 25282348,   https://go.nasa.gov/4bQXoME  2022 (good)
# 24701624
ID = 25282348
year = 2022
fig_title = "Calf Canyon/Hermits Peak Fire"
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v14"
ml_pack = "tf"
target_vars = "FRP"
plot_method = "mean"
persist = True
dt = 12
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")

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


try:
    ds = xr.open_dataset(
        f"/Volumes/ThunderBay/CRodell/fires/{method[-3:]}/{year}-{ID}.nc"
    )
except:
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
        y_out_this_nhn = y_out_this_nhn * config["FRP_MAX"]
        # y_out_this_nhn[:, 0] = y_out_this_nhn[:, 0] * config["FRP_MAX"]
    if config["transform"] == True:
        print("retransforming target")
        y_out_this_nhn = np.expm1(y_out_this_nhn)

    FRP_FULL = y_out_this_nhn.ravel().reshape(shape)
    FRPend = datetime.now() - startFRP
    print("Time to predict FRP: ", FRPend)
    ds["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
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
    startWRITE = datetime.now()
    ds, encoding = compressor(ds)
    file_dir = f"/Volumes/ThunderBay/CRodell/fires/{method[-3:]}/{year}-{ID}.nc"
    print(f"WRITING AT: {datetime.now()}")
    ds.to_netcdf(file_dir, encoding=encoding, mode="w")
    print(f"Wrote: {file_dir}")
    print("Time to write: ", datetime.now() - startWRITE)

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


presist_hour = 13
ds_map = ds  # [["FRP", "FRE", "MODELED_FRP", "ZoneST", "OFFSET_NORM", 'R', 'U', 'hour_sin', '']]
# frp_curve = ds_map['hour_sin'].mean(dim=("x", "y")).values[:24]
# ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)
utc_offset = int(ds_map["ZoneST"].mean(dim=("x", "y")).values[0])
LOCAL_TIME = ds_map.time.values - pd.Timedelta(hours=utc_offset)
local_hours = pd.to_datetime(LOCAL_TIME).hour
over_pass_viirs = np.where(local_hours == presist_hour)[0]


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
    ds_time_sum = xr.combine_nested(sum_list, concat_dim="time").sum("time")
    ds_time_sum = ds_time_sum.salem.roi(shape=fire_i, all_touched=True)

else:
    ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)


frp_curve = ds_map["hour_sin"].mean(dim=("x", "y")).values[:24]
# frp_curve = ds_map['OFFSET_NORM'].mean(dim=("x", "y")).values[:24]
ds_space_avg = ds_map.mean(dim=("x", "y"), skipna=True)
ds_space_sum = ds_map.sum(dim=("x", "y"), skipna=True)


###############################################################################################


# %%

###############################################################################################

FRP = ds_space_avg["FRP"].values
MODELED_FRP = ds_space_avg["MODELED_FRP"].values

utc_offset = ds_space_avg["ZoneST"].values[0]
LOCAL_TIME = ds_space_avg.time.values - pd.Timedelta(hours=utc_offset)
local_hours = pd.to_datetime(LOCAL_TIME).hour
over_pass_viirs = np.where(local_hours == presist_hour)[0]
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

ds_space_nan = ds_space_avg.dropna("time").isel(time=slice(24, None))
FRP_NAN = ds_space_nan["FRP"].values
MODELED_FRP_NAN = ds_space_nan["MODELED_FRP"].values
FRP_PRE_NAN = ds_space_nan["FRP_PRE"].values
###############################################################################################


# %%


FRP_PRE = ds_space_avg["FRP"].roll(time=24).interpolate_na(dim="time").values
# MODELED_FRP[np.isnan(FRP)==True] = np.nan
FRP_PRE[np.isnan(FRP) == True] = np.nan
ds_space_avg["FRP_PRE"] = (("time"), FRP_PRE)
fig = plt.figure(figsize=(16, 6))
ax = fig.add_subplot(1, 1, 1)
ax.plot(LOCAL_TIME, ds_space_avg["FRP_PRE"], color="tab:red")
ax.plot(LOCAL_TIME, ds_space_avg["FRP"], color="k")
ax.plot(LOCAL_TIME, ds_space_avg["MODELED_FRP"], color="tab:blue")

ds_space_avg_nan = ds_space_avg.dropna("time").isel(time=slice(24, -1))
FRP_NAN = ds_space_avg_nan["FRP"]
MODELED_FRP_NAN = ds_space_avg_nan["MODELED_FRP"]
FRP_PRE_NAN = ds_space_avg_nan["FRP_PRE"]

print(
    "MLP vs Observed \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
    + " MBE: "
    + str(np.round(MBE(FRP_NAN, MODELED_FRP_NAN), 2))
    + " (MW) RMSE: "
    + str(np.round(RMSE(FRP_NAN, MODELED_FRP_NAN), 2))
    + " (MW)"
)

print(
    "PRES. vs Observed \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
    + " MBE: "
    + str(np.round(MBE(FRP_NAN, FRP_PRE_NAN), 2))
    + " (MW) RMSE: "
    + str(np.round(RMSE(FRP_NAN, FRP_PRE_NAN), 2))
    + " (MW)"
)

plt.rcParams.update({"font.size": 14})
fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])


ax = fig.add_subplot(gs[0, 0])
ax.scatter(MODELED_FRP, FRP, color="tab:blue", label="MLP", zorder=10, s=20)
ax.scatter(FRP_PRE, FRP, color="tab:red", label="PERS", zorder=5, s=20)
# coeffs_mlp = np.polyfit(MODELED_FRP_NAN, FRP_NAN, 1)
# fit_line_mlp = np.poly1d(coeffs_mlp)
# ax.plot(MODELED_FRP_NAN, fit_line_mlp(MODELED_FRP_NAN), color="k", linestyle='-.', linewidth=0.5, zorder=10)

# # For PERS
# coeffs_pers = np.polyfit(FRP_PRE_NAN, FRP_NAN, 1)
# fit_line_pers = np.poly1d(coeffs_pers)
# ax.plot(FRP_PRE_NAN, fit_line_pers(FRP_PRE_NAN), color="k", linestyle=':', linewidth=0.5, zorder=10)
ax.legend(ncol=2, fancybox=True, shadow=True, loc="upper right")
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
ax.set_ylabel("Observed FRP (MW)")
ax.set_xlabel("Modeled FRP (MW)")
ax.set_title(
    "MLP vs Observed \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
    + " MBE: "
    + str(np.round(MBE(FRP_NAN, MODELED_FRP_NAN), 2))
    + " (MW) RMSE: "
    + str(np.round(RMSE(FRP_NAN, MODELED_FRP_NAN), 2))
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
    "PRES. vs Observed \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
    + " MBE: "
    + str(np.round(MBE(FRP_NAN, FRP_PRE_NAN), 2))
    + " (MW) RMSE: "
    + str(np.round(RMSE(FRP_NAN, FRP_PRE_NAN), 2))
    + " (MW)",
    loc="right",
    color="tab:red",
    fontsize=14,
)

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

utc_offset = ds_space_avg["ZoneST"].values[0]
LOCAL_TIME = ds_space_sum.time.values - pd.Timedelta(hours=utc_offset)
local_hours = pd.to_datetime(LOCAL_TIME).hour
over_pass_viirs = np.where(local_hours == presist_hour)[0]
fre_1300s = FRE[over_pass_viirs]
fre_1300s = replace_nan_with_previous(fre_1300s)
fre_1300s = np.roll(fre_1300s, 1)
fre_1300s[0] = 0


FRE_PRE = np.ravel(
    [
        scale_frp(fre_1300s[i], frp_curve[over_pass_viirs[0]], frp_curve)
        for i in range(len(fre_1300s))
    ]
)[: len(LOCAL_TIME)]

ds_space_sum["FRE_PRE"] = ("time", FRE_PRE)

FRE_PRE = ds_space_sum["FRE_PRE"].values
ds_space_sum = xr.where(
    np.isnan(ds_space_sum["FRP"].values) == True, np.nan, ds_space_sum
)

ds_space_nan = ds_space_sum.dropna("time").isel(time=slice(24, None))
FRE_NAN = ds_space_nan["FRE"].values
MODELED_FRE_NAN = ds_space_nan["MODELED_FRE"].values
FRE_PRE_NAN = ds_space_nan["FRE_PRE"].values
###############################################################################################


# %%
plt.rcParams.update({"font.size": 14})
fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, height_ratios=[1.2, 1])


ax = fig.add_subplot(gs[0, 0])
ax.scatter(MODELED_FRE, FRE, color="tab:blue", label="MLP", zorder=10, s=20)
ax.scatter(FRE_PRE, FRE, color="tab:red", label="PERS", zorder=5, s=20)
# coeffs_mlp = np.polyfit(MODELED_FRP_NAN, FRP_NAN, 1)
# fit_line_mlp = np.poly1d(coeffs_mlp)
# ax.plot(MODELED_FRP_NAN, fit_line_mlp(MODELED_FRP_NAN), color="k", linestyle='-.', linewidth=0.5, zorder=10)

# # For PERS
# coeffs_pers = np.polyfit(FRP_PRE_NAN, FRP_NAN, 1)
# fit_line_pers = np.poly1d(coeffs_pers)
# ax.plot(FRP_PRE_NAN, fit_line_pers(FRP_PRE_NAN), color="k", linestyle=':', linewidth=0.5, zorder=10)
ax.legend(ncol=2, fancybox=True, shadow=True, loc="upper right")
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
ax.set_ylabel("Observed FRE (MJ)")
ax.set_xlabel("Modeled FRE (MJ)")
ax.set_title(
    "MLP vs Observed \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRE_NAN, MODELED_FRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRE_NAN, MODELED_FRE_NAN), 2))
    + " MBE: "
    + "{:.1e}".format(np.round(MBE(FRE_NAN, MODELED_FRE_NAN), 2))
    + " (MJ) RMSE: "
    + "{:.1e}".format(np.round(RMSE(FRE_NAN, MODELED_FRE_NAN), 2))
    + " (MJ)"
    + "\n",
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
fre_vals = [FRE_NAN, MODELED_FRE_NAN, FRE_PRE_NAN]
labels = ["OBS", "MLP", "PERS"]
colors = ["k", "tab:blue", "tab:red"]
ax.set_ylabel("FRE (MJ)")
bplot = ax.boxplot(fre_vals, patch_artist=True, labels=labels)

for patch, color in zip(bplot["boxes"], colors):
    patch.set_facecolor(color)
ax.set_title(
    "PRES. vs Observed \n"
    + "r: "
    + str(np.round(stats.pearsonr(FRE_NAN, FRE_PRE_NAN)[0], 2))
    + r" $R^{2}$: "
    + str(np.round(r2_score(FRE_NAN, FRE_PRE_NAN), 2))
    + " MBE: "
    + "{:.1e}".format(np.round(MBE(FRE_NAN, FRE_PRE_NAN), 2))
    + " (MW) RMSE: "
    + "{:.1e}".format(np.round(RMSE(FRE_NAN, FRE_PRE_NAN), 2))
    + " (MW)"
    + "\n",
    loc="right",
    color="tab:red",
    fontsize=14,
)

ax = fig.add_subplot(gs[1, :])
# MODELED_FRE[np.isnan(FRE)==True] =np.nan
# FRE_NAN[np.isnan(FRE)==True] =np.nan
ax.plot(LOCAL_TIME, FRE, color="k", lw=2.5, zorder=1, label="OBS")
ax.plot(LOCAL_TIME, MODELED_FRE, color="tab:blue", label="MLP", lw=2, zorder=6)
ax.plot(LOCAL_TIME, FRE_PRE, color="tab:red", label="PERS", lw=2, zorder=5)
ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax.set_xlabel(f"Local DateTime (YYYY-MM-DD)", fontsize=18)
ax.set_ylabel(f"FRE (MJ)", fontsize=18)
fig.suptitle(fig_title, fontsize=22)


# %%

fig = plt.figure(figsize=(16, 12))
# Create a gridspec layout
# The first row (for maps) is twice the height of the second row (for line plots)
gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1])
g = salem.GoogleVisibleMap(
    x=[fire_i.min_x, fire_i.max_x],
    y=[fire_i.min_y, fire_i.max_y],
    scale=2,  # scale is for more details
    maptype="satellite",
    size_x=40,
    size_y=40,
)  # try out also: 'terrain'


model_title = "MODELED FIRE RADIATIVE ENERGY (MJ)"
obs_title = "OBSERVED FIRE RADIATIVE ENERGY (MJ)"
vmax = 4e8

vmax = np.nanpercentile(ds_time_sum["MODELED_FRE"].values, 99)
# np.nanpercentile(ds_time_sum["FRE"].values,95)

for var in list(ds_map):
    ds_time_sum[var].attrs = ds.attrs
ds_time_sum.attrs = ds.attrs

# First map on the top left
ax = fig.add_subplot(gs[0, 0])
ax.set_title(model_title)
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmin=0, vmax=vmax)
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_sum["MODELED_FRE"], overplot=True)
sm.set_scale_bar(
    location=(0.88, 0.94),
)
sm.visualize(ax=ax)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# Second map on the top right
ax = fig.add_subplot(gs[0, 1])
ax.set_title(obs_title)
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmin=0, vmax=vmax)
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_sum["FRE"], overplot=True)
sm.set_scale_bar(location=(0.88, 0.94))
sm.visualize(ax=ax)
ax.set_yticklabels([])
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


# %%
