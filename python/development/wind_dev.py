#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import json
import numpy as np
import xarray as xr
import geojsoncontour
import mplleaflet

from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from dev_geoutils import mask, mycontourf_to_geojson
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import data_dir, xr_dir, wrf_dir, root_dir

import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")


### Open color map json
with open('/bluesky/fireweather/fwf/json/dev_colormaps.json') as f:
  cmaps = json.load(f)


### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

### Open datasets
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

wsp = hourly_ds.W.values
wsp = wsp[18, ::4,::4]

wdir = hourly_ds.WD.values
wdir = wdir[18, ::4,::4]

u = -abs(wsp) * np.sin(np.pi*180/wdir)
v = -abs(wsp) * np.cos(np.pi*180/wdir)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
lats, lons = lats[::4,::4], lons[::4,::4]

# var = 'T'
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# name, colors = str(cmaps[var]["name"]), cmaps[var]["colors18"]
# levels = cmaps[var]["levels"]
# title = cmaps[var]["title"]
# Cnorm = matplotlib.colors.Normalize(vmin= vmin, vmax =vmax+1)

Plot_Title = "Wind Direction Test"
day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
fig, ax = plt.subplots()
fig.suptitle(Plot_Title + day, fontsize=16)
fig.subplots_adjust(hspace=0.8)


q = ax.quiver(lons, lats, u, v, scale=10, color='white')
mplleaflet.display(fig=fig, tiles='esri_aerial')

js = mplleaflet.fig_to_geojson(fig=fig)
with open(str(data_dir) + "/json/test.json", "w") as outfile:
    json.dump(js, outfile, indent=4)