import context
import salem
import json
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

import matplotlib.pyplot as plt
import matplotlib.colors

from datetime import datetime, timedelta
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from netCDF4 import Dataset

from context import data_dir, root_dir


doi = "2023071006"
domain = "d02"
var = "S"


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


vmin, vmax = 0, 1

name, colors, sigma = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors18"],
    cmaps[var]["sigma"],
)
# levels = cmaps[var]["levels"]
levels = np.arange(0, 1.1, 0.1)
Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)

doi_daily_ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/fwf-daily-{domain}-{doi}.nc"
)["S"].isel(time=0)
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
doi_daily_ds["south_north"] = static_ds["south_north"]
doi_daily_ds["west_east"] = static_ds["west_east"]

daily_ds = xr.open_dataset(str(data_dir) + f"/norm/fwi-daily-{domain}.nc")

nomr_ds = (doi_daily_ds - daily_ds["S_min"]) / (daily_ds["S_max"] - daily_ds["S_min"])
nomr_ds["Time"] = doi_daily_ds["Time"]
static_ds["S_norm"] = nomr_ds
static_ds["S_norm"].attrs = static_ds.attrs

fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(1, 1, 1)
static_ds["S_norm"].salem.quick_map(
    prov=True, states=True, oceans=True, vmax=0.75, vmin=vmin, cmap="jet", ax=ax
)
plt.savefig(
    str(data_dir) + f"/images/norm/fwf-{doi}-norm.png",
    dpi=250,
    bbox_inches="tight",
)

fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot(1, 1, 1)
doi_daily_ds.salem.quick_map(
    prov=True, states=True, oceans=True, cmap="jet", vmax=30, ax=ax
)
plt.savefig(
    str(data_dir) + f"/images/norm/fwf-{doi}.png",
    dpi=250,
    bbox_inches="tight",
)


# static_ds['S'] = houlry_ds['S_max']
# static_ds['S'].attrs = static_ds.attrs
# static_ds['S'].salem.quick_map()
# static_ds['S_max_daily'] = (daily_ds['S_max']- houlry_ds['S_max'])
# static_ds['S_max_daily'].attrs = static_ds.attrs
# static_ds['S_max_daily'].salem.quick_map(vmin = -20, vmax = 20, cmap ='coolwarm', prov = True, states= True, oceans =True)

# doi_daily_ds =salem.open_xr_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/fwf-hourly-{domain}-2023081706.nc")['S'].isel(time = 0)
# doi_daily_ds.salem.quick_map(prov = True, states= True, oceans =True, vmax = 40)
