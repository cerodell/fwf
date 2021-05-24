import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.make_intercomp import daily_merge_ds
from pylab import *

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter
import matplotlib.ticker as mticker


from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_dir
from datetime import datetime, date, timedelta


date = pd.Timestamp(2021, 5, 21)
forecast_date = date.strftime("%Y%m%d06")
domain = "d02"
wrf_model = "wrf4"


### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


file_dir = str(fwf_dir) + f"/fwf-hourly-{domain}-{forecast_date}.nc"
ds = xr.open_dataset(file_dir)
ds = ds.isel(time=14)
day_hour = np.datetime_as_string(ds.Time, unit="h")
day = day_hour.replace("-", "")

### Open nested index json
with open(str(data_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)


y1, y2, x1, x2 = (
    nested_index["y1_" + domain],
    nested_index["y2_" + domain],
    nested_index["x1_" + domain],
    nested_index["x2_" + domain],
)
x1, x2 = 40, 8
shape = ds.XLAT.shape
I = np.arange(y1, shape[0] - y2)
J = np.arange(x1, shape[1] - x2)
ds = ds.isel(south_north=I, west_east=J)


var_list = ["HFI", "ROS", "CFB", "SFC", "TFC"]

for var in var_list:
    vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
    name, colors, sigma, levels = (
        str(cmaps[var]["name"]),
        cmaps[var]["colors"],
        cmaps[var]["sigma"],
        cmaps[var]["levels"],
    )

    if var == "CFB":
        fillarray = ds[var].values * 100
    else:
        fillarray = ds[var].values
    fillarray = np.round(fillarray, 0)
    fillarray = ndimage.gaussian_filter(fillarray, sigma=sigma)
    Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
    save_file = f"/images/fbp/{var}-{wrf_model}-{domain}-{day}.png"
    save_dir = str(data_dir) + save_file

    ## bring in state/prov boundaries
    states_provinces = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none",
    )

    ## bring in state/prov boundaries
    states_provinces = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none",
    )

    proj = ccrs.PlateCarree(central_longitude=0)
    ## make fig for make with projection
    fig = plt.figure(figsize=[16, 8])
    ax = fig.add_subplot(1, 1, 1, projection=proj)

    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

    ## add map features
    gl = ax.gridlines(
        draw_labels=True,
        crs=ccrs.PlateCarree(),
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
        zorder=10,
    )
    gl.top_labels = gl.right_labels = False
    gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 10)))
    ax.add_feature(cfeature.LAND, zorder=1)
    ax.add_feature(cfeature.LAKES, zorder=9)
    ax.add_feature(cfeature.OCEAN, zorder=9)
    ax.add_feature(cfeature.BORDERS, zorder=9)
    ax.add_feature(cfeature.COASTLINE, zorder=9)
    ax.add_feature(states_provinces, edgecolor="k", zorder=9, lw=0.5)
    ax.set_xlabel("Longitude", fontsize=18)
    ax.set_ylabel("Latitude", fontsize=18)
    ax.tick_params(axis="both", which="major", labelsize=14)
    ax.tick_params(axis="both", which="minor", labelsize=14)

    ## add title and adjust subplot buffers
    if domain == "d02":
        res = "12 km"
    elif domain == "d03":
        res = "4 km"
    else:
        res = ""

    ## add title and adjust subplot buffers
    Plot_Title = f"{var} at {day_hour} \n {wrf_model} {res}"
    ax.set_title(Plot_Title, fontsize=20, weight="bold")

    Cnorm = matplotlib.colors.Normalize(
        vmin=int(np.min(levels)), vmax=int(np.max(levels))
    )
    contourf = ax.contourf(
        ds.XLONG,
        ds.XLAT,
        fillarray,
        levels=levels,
        extend="max",
        colors=colors,
        norm=Cnorm,
        zorder=4,
        alpha=1,
    )

    fig.add_axes(ax_cb)
    cbar = plt.colorbar(contourf, cax=ax_cb)

    ## set map bounds
    if wrf_model == "wrf3":
        ax.set_xlim([-140, -60])
        ax.set_ylim([36, 70])
    elif wrf_model == "wrf4":
        ax.set_xlim([-174, -30])
        ax.set_ylim([25, 80])
    else:
        pass

    fig.savefig(save_dir, dpi=240)
    plt.close()
