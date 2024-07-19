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


all_fire = False
ID = 24564038
year = 2021
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v11"
ml_pack = "tf"
target_vars = "FRP"
plot_method = "mean"
persist = False
dt = 6
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
# ID = fire_cases[0].astype(int)[10]
# year = fire_cases[1].astype(int)[10]


def predict_frp(config):
    ID = config["ID"]
    year = config["year"]
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
    # times = ds["time"].values
    # zero_full = np.empty(shape, dtype="datetime64[ns]")
    # for i in range(shape[0]):
    #     times_full = np.full(shape[1:3], times[i])
    #     zero_full[i] = times_full

    df_dict = {}
    # print(config["feature_vars"])

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

    # Load the model
    model = load_model(f"{model_dir}/model.keras")

    startFRP = datetime.now()
    # print("Start prediction:", startFRP)
    y_out_this_nhn = model(X_new_scaled).numpy()
    if config["target_scaler_type"] != None:
        # y_out_this_nhn = target_scaler.inverse_transform(y_out_this_nhn)
        y_out_this_nhn = y_out_this_nhn * config["FRP_MAX"]
    if config["transform"] == True:
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
        elif var == "MODELED_FRE":
            ds[var].attrs = {
                "description": "FIRE ENERGY POWER",
                "pyproj_srs": ds_attrs["pyproj_srs"],
                "units": "(MJ)",
            }
        else:
            ds[var].attrs = ds_og[var].attrs
    ds.attrs = ds_attrs
    print("Time to run FWX: ", datetime.now() - startFWX)
    startWRITE = datetime.now()
    ds, encoding = compressor(ds)
    file_dir = f"/Volumes/ThunderBay/CRodell/fires/v9/{year}-{ID}.nc"
    print(f"WRITING AT: {datetime.now()}")
    ds.to_netcdf(file_dir, encoding=encoding, mode="w")
    print(f"Wrote: {file_dir}")
    print("Time to write: ", datetime.now() - startWRITE)
    return ds, fire_i


# for var in list(ds):
#     if np.any(np.isinf(ds[var].values)) == True:
#         print(var)


save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]

if all_fire == False:
    config["ID"] = ID
    config["year"] = year
    ds, fire_i = predict_frp(config)
    plot_fire(fire_i, ds, persist, dt, save_dir, "mean")

elif all_fire == True:
    fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
    ids = fire_cases[0].astype(int)
    years = fire_cases[1].astype(int)
    for i in range(len(ids)):
        config["ID"] = int(ids[i])
        config["year"] = years[i]
        ds, fire_i = predict_frp(config)
        # ds["MODELED_FRP"] = xr.where(ds["FRP"] == 0, 0, ds["MODELED_FRP"])
        plot_fire(fire_i, ds, persist, dt, save_dir, "mean")
        # print(ID)
