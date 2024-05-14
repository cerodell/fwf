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


mlp_test_case = "MLP_32U-Dense_32U-Dense_1U-Dense"
trail = "obs"
model_dir = str(data_dir) + f"/mlp/{mlp_test_case}"
save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)

config["model"] = "wrf"
config["method"] = "hourly"
config["trail_name"] = "01"
config["date_range"] = pd.date_range("2023-06-06", "2023-06-06", freq="h")
config["domain"] = "d02"


fwx = FWX(config=config)
fwx_roi = fwx.open_fwx(var_list=["S", "F", "HFI"])
fwx_roi = get_solar_hours(fwx_roi)
static_roi = salem.open_xr_dataset(
    str(data_dir) + f'/static/static-vars-wrf-{config["domain"]}.nc'
).expand_dims("time")
static_roi = static_roi[["ZoneST", "GS", "HGT", "LAND"]]
static_roi.coords["time"] = pd.Series(fwx_roi.time.values[0])

mlD = MLDATA(config=config)
fwx_roi = mlD.get_static(fwx_roi)
fwx_roi = get_solar_hours(fwx_roi)

viirs = VIIRS(config=config)
ndvi_ds = viirs.open_ndvi()
lai_ds = viirs.open_lai()

ndvi_roi = fwx_roi.salem.transform(ndvi_ds["NDVI"], interp="nearest")
lai_roi = fwx_roi.salem.transform(lai_ds["LAI"], interp="nearest")


fwx_roi = xr.where(fwx_roi < 0, 0, fwx_roi)
lai_roi = xr.where(lai_roi < 0, 0, lai_roi)
lai_roi = xr.where(lai_roi > 25, 0, lai_roi)
ndvi_roi = xr.where(ndvi_roi < -1, -1, ndvi_roi)
ndvi_roi = xr.where(ndvi_roi > 1, 1, ndvi_roi)


lai_roi = xr.where(np.isnan(lai_roi) == True, 0, lai_roi)
ndvi_roi = xr.where(np.isnan(ndvi_roi) == True, 0, ndvi_roi)

ndvi_roi = ndvi_roi.reindex(time=fwx_roi.time, method="ffill")
lai_roi = lai_roi.reindex(time=fwx_roi.time, method="ffill")
static_roi = static_roi.reindex(time=fwx_roi.time, method="ffill")

fwx_roi["LAI"] = lai_roi
fwx_roi["NDVI"] = ndvi_roi

for var in list(static_roi):
    fwx_roi[var] = static_roi[var]
fwx_roi = xr.where(static_roi["LAND"] == 1, 0, fwx_roi)

shape = fwx_roi["F"].shape
times = fwx_roi["time"].values
zero_full = np.empty(shape, dtype="datetime64[ns]")
for i in range(shape[0]):
    times_full = np.full(shape[1:3], times[i])
    zero_full[i] = times_full

df_dict = {}
for key in config["features_used"]:
    try:
        df_dict[key] = np.ravel(fwx_roi[key].values)
    except KeyError:
        df_dict[
            key
        ] = None  # or use an empty array np.array([]), or skip adding the key entirely
        # print(f"Key '{key}' not found in dataset. Defaulting to None.")

df = pd.DataFrame(df_dict)
df["time"] = np.ravel(zero_full)
df["ZoneST"] = np.ravel(np.ravel(fwx_roi["ZoneST"].values))
df["solar_hour"] = np.ravel(np.ravel(fwx_roi["solar_hour"].values))

df["dayofyear"] = (
    pd.to_datetime(df["time"]) - pd.to_timedelta(df["ZoneST"].astype(int), unit="h")
).dt.dayofyear

df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)
X = df[config["features_used"]]

# Load the scaler from disk
scaler = joblib.load(f"{model_dir}/scaler.joblib")
# # Scale new data
X_new_scaled = scaler.transform(X)

model = load_model(f"{model_dir}/model.keras")

startFRP = datetime.now()
print("Start prediction:", startFRP)
FRP = model.predict(X_new_scaled)
FRP_FULL = FRP.ravel().reshape(shape)
print("Time to predict FRP: ", datetime.now() - startFRP)

fwx_roi["FRP"] = (("time", "south_north", "west_east"), FRP_FULL)
for var in list(fwx_roi):
    fwx_roi[var].attrs = static_roi.attrs
fwx_roi.attrs = static_roi.attrs

del FRP_FULL, FRP, model, X_new_scaled, scaler, X, df
print("Time to run FWX: ", datetime.now() - startFWX)


# rave = RAVE(config=config)
# rave_ds = rave.open_rave(var_list=["FRP_MEAN"])
# rave_ds = rave_ds.sel(x=slice(-179, -50), y=slice(25, 75))
# rave_roi = fwx_roi.salem.transform(rave_ds, interp="linear")


# ########################################################################
# ############################ FULL DOMAIN ###############################
# ########################################################################
# time = fwx_roi.time.values
# save_time = pd.Timestamp(time[0]).strftime("%Y%m%d%H")

# full_fwx = xr.where(rave_roi["FRP_MEAN"] == 0, np.nan, fwx_roi)
# full_fwx = xr.where(np.isnan(rave_roi["FRP_MEAN"]) == True, np.nan, full_fwx)
# full_rave = xr.where(rave_roi["FRP_MEAN"] == 0, np.nan, rave_roi)

# obs = full_rave['FRP_MEAN'].sum(( 'south_north', 'west_east')).values
# model = full_fwx["FRP"].sum(("south_north", "west_east")).values
# time = full_rave.time.values

# fig = plt.figure(figsize=(10,4))
# ax = fig.add_subplot(1,1,1)
# ax.plot(time, obs, label="Obs", color="tab:orange")
# ax.plot(time, model, label="MODEL", color="tab:blue")
# ax.set_ylabel('FRP (MW)')
# ax.legend()
# fig.autofmt_xdate()
# r2 = np.round(r2_score(obs, model), 2)
# pr = np.round(stats.pearsonr(obs, model)[0], 2)
# rmse = np.round(RMSE(obs, model), 2)
# mbe = np.round(MBE(obs, model), 2)
# ax.set_title(f"R^2: {r2}     r: {pr}  rmse {rmse}   mbe {mbe}")
# fig.savefig(str(save_dir) + f'/full-timeseries-{save_time}.png')


# ########################################################################
# fig = plt.figure(figsize=(6,6))
# ax = fig.add_subplot(1,1,1)
# sc = ax.scatter(model, obs, zorder = 10,c=mdates.date2num(pd.to_datetime(time)))
# cbar = plt.colorbar(sc, ax=ax, pad=0.008, alpha=1)
# loc = mdates.AutoDateLocator()
# cbar.ax.yaxis.set_major_locator(loc)
# cbar.ax.tick_params(labelsize=16)
# cbar.ax.yaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
# ax.set_xlabel('modeled FRP')
# ax.set_ylabel('Observed FRP')
# ax.axline((0, 0), slope=1, color = 'k', zorder = 1)
# fig.savefig(str(save_dir) + f'/full-scatter-{save_time}.png')


# ########################################################################

fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(1, 1, 1)
fwx_roi["FRP"].isel(time=0).salem.quick_map(ax=ax, cmap="jet", vmin=0, vmax=400)
# fig.savefig(str(save_dir) + f'/full-frp-{save_time}.png', bbox_inches='tight')


fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(1, 1, 1)
fwx_roi["S"].isel(time=0).salem.quick_map(
    ax=ax, states=True, prov=True, cmap="jet", vmin=0, vmax=80, oceans=True, lakes=True
)
# fig.savefig(str(save_dir) + f'/full-fwi-{save_time}.png',  bbox_inches='tight')

fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(1, 1, 1)
fwx_roi["NDVI"].isel(time=0).salem.quick_map(
    ax=ax,
    states=True,
    prov=True,
    cmap="Greens",
    vmin=0,
    vmax=1,
    oceans=True,
    lakes=True,
)
# fig.savefig(str(save_dir) + f'/full-ndvi-{save_time}.png',  bbox_inches='tight')


fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(1, 1, 1)
fwx_roi["LAI"].isel(time=0).salem.quick_map(
    ax=ax, states=True, prov=True, cmap="YlGn", vmin=0, vmax=4, oceans=True, lakes=True
)
# fig.savefig(str(save_dir) + f'/full-lai-{save_time}.png',  bbox_inches='tight')


fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(1, 1, 1)
fwx_roi["HFI"].isel(time=0).salem.quick_map(
    ax=ax,
    states=True,
    prov=True,
    cmap="jet",
    vmin=0,
    vmax=10000,
    oceans=True,
    lakes=True,
)
# fig.savefig(str(save_dir) + f'/full-hfi-{save_time}.png',  bbox_inches='tight')
# print("Total Run Time: ", datetime.now() - startTime)
