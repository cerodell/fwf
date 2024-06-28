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
mlp_test_case = "MLP_64U-Dense_64U-Dense_64U-Dense_64U-Dense_2U-Dense-Decent"
model_dir = str(data_dir) + f"/mlp/tf/averaged-v7/FRP_FRE/{mlp_test_case}"


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
    # fwf_daily = (
    #     xr.open_dataset(
    #         f"{fwf_dir}/{domain}/{doi.strftime('%Y')}/fwf-daily-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    #     )["U"]
    #     .to_dataset()
    #     .chunk("auto")
    # )
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


# def predict_frp(doi, domain, model_dir):
startFRP = datetime.now()
### Open model config
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]
mlD = MLDATA(config)
# print("Start prediction:", startFRP)
fwf_ds = open_fwf(doi, domain)  # .isel(time = slice(0,24))

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

# Load the model
model = load_model(f"{model_dir}/model.keras")
y_out_this_nhn = model(X_new_scaled).numpy()

if config["transform"] == True:
    y_out_this_nhn = np.expm1(y_out_this_nhn)

FRP_FULL = y_out_this_nhn[:, 0].ravel().reshape(shape)
FRE_FULL = y_out_this_nhn[:, 1].ravel().reshape(shape)

fwf_ds["FRP"] = (("time", "south_north", "west_east"), FRP_FULL)
fwf_ds["FRE"] = (("time", "south_north", "west_east"), FRE_FULL)

# fwf_ds["MODELED_FRP"] = xr.where(fwf_ds["SNOWC"] > 0.5, 0, fwf_ds["MODELED_FRP"])
# fwf_ds["MODELED_FRE"] = xr.where(fwf_ds["SNOWC"] > 0.5, 0, fwf_ds["MODELED_FRE"])
# fwf_ds["MODELED_FRP"] = xr.where(fwf_ds["MODELED_FRP"] <= 0.0, 0, fwf_ds["MODELED_FRP"])
# fwf_ds["MODELED_FRE"] = xr.where(fwf_ds["Total_Fuel_Load"] <= 0.0, 0, fwf_ds["MODELED_FRE"])

for var in list(fwf_ds):
    if var == "FRP":
        fwf_ds[var].attrs = {
            "description": "MEAN FIRE RADIATIVE POWER",
            "pyproj_srs": target_grid.attrs["pyproj_srs"],
            "units": "(MW)",
        }
    elif var == "FRE":
        fwf_ds[var].attrs = {
            "description": "FIRE ENERGY POWER",
            "pyproj_srs": target_grid.attrs["pyproj_srs"],
            "units": "(MJ)",
        }
    else:
        fwf_ds[var].attrs["pyproj_srs"] = target_grid.attrs["pyproj_srs"]
fwf_ds.attrs = target_grid.attrs
FRPend = datetime.now() - startFRP
print("Time to predict FRP: ", FRPend)
# return fwf_ds

# fwf_ds['R-diurnal_curve-Total_Fuel_Load'] = fwf_ds['R']  * fwf_ds['diurnal_curve']  * fwf_ds['Total_Fuel_Load']

fwf_ds["FRP"].isel(time=18).salem.quick_map(vmin=0, vmax=2500)
fwf_ds["R"].isel(time=18).salem.quick_map()

# fwf_ds = predict_frp(doi, domain, model_dir)

test = pd.DatetimeIndex(fwf_ds["Time"].values)
# print(float(fwf_ds["MODELED_FRP"].max()))

y, x = make_KDtree(49.01554, -76.43027, target_grid)
# y, x = make_KDtree(57.47797,-121.16833, target_grid)
# y, x = make_KDtree(27.92145, -81.09624, target_grid)
# y, x = make_KDtree(62.21035,-113.32549, target_grid)
# y, x = make_KDtree(37.307,-113.571, target_grid)
# y, x = make_KDtree(40,-140, target_grid)


# frp_interp = fwf_ds.isel(x= x, y =y)
frp_interp = fwf_ds.isel(west_east=x, south_north=y)

fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(1, 1, 1)
frp_interp[""].plot(ax=ax)
# # plt.savefig('MODELED_FRP.png')
fig = plt.figure(figsize=(10, 3))
ax = fig.add_subplot(1, 1, 1)
# frp_interp["Total_Fuel_Load"].plot(ax=ax)

# for var in config["feature_vars"]:
#     fig = plt.figure(figsize=(10, 3))
#     ax = fig.add_subplot(1, 1, 1)
#     frp_interp[var].plot(ax=ax)

# # fig = plt.figure(figsize=(10,3))
# # ax = fig.add_subplot(1,1,1)
# # frp_interp['U'].plot(ax =ax)

# fig = plt.figure(figsize=(10, 3))
# ax = fig.add_subplot(1, 1, 1)
# frp_interp["r_o"].plot(ax=ax)
# # plt.savefig('S.png')

# %%
# frp_da_small = fwf_ds.isel(time=slice(0, 24))
# frp_i = hourly_rain(frp_da_small)

# frp_i = frp_da_small.isel(time=18)
# # frp_i["MODELED_FRP"] = xr.where(frp_i["Live_Wood"]<0.05,0, frp_i["MODELED_FRP"])

# for var in list(frp_i):
#     frp_i[var].attrs = target_grid.attrs
# frp_i.attrs = target_grid.attrs
