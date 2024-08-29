import context
import salem
import json
import math

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
import string

from context import data_dir, wrf_dir
from datetime import datetime, date, timedelta

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors

from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm


startTime = datetime.now()
# import dask
# from dask.distributed import Client
# client = Client(memory_limit='20GB',n_workers=3)
# client.close()
static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")

ds = salem.open_xr_dataset(str(data_dir) + "/fwf-data/fwf-hourly-d02-2024061906.nc")


ds = xr.where(static_ds['LAND']==1,10000, ds)

for var in list(ds):
    ds[var].attrs = static_ds.attrs
# ds.attrs = static_ds.attrs


frp_i = ds.isel(time=18)

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(1, 1, 1)
var = "FRP"
# vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
# levels = cmaps[var]["levels"]
vmin, vmax = 0, 3000
levels = [0,15,50,100,150,200,250,300,400,500,600,700,1000,1400,1800,2200,2500,3000]
# title, colors = str(cmaps[var]["title"]), cmaps[var]["colors"]
# custom_cmap = LinearSegmentedColormap.from_list(
#     "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
# )
colors = np.vstack(
    ([1, 1, 1, 1], plt.get_cmap("inferno")(np.linspace(0, 1, 256)))
)  # Add white at the start
custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)

custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', ['#FFFFFF','#FFFF32', '#db6400', '#9f0000'])


norm = BoundaryNorm(levels, custom_cmap.N)
frp_i[var].attrs["units"] = ""
frp_i[var].salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm,extend='max')
ax.set_title(f"Fire Radiative Power (MW) \n")


# model = "wrf"
# domain = "d02"/0
# date_range = pd.date_range("2023-05-15", "2023-05-15")

# # static_ds = salem.open_xr_dataset('/bluesky/fireweather/fwf/data/fwf-data/fwf-daily-d03-2023051506.nc')

# for domain in ['d02', 'd03']:
#   static_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
#   # tzone = static_ds["ZoneST"].values
#   # masked_arr = np.ma.masked_where(static_ds["LAND"] == 1, static_ds["LAND"])

#   for doi in date_range:
#     ds = xr.open_dataset(str(data_dir) + f'/fwf-data/fwf-daily-{domain}-{doi.strftime("%Y%m%d06")}.nc')
#     ds['south_north'] = static_ds['south_north']
#     ds['west_east'] = static_ds['west_east']
#     ds.to_netcdf(f'/bluesky/archive/fireweather/data/fwf-daily-{domain}-{doi.strftime("%Y%m%d06")}.nc', mode = 'w')

#     ds = xr.open_dataset(str(data_dir) + f'/fwf-data/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')
#     ds['south_north'] = static_ds['south_north']
#     ds['west_east'] = static_ds['west_east']
#     ds.to_netcdf(f'/bluesky/archive/fireweather/data/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc', mode = 'w')

# # var = 'mSt'
# # masked_array = ds[var].to_masked_array()
# # masked_array.mask = masked_arr.mask
# # ds[var] = (("south_north", "west_east"), masked_array)
# # ds[var] = ds[var] - 12
# # ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
# # ds[var].attrs["units"] = "Hours"
# # ds[var].salem.quick_map(vmin= -12, vmax =12, cmap = 'coolwarm')
