#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import joblib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.ml_data import MLDATA
from utils.firep import FIREP
from utils.compressor import compressor

from tensorflow.keras.models import load_model
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from context import root_dir, data_dir

import warnings

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)
startFWX = datetime.now()


# 25282348 (2022) "Calf Canyon/Hermits Peak Fire" https://go.nasa.gov/4bQXoME
# 24564081 (2021) "Fire ID 24564081 / Northern California"
# 26691009 (2023) "Fire ID 26691009 / Coastal British Columbia"
# 26567967 (2023) "Fire ID 26567967 / Northwest Territories, Canada"
ID = 25282348
year = 2022
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]

config["ID"] = ID
config["year"] = year
########################################################################################################
#####################################       RUN MODEL         ##########################################
########################################################################################################


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

    # Load the model
    model = load_model(f"{model_dir}/model.keras")

    startFRP = datetime.now()
    print("Start prediction:", startFRP)
    y_out_this_nhn = model(X_new_scaled).numpy()
    if config["target_scaler_type"] != None:
        print("rescaling target")
        y_out_this_nhn[:, 0] = y_out_this_nhn[:, 0] * config["FRP_MAX"]
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
    save_dir = Path(f"/Volumes/ThunderBay/CRodell/fires/{method[-3:]}/")
    save_dir.mkdir(parents=True, exist_ok=True)
    print(f"WRITING AT: {datetime.now()}")
    ds.to_netcdf(str(save_dir) + f"/{year}-{ID}.nc", encoding=encoding, mode="w")
    print("Time to write: ", datetime.now() - startWRITE)
    return


for i in range(len(ids)):
    config["ID"] = int(ids[i])
    config["year"] = years[i]
    predict_frp(config)
