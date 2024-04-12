import context
import salem
import joblib
import random
import string
import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


from utils.rave import RAVE
from utils.fwx import FWX
from utils.viirs import VIIRS

from scipy import stats
from utils.stats import MBE
from utils.geoutils import make_KDtree

from context import data_dir, root_dir


trail = "test3"
keep_vars = ["FFMC", "HFI", "LAI", "NDVI", "HGT", "GS", "hour", "month"]

# Configuration dictionary for the RAVE and FWX models
config = dict(
    model="wrf",
    trail_name="01",
    method="hourly",
    date_range=pd.date_range("2023-05-06", "2023-05-07", freq="h"),
    domain="d02",
)


rave = RAVE(config=config)
rave_ds = rave.open_rave(var_list=["FRP_MEAN"])
rave_ds = rave_ds.sel(x=slice(-179, -50), y=slice(25, 75))

fwx = FWX(config=config)
fwx_roi = fwx.open_fwx(var_list=["S", "F", "HFI"])
static_roi = salem.open_xr_dataset(
    str(data_dir) + f'/static/static-vars-wrf-{config["domain"]}.nc'
).expand_dims("time")
static_roi = static_roi[["ZoneST", "GS", "HGT", "LAND"]]
static_roi.coords["time"] = pd.Series(fwx_roi.time.values[0])


viirs = VIIRS(config=config)
ndvi_ds = viirs.open_ndvi()
lai_ds = viirs.open_lai()


rave_roi = fwx_roi.salem.transform(rave_ds, interp="linear")
ndvi_roi = fwx_roi.salem.transform(ndvi_ds["NDVI"], interp="nearest")
lai_roi = fwx_roi.salem.transform(lai_ds["LAI"], interp="nearest")


fwx_roi = xr.where(fwx_roi < 0, 0, fwx_roi)
lai_roi = xr.where(lai_roi < 0, 0, lai_roi)
lai_roi = xr.where(lai_roi < 0, 0, lai_roi)
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


for var in list(fwx_roi):
    fwx_roi[var].attrs = static_roi.attrs
fwx_roi.attrs = static_roi.attrs

# raveled = np.ravel(FFMC)
# new_arr = raveled.reshape(shape)

df = pd.DataFrame(
    {
        "FFMC": np.ravel(fwx_roi["F"].values),
        "HFI": np.ravel(fwx_roi["HFI"].values),
        "NDVI": np.ravel(fwx_roi["NDVI"].values),
        "LAI": np.ravel(fwx_roi["LAI"].values),
        "ZoneST": np.ravel(fwx_roi["ZoneST"].values),
        "HGT": np.ravel(fwx_roi["HGT"].values),
        "GS": np.ravel(fwx_roi["GS"].values),
        "time": np.ravel(zero_full),
    }
)

df["local_time"] = pd.to_datetime(df["time"]) - pd.to_timedelta(
    df["ZoneST"].astype(int), unit="h"
)
df["hour"] = df["local_time"].dt.hour
df["month"] = df["local_time"].dt.month
X = df[keep_vars]

# Load the scaler from disk
scaler = joblib.load(str(data_dir) + f"/mlp/{trail}/scaler.joblib")

# # Scale new data
X_new_scaled = scaler.transform(X)


model = joblib.load(str(data_dir) + f"/mlp/{trail}/model-1H20USEF.joblib")

FRP = model.predict(
    X_new_scaled
)  # model prediction for this number of hidden neurons (nhn)
FRP_FULL = FRP.reshape(shape)


fwx_roi["FRP"] = (("time", "south_north", "west_east"), FRP_FULL)
for var in list(fwx_roi):
    fwx_roi[var].attrs = static_roi.attrs
fwx_roi.attrs = static_roi.attrs


# y, x = make_KDtree('wrf', 'd02', [52.64,53.42], [-77., -72])
# # y, x = make_KDtree('wrf', 'd02', [57,58.2], [-122.5, -120.4])
# # y, x = make_KDtree('wrf', 'd02', [57.,60], [-113, -109.])

# fire_ds  = fwx_roi.isel(south_north =slice(y[0],y[1]), west_east = slice(x[0],x[1]))
# rave_close  = rave_roi.isel(south_north =slice(y[0],y[1]), west_east = slice(x[0],x[1]))


# fire_ds = xr.where(rave_close['FRP_MEAN'] == 0, np.nan, fire_ds)

# rave_close = xr.where(rave_close['FRP_MEAN'] == 0, np.nan, rave_close)


# fire_ds['FRP'].sum(( 'south_north', 'west_east')).plot()

# rave_close['FRP_MEAN'].sum(( 'south_north', 'west_east')).plot()


# (fire_ds['FRP'].sum(('time')) - rave_close['FRP_MEAN'].sum(('time'))).plot()

# rave_close['FRP_MEAN'].mean(('time')).plot(vmax = 140)


full_fwx = xr.where(rave_roi["FRP_MEAN"] == 0, np.nan, fwx_roi)
full_fwx = xr.where(np.isnan(rave_roi["FRP_MEAN"]) == True, np.nan, full_fwx)

full_rave = xr.where(rave_roi["FRP_MEAN"] == 0, np.nan, rave_roi)

full_fwx["FRP"].mean(("south_north", "west_east")).plot(label="MODEL", color="tab:blue")
full_rave["FRP_MEAN"].mean(("south_north", "west_east")).plot(
    label="OBS", color="tab:orange"
)
