#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
/bluesky/bsf-ops/modules/HYSPLIT/v7/
Creates geojson files for each fwf forecast prodcut. Used as intermediate step for dispaly on leaflet map.
NOTE: The geojson file get post processed to topojson for use on leaflet.
      The node_module geo2topo in topojson-server handles convertion

"""
import context
import sys
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from utils.geoutils import mask, mycontourf_to_geojson
from scipy.ndimage import gaussian_filter
import scipy.ndimage as ndimage

from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt
import matplotlib.colors

startTime = datetime.now()

from context import data_dir, root_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


### make folder for json files on webapge
forecast_date = pd.Timestamp("2020-06-14").strftime("%Y%m%d%H")


### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

### Open nested index json
with open(str(root_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)


config = dict(
    model="ecmwf",
    domain="era5",
    trail_name="01",
    root_dir="/Volumes/WFRT-Ext24/fwf-data",
)


daily_file_dir = (
    str(config["root_dir"])
    + f"/{config['model']}/{config['domain']}/{config['trail_name']}/fwf-daily-{config['domain']}-{forecast_date}.nc"
)

daily_ds = salem.open_xr_dataset(daily_file_dir)
daily_ds = daily_ds.load()


var = "T"
daily_ds[var] = xr.where(
    daily_ds[var] < cmaps[var]["vmax"],
    daily_ds[var],
    int(cmaps[var]["vmax"] + 1),
)
da = daily_ds[var].isel(time=0).round(0)

# ## Get first timestamp of forecast and make dir to store files
timestamp = np.array(daily_ds.Time.dt.strftime("%Y%m%d"))
folderdate = timestamp


vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
name, colors, sigma = (
    str(cmaps[var]["name"]),
    cmaps[var]["colors"],
    cmaps[var]["sigma"],
)

geojson_filename = str(name + "-" + timestamp + "-" + config["domain"])
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
plt.close()

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

# ### Timer
print("Run Time: ", datetime.now() - startTime)
