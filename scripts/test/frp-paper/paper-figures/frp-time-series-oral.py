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
import matplotlib.dates as mdates
from matplotlib.patches import Ellipse

from scipy import stats
from utils.stats import MBE, RMSE, MAE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter


from context import root_dir, data_dir


######################################################
# ID = 25723697
# year = 2022
# fig_title = "McFarland Fire, California, United States"
######################################################
ID = 26695902
year = 2023
fig_title = "Northwest Territories, Canada"
hour_interval = 3
######################################################
save_fig = True
paper_fig = False
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v19"
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


ds_map = xr.open_dataset(f"/Volumes/ThunderBay/CRodell/fires/v19/{year}-{ID}.nc")[
    ["FRP", "FRE", "MODELED_FRP"]
]
area_ha = float(ds_map.attrs["area_ha"])
area_ha = format(area_ha, ".2e")


ds_map = ds_map.sel(time=slice("2023-08-13T00", None))
# fig_title = fig_title + f"\n {area_ha} hectors"

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
    # FRP_MEAN_PERS = ds_active["FRP"].mean(dim ='time').values
    # ds_active['FRP_MEAN_PERS'] = (('time', 'y', 'x'), np.tile(FRP_MEAN_PERS, (desired_shape[0], 1, 1)))

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
        # FRP_MEAN_PERS = ds_active["FRP"].mean(dim ='time').values
        ds_active = ds_map.isel(time=slice(i, i + dt))
        nan_array = np.isnan(ds_active["FRP"]).values
        ds_active["MODELED_FRP"] = xr.where(
            nan_space <= 0, np.nan, ds_active["MODELED_FRP"]
        )
        # desired_shape = ds_active["FRP"].shape
        # ds_active['FRP_MEAN_PERS'] = (('time', 'y', 'x'), np.tile(FRP_MEAN_PERS, (desired_shape[0], 1, 1)))

        zero_full = np.zeros(nan_array.shape)
        zero_full[nan_array == False] = 1
        nan_space = np.sum(np.stack(zero_full), axis=0)

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

# PERS_days = []
# FRP_PRE = ds_space_avg['FRP'].roll(time =24).interpolate_na(dim ='time').to_dataset()
# for i in range(0, len(FRP_PRE.time), 24):
#     FRP_PRE_DAY = FRP_PRE.isel(time = slice(i, i+24))
#     desired_shape = FRP_PRE_DAY['FRP'].shape
#     FRP_MEAN_PERS = FRP_PRE_DAY['FRP'].mean(dim ='time').values
#     FRP_PRE_DAY['FRP_MEAN_PERS'] = (('time'), np.tile(FRP_MEAN_PERS, (desired_shape[0])))
#     PERS_days.append(FRP_PRE_DAY)

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
fig = plt.figure(figsize=(18, 6))
ax = fig.add_subplot(1, 1, 1)
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

# Set the major and minor ticks
ax.xaxis.set_major_locator(
    mdates.DayLocator(interval=hour_interval)
)  # Major ticks every 1 day

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
ax.set_xlabel(f"Local DateTime ({pd.Timestamp(LOCAL_TIME[0]).year}-MM-DD)", fontsize=18)
ax.set_ylabel(f"FRP (MW)", fontsize=18)
ax.grid(True, which="both", linestyle="--", linewidth=0.1, color="grey")
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
ax.set_title(
    "PERS vs OBS \n"
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
fig.suptitle(fig_title, fontsize=22, y=1.05)

# Add the area_ha in a smaller font as a subtitle
fig.text(
    0.5,
    0.96,
    f"Area Burned: {area_ha} hectares",
    ha="center",
    fontsize=14,
    transform=fig.transFigure,
)

if save_fig == True:
    fig.savefig(
        str(data_dir)
        + f"/images/frp-paper/fireID-{ID}-year-{year}-frp-time-series-{method[-3:]}-pers-oral.png",
        bbox_inches="tight",
        dpi=240,
    )

if paper_fig == True:
    fig.savefig(
        f"/Users/crodell/ams-frp/fireID-{ID}-year-{year}-frp-time-series-{method[-3:]}-oral.pdf",
        bbox_inches="tight",
    )


# %%
