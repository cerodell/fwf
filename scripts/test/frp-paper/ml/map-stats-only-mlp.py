#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from utils.ml_data import MLDATA
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler


from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


# Mark the start time for the run
startTime = datetime.now()


all_fire = True
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
persist = False

df = pd.read_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/avg-averaged-{method[-3:]}-persist-{persist}.csv"
)


# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00")
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


# %%
matplotlib.rcParams.update({"font.size": 22})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)


scaler = joblib.load(f"dot-scaler.joblib")
df["obs_hours_scale"] = scaler.transform(
    np.array(df["obs_hours"].values).reshape(-1, 1)
).flatten()

############################################################################
########################     Pearson's r        ############################
############################################################################

# Create a figure
fig = plt.figure(figsize=(18, 12))
# Set the GeoAxes to the projection used by WRF
ax = fig.add_subplot(2, 2, 1, projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

## plot wx stations locations
sc = ax.scatter(
    df["lons"],
    df["lats"],
    c=df["r"],
    cmap="PRGn",
    vmin=-1,
    vmax=1,
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=df["obs_hours_scale"],
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
cbar.set_label("r", rotation=90)

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


ax.set_title(f"Pearson's r")

# # save as png
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/map-pearsonr-{method}.png",
#     bbox_inches="tight",
#     dpi=240,
# )

############################################################################
############################       MAE        ##############################
############################################################################

# Create a figure
# Set the GeoAxes to the projection used by WRF
ax = fig.add_subplot(2, 2, 4, projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

vmin = np.percentile(df["mae"], 5)
vmax = np.percentile(df["mae"], 95)
vm = abs(vmax - abs(vmin))
## plot wx stations locations
sc = ax.scatter(
    df["lons"],
    df["lats"],
    c=df["mae"],
    cmap="Oranges_r",
    vmin=vmin,
    vmax=vmax,
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=df["obs_hours_scale"],
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
cbar.set_label("MW", rotation=90)

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

ax.set_title(f"Mean Absolute Error")

# # save as png
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/map-mbe-{method}.png",
#     bbox_inches="tight",
#     dpi=240,
# )

############################################################################
############################       RMSE       ##############################
############################################################################
# Create a figure
# Set the GeoAxes to the projection used by WRF
ax = fig.add_subplot(2, 2, 3, projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

vmin = np.percentile(df["rmse"], 5)
vmax = np.percentile(df["rmse"], 95)
## plot wx stations locations
sc = ax.scatter(
    df["lons"],
    df["lats"],
    c=df["rmse"],
    vmin=0,
    vmax=vmax,
    cmap="OrRd_r",
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=df["obs_hours_scale"],
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
cbar.set_label("MW", rotation=90)

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

ax.set_title(f"Root Mean Square Error")

# # save as png
# fig.savefig(
#     str(data_dir) + f"/images/frp-paper/map-rmse-{method}.png",
#     bbox_inches="tight",
#     dpi=240,
# )


############################################################################
##########################     R Square        #############################
############################################################################

# Create a figure
# Set the GeoAxes to the projection used by WRF
ax = fig.add_subplot(2, 2, 2, projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

vmin = np.percentile(df["r2"], 5)
vmax = np.percentile(df["r2"], 95)
## plot wx stations locations
sc = ax.scatter(
    df["lons"],
    df["lats"],
    c=df["r2"],
    vmin=-1,
    vmax=1,
    cmap="coolwarm",
    edgecolor="k",
    lw=0.5,
    zorder=10,
    alpha=1,
    s=df["obs_hours_scale"],
    transform=crs.PlateCarree(),
)

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Value", pad=0.01)
# cbar.set_label("MW", rotation=90)

ax.set_title(f"R Squared")

# Add the gridlines with labels
gl = ax.gridlines(
    draw_labels=False, linewidth=0.2, color="gray", alpha=1, linestyle="--"
)

# Create a second legend for the sizes
size_values_invers = np.array([30.0, 503.0, 1003.5])
# Calculate the range for obs_hours
min_obs_hours = int(size_values_invers[0])
median_obs_hours = int(size_values_invers[1])
max_obs_hours = int(size_values_invers[2])

# Create a second legend for the sizes
size_values = [10, 96, 187]
size_labels = ["30 - 499 h", "500 - 999 h", r"$>=$ 1000 h"]
size_legend = [
    plt.scatter([], [], s=size, lw=0.4, color="gray", edgecolor="k")
    for size in size_values
]

# Add the global legend
fig.legend(
    size_legend,
    size_labels,
    title="Observation Hours",
    loc="upper center",
    bbox_to_anchor=(0.5, 1.08),
    ncol=3,
)

plt.tight_layout()

#
## save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-stats-{method}.png",
    bbox_inches="tight",
    dpi=240,
)

# %%
