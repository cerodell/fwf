import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import scipy.stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
import plotly.express as px

from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter
from pylab import *

from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText

import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

wrf_model = "wrf4"
method = "interp"
models = [f"_era5_{method}", f"_day1_{method}"]
model = f"_day1_{method}"
domain = "d02"
# date = pd.Timestamp("today")
# date = pd.Timestamp(2022, 7, 30)
date = pd.Timestamp(2021, 11, 1)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/d02/ERA5WRF01/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
# )
ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)
ds = ds.load()
ds = ds.sel(time=slice("2021-04-01", "2021-11-01"))


# ds_bc = ds.where(ds['wmo'][ds.prov == 'BC'])
# ds_bc.dropna(dim = 'wmo', how='any', thresh=None, subset=None)
# wmo_100 = ds_bc.mean(dim = 'wmo')

wmo_100 = ds.sel(wmo=71765)

fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
for var in fwi_list:
    fig = plt.figure(figsize=(8, 4))  # (Width, height) in inches.
    fig.autofmt_xdate()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(wmo_100.time, wmo_100[var], lw=2, label="Observed")
    ax.plot(wmo_100.time, wmo_100[f"{var}_wrf01"], lw=2, label="Modeled")
    xfmt = DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(xfmt)
    ax.set_xlabel("Time (HH:MM)", fontsize=14)
    ax.set_ylabel(var.upper(), fontsize=14)
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.xaxis.grid(color="gray", linestyle="dashed")
    ax.yaxis.grid(color="gray", linestyle="dashed")
    ax.legend(
        loc="upper right",
        # bbox_to_anchor=(0.48, 1.15),
        ncol=1,
        fancybox=True,
        shadow=True,
    )
    fig.tight_layout()

met_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
for var in met_list:
    ############################################################
    fig = plt.figure(figsize=(8, 4))  # (Width, height) in inches.
    fig.autofmt_xdate()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(wmo_100.time, wmo_100[var], lw=2, label="Observed")
    ax.plot(wmo_100.time, wmo_100[f"{var}_wrf01"], lw=2, label="Modeled")
    xfmt = DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(xfmt)
    ax.set_xlabel("Time (HH:MM)", fontsize=14)
    ax.set_ylabel(var.upper(), fontsize=14)
    ax.tick_params(axis="both", which="major", labelsize=13)
    ax.xaxis.grid(color="gray", linestyle="dashed")
    ax.yaxis.grid(color="gray", linestyle="dashed")
    ax.legend(
        loc="upper right",
        # bbox_to_anchor=(0.48, 1.15),
        ncol=1,
        fancybox=True,
        shadow=True,
    )
fig.tight_layout()

fig = plt.figure(figsize=(8, 4))  # (Width, height) in inches.
fig.autofmt_xdate()
ax = fig.add_subplot(1, 1, 1)

#
ax.plot(wmo_100.time, wmo_100[f"snowc"], lw=2, label="Modeled")
xfmt = DateFormatter("%m-%d")
ax.xaxis.set_major_formatter(xfmt)
ax.set_xlabel("Time (HH:MM)", fontsize=14)
ax.set_ylabel(var.upper(), fontsize=14)
ax.tick_params(axis="both", which="major", labelsize=13)
ax.xaxis.grid(color="gray", linestyle="dashed")
ax.yaxis.grid(color="gray", linestyle="dashed")
ax.legend(
    loc="upper right",
    # bbox_to_anchor=(0.48, 1.15),
    ncol=1,
    fancybox=True,
    shadow=True,
)
fig.tight_layout()
# ds = ds.sel(time=slice("2021-04-01", "2021-11-01"))
# ds = ds.sel(time=slice("2022-04-01", "2022-07-01"))

# date_range = pd.date_range(ds.time.values[0], ds.time.values[-1])
# ds = ds.chunk(chunks="auto")
# ds = ds.unify_chunks()
# for var in list(ds):
#     ds[var].encoding = {}

# if domain == "d02":
#     res = "12 km"
# else:
#     res = "4 km"

# df = ds.to_dataframe().dropna()
# df = df.reset_index()
# df = df[~np.isnan(df.bui)]
# df = df[~np.isnan(df[f"bui_day1_{method}"])]

# unique, counts = np.unique(df.wmo.values, return_counts=True)
# # wmo_of_int = unique[counts > 170]
# # df = df[df.wmo.isin(wmo_of_int)]
# # unique, counts = np.unique(df.wmo.values, return_counts=True)
