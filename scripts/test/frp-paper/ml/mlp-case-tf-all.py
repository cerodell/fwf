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


# index = 96
plot_method = "norm"
ml_pack = "tf"
mlp_test_case = "MLP_32U-Dense_32U-Dense_1U-Dense"
startFWX = datetime.now()
trail = "obs"

model_dir = str(data_dir) + f"/mlp/{ml_pack}/{mlp_test_case}"
save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)

config["model"] = "wrf"
config["method"] = "hourly"
config["trail_name"] = "01"


fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
ids = fire_cases[0].astype(int)
years = fire_cases[1].astype(int)
for i in range(len(ids)):
    config["year"] = years[i]
    ID = int(ids[i])
    # ID = 25485086  # 25407482 (2022) 25485086 (2022) 24448308 (2021)
    # config["year"] = "2022"
    firep = FIREP(config=config)
    firep_df = firep.open_firep()
    jj = firep_df[firep_df["id"] == ID].index[0]
    fire_i = firep_df.iloc[jj : jj + 1]

    if os.path.exists(f"/Volumes/ThunderBay/CRodell/fires/{config['year']}-{ID}.nc"):
        ds = xr.open_dataset(
            f"/Volumes/ThunderBay/CRodell/fires/{config['year']}-{ID}.nc"
        )[["FRP", "MODELED_FRP"]]
        ds_nan = xr.open_zarr(
            f"/Volumes/WFRT-Ext23/fire/full/{config['year']}-{ID}.zarr"
        )["FRP"].to_dataset()
        ds_nan["MODELED_FRP"] = (("time", "y", "x"), ds["MODELED_FRP"].values)
    else:

        ds = xr.open_zarr(f"/Volumes/WFRT-Ext23/fire/full/{config['year']}-{ID}.zarr")
        ds_og = ds
        ds_nan = ds["FRP"].to_dataset()
        ds_attrs = ds.attrs
        ds_attrs["pyproj_srs"] = ds["S"].attrs["pyproj_srs"]

        mlD = MLDATA(config=config)
        ds = mlD.get_static(ds)
        ds = get_solar_hours(ds)
        ds = xr.where(np.isnan(ds["FRP"].values) == True, 0, ds)

        shape = ds["F"].shape
        times = ds["time"].values
        zero_full = np.empty(shape, dtype="datetime64[ns]")
        for i in range(shape[0]):
            times_full = np.full(shape[1:3], times[i])
            zero_full[i] = times_full

        df_dict = {}
        for key in config["features_used"]:
            try:
                df_dict[key] = np.ravel(ds[key].values)
            except KeyError:
                df_dict[key] = None

        df = pd.DataFrame(df_dict)
        df["solar_hour"] = np.ravel(np.ravel(ds["solar_hour"].values))
        df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)

        # pt = PowerTransformer(method="yeo-johnson", standardize=False)
        # df["Dead_Wood"] = pt.fit_transform(df[["Dead_Wood"]] + 1)
        # df["Live_Wood"] = pt.fit_transform(df[["Live_Wood"]] + 1)
        # df["Live_Leaf"] = pt.fit_transform(df[["Live_Leaf"]] + 1)
        # df["Dead_Foliage"] = pt.fit_transform(df[["Dead_Foliage"]] + 1)
        # df["U"] = np.log1p(df["U"])
        # df["R"] = np.log1p(df["R"])
        X = df[config["features_used"]]

        # Load the scaler
        scaler = joblib.load(f"{model_dir}/scaler.joblib")
        X_new_scaled = scaler.transform(X)

        # Load the model
        model = load_model(f"{model_dir}/model.keras")

        startFRP = datetime.now()
        print("Start prediction:", startFRP)
        FRP = model.predict(X_new_scaled)
        FRP_FULL = FRP.ravel().reshape(shape)
        FRPend = datetime.now() - startFRP
        print("Time to predict FRP: ", FRPend)
        # FRP_FULL = np.expm1(FRP_FULL)
        ds["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
        ds_nan["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
        # ds["MODELED_FRP"] = xr.where(ds["FRP"] == 0, 0, ds["MODELED_FRP"])
        for var in list(ds):
            if var == "MODELED_FRP":
                ds[var].attrs = {
                    "description": "MODELED FIRE RADIATIVE POWER",
                    "pyproj_srs": "+proj=longlat +datum=WGS84 +no_defs",
                    "units": "(MW)",
                }
            else:
                ds[var].attrs = ds_og[var].attrs
        ds.attrs = ds_attrs
        print("Time to run FWX: ", datetime.now() - startFWX)

        startWRITE = datetime.now()
        ds, encoding = compressor(ds)
        file_dir = f"/Volumes/ThunderBay/CRodell/fires/{config['year']}-{ID}.nc"
        print(f"WRITING AT: {datetime.now()}")
        ds.to_netcdf(file_dir, encoding=encoding, mode="w")
        print(f"Wrote: {file_dir}")
        print("Time to write: ", datetime.now() - startWRITE)

    ds["MODELED_FRP"] = xr.where(ds["FRP"] == 0, 0, ds["MODELED_FRP"])
    plot_fire(fire_i, ds, ds_nan, save_dir, method="sum")
    plot_fire(fire_i, ds, ds_nan, save_dir, method="mean")
    plot_fire(fire_i, ds, ds_nan, save_dir, method="norm")
