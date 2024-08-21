#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
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
from utils.fwx import FWX
from utils.wrf_ import hourly_rain
from utils.solar_hour import get_solar_hours
from utils.geoutils import make_KDtree
from tensorflow.keras.models import load_model

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors

from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm

from context import root_dir, data_dir

import warnings

startFWX = datetime.now()
# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)

domain = "d02"
doi = pd.Timestamp("2023-06-06")
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/tf/{method}/{target_vars}/{mlp_test_case}"
save_dir = f"/Volumes/ThunderBay/CRodell/frp/{domain}"

### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


target_grid = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")


def open_fwf(doi, domain):

    fwf_dir = "/Volumes/WFRT-Ext24/fwf-data/wrf/"
    # fwf_dir = " /Volumes/ThunderBay/CRodell/fwf-data/"
    static = salem.open_xr_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )
    fwf_hourly = xr.open_dataset(
        f"{fwf_dir}/{domain}/04/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    ).chunk("auto")
    # fwf_hourly = xr.open_dataset(
    #     f"{fwf_dir}/{domain}/{doi.strftime('%Y')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    # ).chunk("auto")
    print(list(fwf_hourly))
    fwf_hourly = fwf_hourly  # [['S', 'R', 'SNOWC', 'r_o', 'F']]
    fwf_hourly["time"] = fwf_hourly["Time"]
    fwf_daily = (
        xr.open_dataset(
            f"{fwf_dir}/{domain}/04/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
        )["U"]
        .to_dataset()
        .chunk("auto")
    )

    fwf_daily["time"] = fwf_daily["Time"]
    fwf_hourly["U"] = fwf_daily["U"].reindex(time=fwf_hourly.Time, method="ffill")
    fwf_hourly["west_east"] = static["west_east"]
    fwf_hourly["south_north"] = static["south_north"]

    for var in list(fwf_hourly):
        fwf_hourly[var].attrs = static.attrs
    fwf_hourly.attrs = static.attrs
    del static
    return fwf_hourly


def open_fuels(moi):
    moi = pd.Timestamp(moi)
    fuel_dir = f"/Volumes/ThunderBay/CRodell/ecmwf/fuel-load/"
    fuels_ds = salem.open_xr_dataset(
        fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
    ).sel(lat=slice(75, 20), lon=slice(-170, -50))
    fuels_ds.coords["time"] = moi
    return fuels_ds


def solve_frp(doi, domain):
    # def predict_frp(doi, domain, model_dir):
    startFRP = datetime.now()
    ### Open model config
    with open(f"{model_dir}/config.json", "r") as json_data:
        config = json.load(json_data)["user_config"]
    mlD = MLDATA(config)
    # print("Start prediction:", startFRP)
    fwf_ds = open_fwf(doi, domain)  # .isel(time = slice(0,24))
    # ds = fwf_ds
    # curves_ds = salem.open_xr_dataset(str(data_dir) + "/static/curves-wrf-d02.nc")
    # fire_time = ds.time.values
    # hour_one = pd.Timestamp(fire_time[0]).hour
    # curves_ds = curves_ds.roll(time=-hour_one, roll_coords=True)
    # for var in list(curves_ds):
    #     CURVES_VAR = curves_ds[var].values
    #     N = len(fire_time)
    #     ds[var] = (
    #         ("time", "south_north", "west_east"),
    #         np.tile(CURVES_VAR, (N + 1, 1, 1))[:N, :, :],
    #     )
    #     ds[var].attrs = ds.attrs

    fwf_ds = mlD.get_static(fwf_ds, static=target_grid)
    fwf_ds = mlD.get_eng_features(fwf_ds, wrf=True)

    shape = fwf_ds["S"].shape
    df_dict = {}
    print(config["feature_vars"])
    for key in config["feature_vars"]:
        try:
            df_dict[key] = np.ravel(fwf_ds[key].values)
        except KeyError:
            df_dict[key] = None

    df = pd.DataFrame(df_dict)
    X = df[config["feature_vars"]]

    # Load the scaler
    feature_scaler = joblib.load(f"{model_dir}/feature-scaler.joblib")
    X_new_scaled = feature_scaler.transform(X)
    df_scaled = pd.DataFrame(X_new_scaled, columns=config["feature_vars"])
    for var in config["feature_vars"]:
        fwf_ds[var] = (
            ("time", "south_north", "west_east"),
            df_scaled[var].values.reshape(shape),
        )
        fwf_ds[var].attrs = fwf_ds.attrs

    # Load the model
    model = load_model(f"{model_dir}/model.keras")
    y_out_this_nhn = model(X_new_scaled).numpy()

    if config["target_scaler_type"] == True:
        # print("self.target_scaler_type is: ", self.target_scaler_type)
        # y_out_this_nhn = self.target_scaler.inverse_transform(y_out_this_nhn)
        y_out_this_nhn = y_out_this_nhn * config["FRP_MAX"]

    if config["transform"] == True:
        y_out_this_nhn = np.expm1(y_out_this_nhn)

    FRP_FULL = y_out_this_nhn.ravel().reshape(shape)
    fwf_ds["FRP"] = (("time", "south_north", "west_east"), FRP_FULL)

    fwf_ds["FRP"] = xr.where(target_grid["LAND"] == 1, 0, fwf_ds["FRP"])
    fwf_ds["FRP"] = xr.where(np.isnan(fwf_ds["FRP"]) == True, 0, fwf_ds["FRP"])

    # fwf_ds = fwf_ds[['FRP']]
    for var in list(fwf_ds):
        if var == "FRP":
            fwf_ds[var].attrs = {
                "description": "MEAN FIRE RADIATIVE POWER",
                "pyproj_srs": target_grid.attrs["pyproj_srs"],
                "units": "(MW)",
            }
        else:
            try:
                fwf_ds[var] = fwf_ds[var].astype("float32")
            except:
                pass
            fwf_ds[var].attrs["pyproj_srs"] = target_grid.attrs["pyproj_srs"]
    fwf_ds.attrs = target_grid.attrs
    FRPend = datetime.now() - startFRP
    print("Time to predict FRP: ", FRPend)
    fwf_ds = fwf_ds.drop_vars("XTIME")
    fwf_ds.to_netcdf(str(data_dir) + f"/frp/sample_{domain}_{method}.nc", mode="w")
    # fwf_ds.to_netcdf(str(save_dir) + f"/frp-{domain}-{doi.strftime('%Y%m%d06')}.nc", mode = 'w')

    del fwf_ds, df, X, df_scaled, X_new_scaled, FRP_FULL, model, mlD
    return


# date_range = pd.date_range("2023-05-01", "2023-09-01")

# for doi in date_range:
solve_frp(doi, domain)
# except:
#     pass
