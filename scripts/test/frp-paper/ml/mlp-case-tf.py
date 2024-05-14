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


index = 96
ml_pack = "tf"
mlp_test_case = "MLP_16U-Dense_16U-Dense_1U-Dense"
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
# config['year'] = years[index]
# ID = int(ids[index])
ID = 24448308  # 25407482 (2022) 25485086 (2022) 24360611 (2021) 24448308 (2021)
config["year"] = "2021"
firep = FIREP(config=config)
firep_df = firep.open_firep()

i = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[i : i + 1]

ds = xr.open_zarr(f"/Volumes/WFRT-Ext23/fire/all/{config['year']}-{ID}.zarr")
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
        df_dict[
            key
        ] = None  # or use an empty array np.array([]), or skip adding the key entirely
        # print(f"Key '{key}' not found in dataset. Defaulting to None.")

df = pd.DataFrame(df_dict)
df["time"] = np.ravel(zero_full)
df["ZoneST"] = np.ravel(np.ravel(ds["ZoneST"].values))
df["solar_hour"] = np.ravel(np.ravel(ds["solar_hour"].values))

df["dayofyear"] = (
    pd.to_datetime(df["time"]) - pd.to_timedelta(df["ZoneST"].astype(int), unit="h")
).dt.dayofyear

df["hour_sin"] = np.sin(2 * np.pi * df["solar_hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["solar_hour"] / 24)

pt = PowerTransformer(
    method="yeo-johnson", standardize=False
)  # Yeo-Johnson allows for zero values
df["Dead_Wood"] = pt.fit_transform(df[["Dead_Wood"]] + 1)
df["Live_Wood"] = pt.fit_transform(df[["Live_Wood"]] + 1)
df["Live_Leaf"] = pt.fit_transform(df[["Live_Leaf"]] + 1)
df["Dead_Foliage"] = pt.fit_transform(df[["Dead_Foliage"]] + 1)
df["FRP"] = np.log1p(df["FRP"])
df["U"] = np.log1p(df["U"])
df["R"] = np.log1p(df["R"])
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
FRPend = datetime.now() - startFRP
print("Time to predict FRP: ", FRPend)
FRP_FULL = np.expm1(FRP_FULL)
# print(f"Estimated time to predict FRP for 24h on 12km WRF {round(6275016.0/len(FRP) * FRPend.seconds /60,2)} Mins")
ds["MODELED_FRP"] = (("time", "y", "x"), FRP_FULL)
for var in list(ds):
    ds[var].attrs = ds.attrs
del FRP_FULL, FRP, model, X_new_scaled, scaler, X, df
print("Time to run FWX: ", datetime.now() - startFWX)

ds = xr.where(ds["FRP"] == 0, np.nan, ds)

ds_map = ds.rename({"FRP": "OBS_FRP"})

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


def drop_outside_std(arr, num_std=4):
    arr = ds_time_avg["OBS_FRP"].values
    # Calculate mean and standard deviation
    mean = np.nanmean(arr)
    std = np.nanstd(arr)

    # Define range based on number of standard deviations
    lower_bound = mean - num_std * std
    upper_bound = mean + num_std * std

    # Filter values within the range
    filtered_arr = arr[(arr >= lower_bound) & (arr <= upper_bound)]

    return float(np.max(filtered_arr))


vmax = (
    (
        (
            drop_outside_std(ds_time_avg["OBS_FRP"].values)
            + float(ds_time_avg["MODELED_FRP"].max())
        )
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


# %%


# %%
