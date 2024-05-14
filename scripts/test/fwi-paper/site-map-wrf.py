import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from mpl_toolkits.axes_grid1 import make_axes_locatable


from datetime import datetime, date, timedelta

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll


from context import data_dir, root_dir

matplotlib.rcParams.update({"font.size": 22})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)

startTime = datetime.now()

model = "wrf"
trail_name = "02"
wx_stations = False
fx_locs = True
wx_hourly = False
tzone = False
save_name = "blank"


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

### Open Fire Cases
with open(str(root_dir) + "/json/fire-cases.json") as f:
    cases = json.load(f)


### Open Station Data

try:
    wx_ds = xr.open_dataset(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/d03-20210101-20221231.nc",
    )
except:
    wx_ds = xr.open_dataset(
        str(data_dir) + f"/intercomp/{trail_name}/{model}/20210101-20221231.nc",
    )

wmo_idx = np.loadtxt(str(data_dir) + "/intercomp/02/wx_station.txt").astype(int)
wx_ds = wx_ds.sel(wmo=wmo_idx)

### Open WRF d01 domain


# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00")

# Get the sea level pressure
slp = getvar(ncfile, "slp")


# Get the latitude and longitude points
lats, lons = latlon_coords(slp)

# Get the cartopy mapping object
cart_proj = get_cartopy(slp)


wrf_d01 = salem.open_xr_dataset(str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00")


### Open WRF d02 domain
wrf_d02 = xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")
fwf_d02 = salem.open_xr_dataset(
    "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-daily-d02-2021081506.nc"
).isel(time=0)


### Open WRF d03 domain
wrf_d03 = xr.open_dataset(str(data_dir) + f"/static/static-vars-wrf-d03.nc")


## set plot title and save dir/name
Plot_Title = "Model Domains in Mercator Projection"
save_dir = str(data_dir)


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_shp",
    scale="50m",
    facecolor="none",
)


# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)


if wx_stations == True:
    save_name = "wx-stations"
    xx, yy = wx_ds.lons, wx_ds.lats
    ## plot wx stations locations
    ax.scatter(
        xx,
        yy,
        color="tab:grey",
        zorder=10,
        alpha=1,
        s=4,
        label="WxStations",
        transform=crs.PlateCarree(),
    )

if fx_locs == True:
    save_name = "fx_locs"
    xx, yy = [], []
    for case in cases:
        yy.append(cases[case]["min_lat"])
        xx.append(cases[case]["min_lon"])

    # xx, yy = xx, yy)
    ## plot wx stations locations
    ax.scatter(
        xx,
        yy,
        color="tab:orange",
        zorder=10,
        alpha=1,
        marker="v",
        edgecolors="k",
        lw=1.5,
        s=200,
        label="WildFires",
        transform=crs.PlateCarree(),
    )


## get d03 lats and lon
linewidth = 2.6
lons, lats = np.array(wrf_d03.XLONG), np.array(wrf_d03.XLAT)
xx, yy = lons[0], lats[0]
ax.plot(
    xx,
    yy,
    color="tab:green",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=crs.PlateCarree(),
)
xx, yy = lons[-1].T, lats[-1].T
ax.plot(
    xx,
    yy,
    color="tab:green",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=crs.PlateCarree(),
)
xx, yy = lons[:, 0], lats[:, 0]
ax.plot(
    xx,
    yy,
    color="tab:green",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=crs.PlateCarree(),
)
xx, yy = lons[:, -1].T, lats[:, -1].T

ax.plot(
    xx,
    yy,
    color="tab:green",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    label="WRF 4 km",
    transform=crs.PlateCarree(),
)


## get d02 lats and lon
linewidth = 2.6
lons, lats = np.array(wrf_d02.XLONG), np.array(wrf_d02.XLAT)
xx, yy = lons[0], lats[0]
ax.plot(
    xx,
    yy,
    color="tab:red",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=crs.PlateCarree(),
)
xx, yy = lons[-1].T, lats[-1].T
ax.plot(
    xx,
    yy,
    color="tab:red",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=crs.PlateCarree(),
)
xx, yy = lons[:, 0], lats[:, 0]
ax.plot(
    xx,
    yy,
    color="tab:red",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=crs.PlateCarree(),
)
xx, yy = lons[:, -1].T, lats[:, -1].T
ax.plot(
    xx,
    yy,
    color="tab:red",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    label="WRF 12 km",
    transform=crs.PlateCarree(),
)

## get d01 lats and lon
linewidth = 2.6
lons, lats = np.array(wrf_d01.XLONG)[0], np.array(wrf_d01.XLAT)[0]
xx, yy = lons[0], lats[0]
ax.plot(
    xx,
    yy,
    color="tab:blue",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=ccrs.Geodetic(),
)
xx, yy = lons[-1].T, lats[-1].T
ax.plot(
    xx,
    yy,
    color="tab:blue",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=ccrs.Geodetic(),
)
xx, yy = lons[:, 0], lats[:, 0]
ax.plot(
    xx,
    yy,
    color="tab:blue",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    transform=ccrs.Geodetic(),
)
xx, yy = lons[:, -1].T, lats[:, -1].T


ax.plot(
    xx,
    yy,
    color="tab:blue",
    linewidth=linewidth,
    zorder=8,
    alpha=1,
    label="WRF 36 km",
    transform=ccrs.Geodetic(),
)

from matplotlib.ticker import MaxNLocator


if tzone == True:
    save_name = "tzone"
    wrf_d02["ZoneST"] = wrf_d02["ZoneST"].astype(int)
    wrf_d02["ZoneST"] = (
        ("south_north", "west_east"),
        np.where(
            (wrf_d02["ZoneST"] == 0) | (wrf_d02["ZoneST"] == 3),
            np.nan,
            wrf_d02["ZoneST"],
        ),
    )
    wrf_d02["ZoneST"].attrs = wrf_d02.attrs
    clb = ax.contourf(
        wrf_d02["XLONG"],
        wrf_d02["XLAT"],
        wrf_d02["ZoneST"],
        cmap="Pastel1",
        levels=np.arange(2, 11, 1),
        extend="neither",
        transform=crs.PlateCarree(),
        zorder=1,
    )
    cb_ctt = fig.colorbar(clb, ax=ax, pad=0.01)
    cb_ctt.set_label("UTC Offset", rotation=90)

if wx_hourly == True:
    save_name = "wx_hourly"
    var = "H"
    fwf_d02[var] = (
        ("south_north", "west_east"),
        np.where(wrf_d02["ZoneST"] == 0, np.nan, fwf_d02[var]),
    )
    fwf_d02[var].attrs = wrf_d02.attrs
    cmaps[var]
    try:
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "wxbell", cmaps[var]["colors18"], N=len(cmaps[var]["levels"])
        )
    except:
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
            "wxbell", cmaps[var]["colors"], N=len(cmaps[var]["levels"])
        )
    # fwf_d02[var].salem.quick_map(countries=False, cmap = cmap, levels = cmaps[var]['levels'][:-1], vmin = cmaps[var]['vmin'],vmax = cmaps[var]['vmax'])
    clb = ax.contourf(
        fwf_d02["XLONG"],
        fwf_d02["XLAT"],
        fwf_d02[var],
        cmap=cmap,
        levels=cmaps[var]["levels"][:-1],
        vmin=cmaps[var]["vmin"],
        vmax=cmaps[var]["vmax"],
        transform=crs.PlateCarree(),
        zorder=1,
    )
    cb_ctt = fig.colorbar(clb, ax=ax, pad=0.01)
    cb_ctt.set_label("Relative Humidity" + r"(\%)", rotation=90)

ax.set_title("")


## add legend
ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, 1.11),
    ncol=5,
    fancybox=True,
    shadow=True,
)


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


# save as png
fig.savefig(
    f"/Users/crodell/ams-fwf/LaTeX/img/fwf/study-map-{save_name}.png",
    bbox_inches="tight",
    dpi=240,
)
fig.savefig(
    f"/Users/crodell/ams-fwf/LaTeX/img/fwf/study-map-{save_name}.pdf",
    bbox_inches="tight",
    dpi=240,
)
plt.close()
