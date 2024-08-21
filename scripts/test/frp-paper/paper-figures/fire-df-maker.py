#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import os
import json
import joblib
import logging
import simplekml
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from scipy import stats
from utils.stats import MBE, RMSE, MAE
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt

# import plotly.experss as px

from datetime import datetime
from utils.ml_data import MLDATA
from utils.firep import FIREP

from context import data_dir
import warnings

warnings.simplefilter(action="ignore", category=UserWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]

fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
ids = fire_cases[0].astype(int)
years = fire_cases[1].astype(int)
persist = True
dt = 12


year_j = None
mbe_avg_mlp, mae_avg_mlp, rmse_avg_mlp, r2_avg_mlp, r_avg_mlp = [], [], [], [], []
mbe_sum_mlp, mae_sum_mlp, rmse_sum_mlp, r2_sum_mlp, r_sum_mlp = [], [], [], [], []
mbe_avg_pers, mae_avg_pers, rmse_avg_pers, r2_avg_pers, r_avg_pers = [], [], [], [], []
mbe_sum_pers, mae_sum_pers, rmse_sum_pers, r2_sum_pers, r_sum_pers = [], [], [], [], []
lats, lons, area_ha, obs_hours = [], [], [], []
years_i, ids_i = [], []


mlp_avg, obs_avg = [], []
mlp_sum, obs_sum = [], []

for jj in range(len(ids)):
    ID = int(ids[jj])
    year = years[jj]

    ds_map = xr.open_dataset(
        f"/Volumes/ThunderBay/CRodell/fires/{method[-3:]}/{year}-{ID}.nc"
    )[["FRP", "FRE", "MODELED_FRP"]]
    area_ha_i = ds_map.attrs["area_ha"]
    lons_i = np.mean([float(ds_map.attrs["min_x"]), float(ds_map.attrs["max_x"])])
    lats_i = np.mean([float(ds_map.attrs["min_y"]), float(ds_map.attrs["max_y"])])

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
        # ds_map_sum = ds_map_sum.salem.roi(shape=fire_i, all_touched=True)

    else:
        ds_map = xr.where(np.isnan(ds_map["FRP"].values) == True, np.nan, ds_map)

    ######### mlp stats for avg FRP #########
    ds_space_avg = ds_map.mean(dim=("x", "y"), skipna=True)
    FRP = ds_space_avg["FRP"].values
    MODELED_FRP = ds_space_avg["MODELED_FRP"].values

    ####### combine all cases  #####
    all_ds_space_avg = ds_map.mean(dim=("x", "y"), skipna=True).dropna("time")
    obs_avg.append(all_ds_space_avg["FRP"].values)
    mlp_avg.append(all_ds_space_avg["MODELED_FRP"].values)
    obs_sum.append(all_ds_space_avg["FRE"].values)
    mlp_sum.append(all_ds_space_avg["MODELED_FRP"].values * 3600)

    FRP_PRE = ds_space_avg["FRP"].roll(time=24).interpolate_na(dim="time").values
    FRP_PRE[np.isnan(FRP) == True] = np.nan
    ds_space_avg["FRP_PRE"] = (("time"), FRP_PRE)
    FRP_PRE = ds_space_avg["FRP_PRE"].values

    ds_space_avg_nan = ds_space_avg.isel(time=slice(24, -1)).dropna("time")
    FRP_NAN = ds_space_avg_nan["FRP"].values
    if len(FRP_NAN) >= 24:
        MODELED_FRP_NAN = ds_space_avg_nan["MODELED_FRP"].values
        FRP_PRE_NAN = ds_space_avg_nan["FRP_PRE"].values

        mbe_avg_mlp.append(str(np.round(MBE(FRP_NAN, MODELED_FRP_NAN), 2)))
        mae_avg_mlp.append(str(np.round(MAE(FRP_NAN, MODELED_FRP_NAN), 2)))
        rmse_avg_mlp.append(np.round(RMSE(FRP_NAN, MODELED_FRP_NAN), 2))
        r2_avg_mlp.append(np.round(r2_score(FRP_NAN, MODELED_FRP_NAN), 2))
        r_avg_mlp.append(np.round(stats.pearsonr(FRP_NAN, MODELED_FRP_NAN)[0], 2))

        mbe_avg_pers.append(str(np.round(MBE(FRP_NAN, FRP_PRE_NAN), 2)))
        mae_avg_pers.append(str(np.round(MAE(FRP_NAN, FRP_PRE_NAN), 2)))
        rmse_avg_pers.append(np.round(RMSE(FRP_NAN, FRP_PRE_NAN), 2))
        r2_avg_pers.append(np.round(r2_score(FRP_NAN, FRP_PRE_NAN), 2))
        r_avg_pers.append(np.round(stats.pearsonr(FRP_NAN, FRP_PRE_NAN)[0], 2))

        ######### mlp stats for summed FRE #########
        ds_space_sum = ds_map.sum(dim=("x", "y"), skipna=True)
        ds_space_sum["MODELED_FRE"] = ds_space_sum["MODELED_FRP"] * 3600

        FRE = ds_space_sum["FRE"].values
        MODELED_FRE = ds_space_sum["MODELED_FRE"].values
        FRE_PRE = ds_space_sum["FRE"].roll(time=24).interpolate_na(dim="time").values
        FRE[np.isnan(FRP) == True] = np.nan
        MODELED_FRE[np.isnan(FRP) == True] = np.nan
        FRE_PRE[np.isnan(FRP) == True] = np.nan
        ds_space_sum["FRE_PRE"] = (("time"), FRE_PRE)

        ds_space_sum = xr.where(
            np.isnan(ds_space_avg["FRP"].values) == True, np.nan, ds_space_sum
        )
        ds_space_nan = ds_space_sum.isel(time=slice(24, -1)).dropna("time")
        FRE_NAN = ds_space_nan["FRE"].values
        MODELED_FRE_NAN = ds_space_nan["MODELED_FRE"].values
        FRE_PRE_NAN = ds_space_nan["FRE_PRE"].values

        mbe_sum_mlp.append(str(np.round(MBE(FRE_NAN, MODELED_FRE_NAN), 2)))
        mae_sum_mlp.append(str(np.round(MAE(FRE_NAN, MODELED_FRE_NAN), 2)))
        rmse_sum_mlp.append(np.round(RMSE(FRE_NAN, MODELED_FRE_NAN), 2))
        r2_sum_mlp.append(np.round(r2_score(FRE_NAN, MODELED_FRE_NAN), 2))
        r_sum_mlp.append(np.round(stats.pearsonr(FRE_NAN, MODELED_FRE_NAN)[0], 2))

        mbe_sum_pers.append(str(np.round(MBE(FRE_NAN, FRE_PRE_NAN), 2)))
        mae_sum_pers.append(str(np.round(MAE(FRE_NAN, FRE_PRE_NAN), 2)))
        rmse_sum_pers.append(np.round(RMSE(FRE_NAN, FRE_PRE_NAN), 2))
        r2_sum_pers.append(np.round(r2_score(FRE_NAN, FRE_PRE_NAN), 2))
        r_sum_pers.append(np.round(stats.pearsonr(FRE_NAN, FRE_PRE_NAN)[0], 2))

        ######### sapio-temporal info on fire #########
        obs_hours.append(len(FRE_NAN))
        area_ha.append(float(area_ha_i))
        lons.append(lons_i)
        lats.append(lats_i)
        years_i.append(year)
        ids_i.append(ID)

    else:
        print(len(FRP_NAN))
        print(ID)
        print(year)

df_final = pd.DataFrame(
    dict(
        ids=ids_i,
        years=years_i,
        obs_hours=obs_hours,
        lats=lats,
        lons=lons,
        area_ha=area_ha,
        mbe_avg_mlp=mbe_avg_mlp,
        mae_avg_mlp=mae_avg_mlp,
        rmse_avg_mlp=rmse_avg_mlp,
        r2_avg_mlp=r2_avg_mlp,
        r_avg_mlp=r_avg_mlp,
        mbe_sum_mlp=mbe_sum_mlp,
        mae_sum_mlp=mae_sum_mlp,
        rmse_sum_mlp=rmse_sum_mlp,
        r2_sum_mlp=r2_sum_mlp,
        r_sum_mlp=r_sum_mlp,
        mbe_avg_pers=mbe_avg_pers,
        mae_avg_pers=mae_avg_pers,
        rmse_avg_pers=rmse_avg_pers,
        r2_avg_pers=r2_avg_pers,
        r_avg_pers=r_avg_pers,
        mbe_sum_pers=mbe_sum_pers,
        mae_sum_pers=mae_sum_pers,
        rmse_sum_pers=rmse_sum_pers,
        r2_sum_pers=r2_sum_pers,
        r_sum_pers=r_sum_pers,
    )
)

df_final.to_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/avg-averaged-{method[-3:]}-persist-{persist}.csv",
    index=False,
)

all_df = pd.DataFrame(
    dict(
        mlp_avg=np.hstack(mlp_avg),
        obs_avg=np.hstack(obs_avg),
        mlp_sum=np.hstack(mlp_sum),
        obs_sum=np.hstack(obs_sum),
    )
)

all_df.to_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/all-cases-{method[-3:]}-persist-{persist}.csv",
    index=False,
)
