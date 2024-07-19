#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib

from utils.ml_data import MLDATA
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v12"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)
feature_vars = config["user_config"]["feature_vars"]


train_ids = np.loadtxt(f"{model_dir}/train_cases.txt", delimiter=",")[0, :]
val_ids = np.loadtxt(f"{model_dir}/val_cases.txt", delimiter=",")[0, :]
test_ids = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")[0, :]

# user_config['min_fire_size'] = 1000
mlD = MLDATA(config=config["user_config"])
df = mlD.open_ml_ds()


# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d02_2023-04-20_00:00:00")
# Get the sea level pressure
slp = getvar(ncfile, "slp")
# Get the cartopy mapping object
cart_proj = get_cartopy(slp)

## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_shp",
    scale="50m",
    facecolor="none",
)


df_group = df.groupby("id").first().reset_index()
scaler = MinMaxScaler(feature_range=(10, 400))
area_ha = scaler.fit_transform(
    np.array(df_group["area_ha"].values).reshape(-1, 1)
).flatten()
df_group["scaled_area"] = area_ha
df_train = df_group[df_group["id"].isin(train_ids)]
df_val = df_group[df_group["id"].isin(val_ids)]
df_test = df_group[df_group["id"].isin(test_ids)]

# %%
matplotlib.rcParams.update({"font.size": 16})
# plt.rc("font", family="sans-serif")
# plt.rc("text", usetex=True)

# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)


## plot wx stations locations
sc = ax.scatter(
    df_train["lons"],
    df_train["lats"],
    color="tab:blue",
    edgecolor="k",
    lw=0.5,
    zorder=1,
    alpha=1,
    s=df_train["scaled_area"],
    transform=crs.PlateCarree(),
    label=f"Training:    {len(df_train)}",
)

## plot wx stations locations
sc = ax.scatter(
    df_val["lons"],
    df_val["lats"],
    color="tab:green",
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=df_val["scaled_area"],
    transform=crs.PlateCarree(),
    label=f"Validation: {len(df_val)}",
)

## plot wx stations locations
sc = ax.scatter(
    df_test["lons"],
    df_test["lats"],
    color="tab:orange",
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=df_test["scaled_area"],
    transform=crs.PlateCarree(),
    label=f"Testing:     {len(df_test)}",
)

lgnd = ax.legend()
lgnd.legend_handles[0]._sizes = [100]
lgnd.legend_handles[1]._sizes = [100]
lgnd.legend_handles[2]._sizes = [100]


# Add the gridlines
# Customize the gridlines
gl = ax.gridlines(
    draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
)

gl.top_labels = False
gl.left_labels = False
# gl.xlines = False
gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])

gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

plt.tight_layout()

ax.set_title(
    f"Total fires:  {len(df_group)}",
    loc="left",
)
# save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-fires-train-val-test.png",
    bbox_inches="tight",
    dpi=240,
)
# %%
