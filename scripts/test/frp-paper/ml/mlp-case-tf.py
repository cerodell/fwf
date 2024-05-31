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


all_fire = True
ID = 26695902  # 25407482 (2022) 25485086 (2022) 24448308 (2021) 24360611 (2021) 24450415 (2021) 26695902 (2023) 26414629 (2023)
year = "2023"
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v2"
ml_pack = "tf"
plot_method = "mean"
persist = False
dt = 6


def predict_frp(config):
    ID = config["ID"]
    year = config["year"]
    firep = FIREP(config=config)
    firep_df = firep.open_firep()
    jj = firep_df[firep_df["id"] == ID].index[0]
    fire_i = firep_df.iloc[jj : jj + 1]

    ds = xr.open_zarr(f"/Volumes/WFRT-Ext23/fire/full/{year}-{ID}.zarr")
    ds_og = ds
    ds_attrs = ds.attrs
    ds_attrs["pyproj_srs"] = ds["S"].attrs["pyproj_srs"]

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
    # print(config["features_used"])

    for key in config["features_used"]:
        try:
            df_dict[key] = np.ravel(ds[key].values)
        except KeyError:
            df_dict[key] = None

    df = pd.DataFrame(df_dict)

    X = df[config["features_used"]]

    # Load the scaler
    scaler = joblib.load(f"{model_dir}/scaler.joblib")
    X_new_scaled = scaler.transform(X)

    # Load the model
    model = load_model(f"{model_dir}/model.keras")

    startFRP = datetime.now()
    # print("Start prediction:", startFRP)
    FRP = model(X_new_scaled)
    FRP_FULL = FRP.numpy().ravel().reshape(shape)
    FRPend = datetime.now() - startFRP
    print("Time to predict FRP: ", FRPend)
    ds["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
    for var in list(ds):
        if var == "MODELED_FRP":
            ds[var].attrs = {
                "description": "MODELED FIRE RADIATIVE POWER",
                "pyproj_srs": ds_attrs["pyproj_srs"],
                "units": "(MW)",
            }
        else:
            ds[var].attrs = ds_og[var].attrs
    ds.attrs = ds_attrs
    # print("Time to run FWX: ", datetime.now() - startFWX)
    # startWRITE = datetime.now()
    # ds, encoding = compressor(ds)
    # file_dir = f"/Volumes/ThunderBay/CRodell/fires/v2/{year}-{ID}.nc"
    # # print(f"WRITING AT: {datetime.now()}")
    # ds.to_netcdf(file_dir, encoding=encoding, mode="w")
    # print(f"Wrote: {file_dir}")
    # print("Time to write: ", datetime.now() - startWRITE)
    return ds, fire_i


model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{mlp_test_case}/"
save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)

if all_fire == False:
    config["ID"] = ID
    config["year"] = year
    ds, fire_i = predict_frp(config)

elif all_fire == True:
    fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
    ids = fire_cases[0].astype(int)
    years = fire_cases[1].astype(int)
    for i in range(len(ids)):
        config["ID"] = int(ids[i])
        config["year"] = years[i]
        ds, fire_i = predict_frp(config)
        ds["MODELED_FRP"] = xr.where(ds["FRP"] == 0, 0, ds["MODELED_FRP"])
        plot_fire(fire_i, ds, persist, dt, save_dir, "mean")
        print(ID)
