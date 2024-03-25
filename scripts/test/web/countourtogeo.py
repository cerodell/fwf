#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import salem
import json
import numpy as np
import xarray as xr
import geojsoncontour
import pandas as pd
import geopandas as gpd
from pathlib import Path
from netCDF4 import Dataset
import branca.colormap as cm
import scipy.ndimage as ndimage
from scipy.ndimage import gaussian_filter
from sklearn.neighbors import KDTree

import matplotlib.pyplot as plt
import matplotlib.colors

from datetime import datetime, date, timedelta

from wrf import getvar
from context import data_dir, root_dir


forecast_date = pd.Timestamp(2021, 2, 9)
var = "S"
domain = "d02"
### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


ds = xr.open_dataset(
    f'/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/04/fwf-hourly-{domain}-{forecast_date.strftime("%Y%m%d06")}.nc'
)

da = ds[var].isel(time=0)
timestamp = pd.Timestamp(da.Time.values).strftime("%Y%m%d%H")
vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
name, colors, sigma = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors18"],
    cmaps[var]["sigma"],
)

geojson_filename = str(name + "-" + timestamp + "-" + domain)
levels = cmaps[var]["levels"]
Cnorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax + 1)
contourf = plt.contourf(
    da.XLONG.values,
    da.XLAT.values,
    ndimage.gaussian_filter(da.values, sigma=sigma),
    levels=levels,
    linestyles="None",
    norm=Cnorm,
    colors=colors,
    extend="both",
)
plt.show()

geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    min_angle_deg=None,
    ndigits=2,
    stroke_width=None,
    fill_opacity=None,
    geojson_properties=None,
    unit="",
    geojson_filepath=str(data_dir) + f"/geojson/{geojson_filename}.geojson",
)
