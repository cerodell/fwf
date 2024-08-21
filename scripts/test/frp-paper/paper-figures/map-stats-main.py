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
persist = True

df = pd.read_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/avg-averaged-{method[-3:]}-persist-{persist}.csv"
)


# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00")
# Get the sea level perssure
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


scaler = joblib.load("dot-scaler.joblib")
df["obs_hours_scale"] = scaler.transform(
    np.array(df["obs_hours"].values).reshape(-1, 1)
).flatten()


########################## Add Static ################################
def add_static(ax):
    ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
    ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
    ax.coastlines("50m", linewidth=0.8, zorder=5)
    # Add a colorbar
    gl = ax.gridlines(
        draw_labels=False, linewidth=0.1, color="gray", alpha=1, linestyle="--"
    )
    # gl.top_labels = False
    # gl.left_labels = False
    # gl.xlines = False
    # gl.xlocator = mticker.FixedLocator([-180, -160, -140, -120, -100, -80, -60, -40])
    # gl.ylocator = mticker.FixedLocator([30, 40, 50, 60, 70])
    # gl.xformatter = LONGITUDE_FORMATTER
    # gl.yformatter = LATITUDE_FORMATTER
    return


########################     Pearson's r        ############################
def map_r(var, index, sub_label, y_label):
    ax = fig.add_subplot(3, 4, index, projection=cart_proj)
    sc = ax.scatter(
        df["lons"],
        df["lats"],
        c=df[var],
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
    cbar = plt.colorbar(sc, ax=ax, orientation="horizontal", label="Value", pad=0.01)
    cbar.set_label("r")
    ax.set_title(sub_label)
    add_static(ax)
    ax.text(
        x=-0.1,  # x-coordinate of the text (use negative values to push it outside the map)
        y=0.5,  # y-coordinate of the text (0.5 is centered vertically)
        s=y_label,  # The label text
        va="center",  # vertical alignment of the text
        ha="center",  # horizontal alignment of the text
        rotation="vertical",  # rotate the text vertically
        transform=ax.transAxes,  # use axis coordinates (0,0 bottom-left, 1,1 top-right)
    )
    return


############################       MAE        ##############################
def map_mae(var, index, method, sub_label):
    ax = fig.add_subplot(3, 4, index, projection=cart_proj)
    vmin = np.percentile(df[f"mae_{method}_pers"], 5)
    vmax_pers = np.percentile(df[f"mae_{method}_pers"], 95)
    vmax_mlp = np.percentile(df[f"mae_{method}_mlp"], 95)
    if vmax_pers > vmax_mlp:
        vmax = vmax_pers
    else:
        vmax = vmax_mlp
    ## plot wx stations locations
    sc = ax.scatter(
        df["lons"],
        df["lats"],
        c=df[var],
        cmap="GnBu",
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
    cbar = plt.colorbar(sc, ax=ax, orientation="horizontal", label="Value", pad=0.01)
    if method == "avg":
        cbar.set_label("MW")
    else:
        cbar.set_label("MJ")
    ax.set_title(sub_label)
    add_static(ax)
    return


############################       RMSE       ##############################


def map_rmse(var, index, method, sub_label):
    ax = fig.add_subplot(3, 4, index, projection=cart_proj)
    vmin = np.percentile(df[f"rmse_{method}_pers"], 5)
    vmax_pers = np.percentile(df[f"rmse_{method}_pers"], 95)
    vmax_mlp = np.percentile(df[f"rmse_{method}_mlp"], 95)
    if vmax_pers > vmax_mlp:
        vmax = vmax_pers
    else:
        vmax = vmax_mlp
    ## plot wx stations locations
    sc = ax.scatter(
        df["lons"],
        df["lats"],
        c=df[var],
        vmin=0,
        vmax=vmax,
        cmap="GnBu",
        edgecolor="k",
        lw=0.5,
        zorder=10,
        alpha=1,
        s=df["obs_hours_scale"],
        transform=crs.PlateCarree(),
    )
    # Add a colorbar
    cbar = plt.colorbar(sc, ax=ax, orientation="horizontal", label="Value", pad=0.01)
    if method == "avg":
        cbar.set_label("MW")
    else:
        cbar.set_label("MJ")
    ax.set_title(sub_label)
    add_static(ax)
    return


##########################     R Square        #############################


def map_r2(var, index, sub_label):
    ax = fig.add_subplot(3, 4, index, projection=cart_proj)
    ## plot wx stations locations
    sc = ax.scatter(
        df["lons"],
        df["lats"],
        c=df[var],
        vmin=-1,
        vmax=1,
        cmap="PRGn",
        edgecolor="k",
        lw=0.5,
        zorder=10,
        alpha=1,
        s=df["obs_hours_scale"],
        transform=crs.PlateCarree(),
    )
    cbar = plt.colorbar(sc, ax=ax, orientation="horizontal", pad=0.01)
    cbar.set_label(r"$R^{2}$")
    ax.set_title(sub_label)
    add_static(ax)
    return


############################       DIFF       ##############################


def map_dif(var, index, method, sub_title, y_label):
    diff = df[f"{var}_{method}_mlp"] - df[f"{var}_{method}_pers"]
    vmin = abs(np.percentile(diff, 20))
    vmax = np.percentile(diff, 80)
    if vmin > vmax:
        vv = vmin
    else:
        vv = vmax

    if (var == "mae") | (var == "rmse"):
        cmap = "coolwarm_r"
    else:
        cmap = "coolwarm"
    if var == "r2":
        vv = 1
    if var == "r":
        vv = 0.5

    ax = fig.add_subplot(3, 4, index, projection=cart_proj)
    sc = ax.scatter(
        df["lons"],
        df["lats"],
        c=df[f"{var}_{method}_mlp"] - df[f"{var}_{method}_pers"],
        vmin=-vv,
        vmax=vv,
        cmap=cmap,
        edgecolor="k",
        lw=0.5,
        zorder=10,
        alpha=1,
        s=df["obs_hours_scale"],
        transform=crs.PlateCarree(),
    )
    cbar = plt.colorbar(sc, ax=ax, orientation="horizontal", pad=0.01)
    cbar.set_label(sub_title)
    add_static(ax)
    ax.text(
        x=-0.1,  # x-coordinate of the text (use negative values to push it outside the map)
        y=0.5,  # y-coordinate of the text (0.5 is centered vertically)
        s=y_label,  # The label text
        va="center",  # vertical alignment of the text
        ha="center",  # horizontal alignment of the text
        rotation="vertical",  # rotate the text vertically
        transform=ax.transAxes,  # use axis coordinates (0,0 bottom-left, 1,1 top-right)
    )
    return


# fig = plt.figure(figsize=(24, 12))
fig = plt.figure(figsize=(20, 14))
map_r("r_avg_mlp", 1, "Pearson's r", "MLP")
map_r("r_avg_pers", 5, "", "pers")
map_r2("r2_avg_mlp", 2, "R Squared")
map_r2("r2_avg_pers", 6, "")
map_mae("mae_avg_mlp", 3, "avg", "Mean Absolute Error")
map_mae("mae_avg_pers", 7, "avg", "")
map_rmse("rmse_avg_mlp", 4, "avg", "Root Mean Square Error")
map_rmse("rmse_avg_pers", 8, "avg", "")

map_dif("r", 9, "avg", "", "Difference")
map_dif("r2", 10, "avg", "", "")
map_dif("mae", 11, "avg", "MW", "")
map_dif("rmse", 12, "avg", "MW", "")


# Create a second legend for the sizes
# size_values = [9.85, 92.2, 184.5]
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

# ## save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-frp-stats-{method}.png",
    bbox_inches="tight",
    dpi=240,
)

# %%


fig = plt.figure(figsize=(20, 14))
map_r("r_sum_mlp", 1, "Pearson's r", "MLP")
map_r("r_sum_pers", 5, "", "pers")
map_r2("r2_sum_mlp", 2, "R Squared")
map_r2("r2_sum_pers", 6, "")
map_mae("mae_sum_mlp", 3, "sum", "Mean Absolute Error")
map_mae("mae_sum_pers", 7, "sum", "")
map_rmse("rmse_sum_mlp", 4, "sum", "Root Mean Square Error")
map_rmse("rmse_sum_pers", 8, "sum", "")

map_dif("r", 9, "sum", "", "Difference")
map_dif("r2", 10, "sum", "", "")
map_dif("mae", 11, "sum", "MJ", "")
map_dif("rmse", 12, "sum", "MJ", "")


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

## save as png
fig.savefig(
    str(data_dir) + f"/images/frp-paper/map-fre-stats-{method}.png",
    bbox_inches="tight",
    dpi=240,
)
# %%
