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
from utils.solar_hour import get_solar_hours
from tensorflow.keras.models import load_model

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from context import root_dir, data_dir

import warnings

startFWX = datetime.now()
# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)


doi = pd.Timestamp("2023-06-06")
mlp_test_case = "MLP_32U-Dense_32U-Dense_1U-Dense"
model_dir = str(data_dir) + f"/mlp/tf/averaged-v2/{mlp_test_case}"
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)

static_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")
ny = (417 * 4) - 12
nx = (627 * 4) - 12

target_grid = salem.Grid(
    nxny=(nx, ny),
    dxdy=(3000.0, 3000.0),
    x0y0=(-3593999.2734108134, -6343328.220350546),
    proj=static_ds.attrs["pyproj_srs"],
).to_dataset()

# smap = salem.Map(grid)
# smap.visualize(addcbar=False)


def transform_ds(ds, domain):
    if domain != "fuel":
        ds["time"] = ds["Time"]
        static_ds = salem.open_xr_dataset(
            str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
        )
        if domain == "d03":
            static_ds = static_ds.isel(
                west_east=slice(30, 610), south_north=slice(30, 810)
            )
        ds["west_east"] = static_ds["west_east"]
        ds["south_north"] = static_ds["south_north"]
        for var in list(ds):
            ds[var].attrs = static_ds.attrs
        ds.attrs = static_ds.attrs
    return target_grid.salem.transform(ds, interp="linear")


startTRANSFORM = datetime.now()
print("Start transform:", startTRANSFORM)
fwf_dir = "/Volumes/WFRT-Ext24/fwf-data/wrf/"
fwf_hourly_d02 = (
    xr.open_dataset(f"{fwf_dir}/d02/04/fwf-hourly-d02-{doi.strftime('%Y%m%d06')}.nc")[
        "R"
    ]
    .to_dataset()
    .chunk("auto")
)
fwf_daily_d02 = (
    xr.open_dataset(f"{fwf_dir}/d02/04/fwf-daily-d02-{doi.strftime('%Y%m%d06')}.nc")[
        "U"
    ]
    .to_dataset()
    .chunk("auto")
)
fwf_hourly_d02 = get_solar_hours(fwf_hourly_d02)
fwf_daily_d02 = transform_ds(fwf_daily_d02, "d02")
fwf_hourly_d02 = transform_ds(fwf_hourly_d02, "d02")


fwf_hourly_d03 = (
    xr.open_dataset(f"{fwf_dir}/d03/04/fwf-hourly-d03-{doi.strftime('%Y%m%d06')}.nc")[
        "R"
    ]
    .to_dataset()
    .isel(west_east=slice(30, 610), south_north=slice(30, 810))
    .chunk("auto")
)
fwf_daily_d03 = (
    xr.open_dataset(f"{fwf_dir}/d03/04/fwf-daily-d03-{doi.strftime('%Y%m%d06')}.nc")[
        "U"
    ]
    .to_dataset()
    .isel(west_east=slice(30, 610), south_north=slice(30, 810))
    .chunk("auto")
)
fwf_daily_d03 = transform_ds(fwf_daily_d03, "d03")
fwf_hourly_d03 = transform_ds(fwf_hourly_d03, "d03")


fwf_hourly_d02["R"] = xr.where(
    ~np.isnan(fwf_hourly_d03["R"]), fwf_hourly_d03["R"], fwf_hourly_d02["R"]
)
fwf_daily_d02["U"] = xr.where(
    ~np.isnan(fwf_daily_d03["U"]), fwf_daily_d03["U"], fwf_daily_d02["U"]
)
fwf_daily_d02 = fwf_daily_d02.reindex(time=fwf_hourly_d02.Time, method="ffill")

fwf_hourly = fwf_hourly_d02
fwf_hourly["U"] = fwf_daily_d02["U"]
shape = fwf_hourly["R"].shape

del fwf_hourly_d02, fwf_daily_d02, fwf_hourly_d03, fwf_daily_d03


def open_fuels(moi):
    fuel_dir = f"/Volumes/WFRT-Ext23/fuel-characteristics/fuel-load/"
    fuels_ds = salem.open_xr_dataset(
        fuel_dir + f'{2021}/CFUEL_timemean_2021{moi.strftime("_%m")}.nc'
    ).sel(lat=slice(75, 20), lon=slice(-170, -50))
    fuels_ds.coords["time"] = moi
    return fuels_ds


fuel_date_range = pd.date_range(
    fwf_hourly["Time"].values[0],
    fwf_hourly["Time"].values[-1],
    freq="MS",
)
if len(fuel_date_range) == 0:
    fuel_date_range = [pd.Timestamp(fwf_hourly["Time"].values[0])]
fuels_ds = xr.combine_nested(
    [open_fuels(moi) for moi in fuel_date_range], concat_dim="time"
)

fuels_ds = transform_ds(fuels_ds, "fuel")
fuels_ds = fuels_ds.reindex(time=fwf_hourly.Time, method="ffill")
for var in list(fuels_ds):
    fwf_hourly[var] = fuels_ds[var]

del fuels_ds
fwf_hourly = xr.where(np.isnan(fwf_hourly["Dead_Wood"]), 0, fwf_hourly)

for var in list(fwf_hourly):
    fwf_hourly[var].attrs = target_grid.attrs
fwf_hourly.attrs = target_grid.attrs
print("Time to transform data: ", datetime.now() - startTRANSFORM)


df_dict = {}
for key in config["features_used"]:
    try:
        df_dict[key] = np.ravel(fwf_hourly[key].values)
    except KeyError:
        df_dict[key] = None

df = pd.DataFrame(df_dict)
df["solar_hour"] = np.ravel(np.ravel(fwf_hourly["solar_hour"].values))
df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)
X = df[config["features_used"]]

# Load the scaler
scaler = joblib.load(f"{model_dir}/scaler.joblib")
X_new_scaled = scaler.transform(X)

# https://micwurm.medium.com/using-tensorflow-lite-to-speed-up-predictions-a3954886eb98
# Load the model
model = load_model(f"{model_dir}/model.keras")

startFRP = datetime.now()
print("Start prediction:", startFRP)

FRP = model(X_new_scaled)
FRP_FULL = FRP.numpy().ravel().reshape(shape)
FRPend = datetime.now() - startFRP
print("Time to predict FRP: ", FRPend)
fwf_hourly["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
for var in list(fwf_hourly):
    fwf_hourly[var].attrs = static_ds.attrs
fwf_hourly.attrs = static_ds
