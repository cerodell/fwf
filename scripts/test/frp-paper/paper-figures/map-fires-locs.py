#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import joblib
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
method = "averaged-v15"
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

print(f'Hours of data use for training:   {len(df[df["id"].isin(train_ids)])}')
print(f'Hours of data use for validation: {len(df[df["id"].isin(val_ids)])}')
print(f'Hours of data use for testing:    {len(df[df["id"].isin(test_ids)])}')

obs_hours = []
for name, group in df.groupby("id"):
    obs_hours.append(len(group["FRP"]))

df_group = df.groupby("id").first().reset_index()
scaler = MinMaxScaler(feature_range=(10, 300))

obs_hours_scaled = scaler.fit_transform(np.array(obs_hours).reshape(-1, 1)).flatten()
joblib.dump(scaler, "dot-scaler.joblib")
df_group["obs_hours_scaled"] = obs_hours_scaled
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
sc_train = ax.scatter(
    df_train["lons"],
    df_train["lats"],
    color="tab:blue",
    edgecolor="k",
    lw=0.3,
    zorder=1,
    alpha=1,
    s=df_train["obs_hours_scaled"],
    transform=crs.PlateCarree(),
    label=f"Training:    {len(df_train)}",
)

## plot wx stations locations
sc_val = ax.scatter(
    df_val["lons"],
    df_val["lats"],
    color="tab:green",
    edgecolor="k",
    lw=0.3,
    zorder=10,
    alpha=1,
    s=df_val["obs_hours_scaled"],
    transform=crs.PlateCarree(),
    label=f"Validation:  {len(df_val)}",
)

## plot wx stations locations
sc_test = ax.scatter(
    df_test["lons"],
    df_test["lats"],
    color="tab:orange",
    edgecolor="k",
    lw=0.3,
    zorder=10,
    alpha=1,
    s=df_test["obs_hours_scaled"],
    transform=crs.PlateCarree(),
    label=f"Testing:      {len(df_test)}",
)

# First legend for the color coding
lgnd1 = ax.legend(loc="upper right")
for handle in lgnd1.legend_handles:
    handle._sizes = [100]

# Add the gridlines with labels
gl = ax.gridlines(
    draw_labels=False, linewidth=0.2, color="gray", alpha=1, linestyle="--"
)

# Create a second legend for the sizes
# size_values = [9.85, 92.2, 184.5]
size_values = [10, 96, 187]
size_values_invers = scaler.inverse_transform(
    np.array(size_values).reshape(-1, 1)
).ravel()  # Small, medium, large
print(size_values_invers)
# Calculate the range for obs_hours
min_obs_hours = int(size_values_invers[0])
median_obs_hours = int(size_values_invers[1])
max_obs_hours = int(size_values_invers[2])

# Generate the labels
size_labels = [
    f"{min_obs_hours:.0f} - {int((median_obs_hours//10)*10-1)} h",
    f"{int((median_obs_hours//10)*10)} - {int((max_obs_hours//10)*10-1)} h",
    r"$>=$" + f"{int((max_obs_hours//10)*10)} h",
]
size_legend = [
    plt.scatter([], [], s=size, lw=0.4, color="gray", edgecolor="k")
    for size in size_values
]

lgnd2 = plt.legend(
    size_legend,
    size_labels,
    title="Observation Hours",
    loc="upper center",
    bbox_to_anchor=(0.5, 1.13),
    ncol=3,
)

ax.add_artist(lgnd1)  # Add the first legend back to the axes

plt.tight_layout()

fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-fires-train-val-test-{method[-3:]}.png",
    bbox_inches="tight",
    dpi=240,
)
