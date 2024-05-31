#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker


from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


# Mark the start time for the run
startTime = datetime.now()


sum_df = pd.read_csv(
    "/Users/crodell/fwf/data/ml-data/test-data/sum-averaged-v2.csv"
).dropna()

avg_df = pd.read_csv(
    "/Users/crodell/fwf/data/ml-data/test-data/avg-averaged-v2.csv"
).dropna()


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


def plot_stats(df, method):
    lat, lon, pearson_r, mbe, rmse = [], [], [], [], []
    for ID, group in df.groupby("id"):
        lat.append(float(group["lat"].iloc[0]))
        lon.append(float(group["lon"].iloc[0]))
        pearson_r.append(
            np.round(stats.pearsonr(group["FRP"], group["MODELED_FRP"])[0], 2)
        )
        mbe.append(np.round(MBE(group["FRP"], group["MODELED_FRP"]), 2))
        rmse.append(np.round(RMSE(group["FRP"], group["MODELED_FRP"]), 2))
    # Create a figure
    fig = plt.figure(figsize=(14, 8))
    # Set the GeoAxes to the projection used by WRF
    ax = plt.axes(projection=cart_proj)

    ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
    ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
    ax.coastlines("50m", linewidth=0.8, zorder=5)

    ## plot wx stations locations
    sc = ax.scatter(
        lon,
        lat,
        c=pearson_r,
        cmap="viridis",
        vmin=0,
        vmax=1,
        zorder=10,
        alpha=1,
        s=100,
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

    plt.tight_layout()

    ax.set_title(f"Pearson's r for the {len(lon)} wildfire test cases")

    # save as png
    fig.savefig(
        str(data_dir) + f"/images/frp-paper/map-pearsonr-{method}.png",
        bbox_inches="tight",
        dpi=240,
    )

    ############################################################################
    ############################################################################
    ############################################################################

    # Create a figure
    fig = plt.figure(figsize=(14, 8))
    # Set the GeoAxes to the projection used by WRF
    ax = plt.axes(projection=cart_proj)

    ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
    ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
    ax.coastlines("50m", linewidth=0.8, zorder=5)

    vmin = np.percentile(mbe, 5)
    vmax = np.percentile(mbe, 95)
    vm = abs(vmax - abs(vmin))
    ## plot wx stations locations
    sc = ax.scatter(
        lon,
        lat,
        c=mbe,
        cmap="coolwarm",
        vmin=-vm,
        vmax=vm,
        zorder=10,
        alpha=1,
        s=100,
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

    plt.tight_layout()

    ax.set_title(f"Mean Bias Error for the {len(lon)} wildfire test cases")

    # save as png
    fig.savefig(
        str(data_dir) + f"/images/frp-paper/map-mbe-{method}.png",
        bbox_inches="tight",
        dpi=240,
    )

    ############################################################################
    ############################################################################
    ############################################################################
    # Create a figure
    fig = plt.figure(figsize=(14, 8))
    # Set the GeoAxes to the projection used by WRF
    ax = plt.axes(projection=cart_proj)

    ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
    ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
    ax.coastlines("50m", linewidth=0.8, zorder=5)

    vmin = np.percentile(rmse, 5)
    vmax = np.percentile(rmse, 95)
    ## plot wx stations locations
    sc = ax.scatter(
        lon,
        lat,
        c=rmse,
        vmin=0,
        vmax=vmax,
        cmap="viridis",
        zorder=10,
        alpha=1,
        s=100,
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

    plt.tight_layout()

    ax.set_title(f"Root mean square error for the {len(lon)} wildfire test cases")

    # save as png
    fig.savefig(
        str(data_dir) + f"/images/frp-paper/map-rmse-{method}.png",
        bbox_inches="tight",
        dpi=240,
    )


plot_stats(sum_df, method="sum")
plot_stats(avg_df, method="avg")


# plt.scatter(avg_df['MODELED_FRP'], avg_df['FRP'])


# plt.plot(avg_df['FRP'], color = 'k')
# plt.plot(avg_df['MODELED_FRP'], color = 'tab:red')
