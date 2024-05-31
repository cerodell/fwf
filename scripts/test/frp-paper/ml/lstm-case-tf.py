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

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)

index = 96
mlp_test_case = (
    "LSTM_32U-LSTM_32U-LSTM_TD-32U-Dense-relu_TD-32U-Dense-relu_TD-1U-Dense-relu"
)
startFWX = datetime.now()
trail = "obs"
model_dir = str(data_dir) + f"/lstm/{mlp_test_case}"
save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)

config["model"] = "wrf"
config["method"] = "hourly"
config["trail_name"] = "01"


fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
ids = fire_cases[0].astype(int)
years = fire_cases[1].astype(int)
config["year"] = years[index]
ID = int(ids[index])
ID = 24360611  # 25407482 (2022) 25485086 (2022) 24360611 (2021)
config["year"] = "2021"

firep = FIREP(config=config)
firep_df = firep.open_firep()

i = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[i : i + 1]

ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext23/fire/all/{config['year']}-{ID}.zarr", consolidated=False
)
mlD = MLDATA(config=config)
ds = mlD.get_static(ds)
ds = get_solar_hours(ds)

ds = xr.where(np.isnan(ds["FRP"].values) == True, 0, ds)

block_size = 24
time_light = len(ds.time)
n_blocks = time_light // block_size
n_feature = len(config["features_used"])
ds_sliced = ds.isel(time=slice(0, n_blocks * block_size))


ds_sliced["hour_sin"] = np.sin(2 * np.pi * ds_sliced["solar_hour"] / 24)
ds_sliced["hour_cos"] = np.cos(2 * np.pi * ds_sliced["solar_hour"] / 24)
shape = ds_sliced["S"].shape
xx = shape[1]
yy = shape[2]

X = []
for var in config["features_used"]:
    X.append(np.reshape(ds_sliced[var].values, (n_blocks * block_size, -1)))


X_stacked = np.stack(X, axis=-1)
# Load the scaler from disk
scaler = joblib.load(f"{model_dir}/scaler.joblib")
model = load_model(f"{model_dir}/model.keras")


startFRP = datetime.now()
print("Start prediction:", startFRP)
FRP_STACKED = []
for i in range(X_stacked.shape[1]):
    # # Scale new data
    X_new_scaled = scaler.transform(X_stacked[:, i, :])

    test = X_new_scaled.reshape(n_blocks, block_size, n_feature)

    FRP = model.predict(test, verbose=False)

    # FRP_Shape = FRP.reshape(shape[1], shape[2])
    # FRP_Shape = FRP.ravel()
    FRP_STACKED.append(FRP.ravel())


ds_sliced["MODELED_FRP"] = (
    ("time", "y", "x"),
    np.stack(FRP_STACKED, axis=-1).reshape(n_blocks * block_size, xx, yy),
)


print("Time to run FWX: ", datetime.now() - startFWX)

ds_sliced = xr.where(ds_sliced["FRP"] == 0, np.nan, ds_sliced)

ds_map = ds_sliced.rename({"FRP": "OBS_FRP"})

# for var in list(ds_map):
#     ds_map[var].attrs = ds_map.attrs


# %%

plt.rcParams.update({"font.size": 14})

fig = plt.figure(figsize=(16, 12))

# Create a gridspec layout
# The first row (for maps) is twice the height of the second row (for line plots)
gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1])
g = salem.GoogleVisibleMap(
    x=[fire_i.min_x, fire_i.max_x],
    y=[fire_i.min_y, fire_i.max_y],
    scale=2,  # scale is for more details
    maptype="satellite",
)  # try out also: 'terrain'


ds_time_avg = ds_map.mean(dim="time")
for var in list(ds_map):
    ds_time_avg[var].attrs = ds.attrs
ds_time_avg.attrs = ds.attrs


vmax = (
    (
        (float(ds_time_avg["OBS_FRP"].max()) + float(ds_time_avg["MODELED_FRP"].max()))
        / 2
    )
    // 50
    * 50
)

if vmax > 2000:
    vmax -= 500
# First map on the top left
ax = fig.add_subplot(gs[0, 0])
ax.set_title("MODELED FIRE RADIATIVE POWER MEAN (MW)")
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmax=vmax, vmin=0)
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_avg["MODELED_FRP"], overplot=True)
# sm.set_data(ds.sel(time = doi), overplot=True)
sm.set_scale_bar(
    location=(0.88, 0.94),
)
sm.visualize(ax=ax)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


# Second map on the top right
ax = fig.add_subplot(gs[0, 1])
ax.set_title("OBSERVED FIRE RADIATIVE POWER MEAN (MW)")
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmax=vmax, vmin=0)
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_avg["OBS_FRP"], overplot=True)
# sm.set_data(rave_roi.sel(time = doi), overplot=True)
sm.set_scale_bar(location=(0.88, 0.94))
sm.visualize(ax=ax)
ax.set_yticklabels([])
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

ax = fig.add_subplot(gs[1, :])
ds_space_avg = ds_map.mean(dim=("x", "y"))


ax.plot(
    ds_space_avg.time,
    ds_space_avg["OBS_FRP"],
    color="k",
    label="OBSERVED FRP",
    lw=2.5,
    zorder=1,
)
ax.plot(
    ds_space_avg.time,
    ds_space_avg["MODELED_FRP"],
    color="tab:red",
    label="MODELED FRP",
    lw=1.75,
    zorder=10,
)
ax.legend(
    ncol=3,
    fancybox=True,
    shadow=True,
    bbox_to_anchor=(0.3, 1.2),
)
ds_nan_free = ds_space_avg.dropna("time")
MODELED_FRP = ds_nan_free["MODELED_FRP"].values
OBS_FRP = ds_nan_free["OBS_FRP"].values

ax.set_title(
    "pearsonr: " + str(np.round(stats.pearsonr(OBS_FRP, MODELED_FRP)[0], 2)) +
    # "\n r2_score: " + str(np.round(r2_score(OBS_FRP, MODELED_FRP), 2)) +
    "\n mbe: "
    + str(np.round(MBE(OBS_FRP, MODELED_FRP), 2))
    + "\n rmse: "
    + str(np.round(RMSE(OBS_FRP, MODELED_FRP), 2)),
    loc="right",
)
# Adjust layout for a better fit
fig.tight_layout()
plt.show()
fig.savefig(str(save_dir) + f"/{fire_i['id'].values[0]}.png")
