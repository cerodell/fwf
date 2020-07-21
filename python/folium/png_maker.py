import context
import math
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from netCDF4 import Dataset

from datetime import datetime, date, timedelta
startTime = datetime.now()

from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir

"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
from wrf import  ll_to_xy

lat, lon = 49.083, -116.5

wrf_file_dir = str(data_dir) + "/wrf/lat_lon.nc"
wrf_file = Dataset(wrf_file_dir,'r')

xy_np  = np.array(ll_to_xy(wrf_file, lat, lon))


hourly_file_dir  = str(xr_dir) + "/current/hourly.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = str(xr_dir) + "/current/daily.zarr"
daily_ds = xr.open_zarr(daily_file_dir)


day  = str(np.array(hourly_ds.Time[0], dtype ='datetime64[D]'))
center_lon = float(hourly_ds.CEN_LON)

lat_max = print(np.nanmax(hourly_ds.XLAT))
lat_min = print(np.nanmin(hourly_ds.XLAT))

lat_max = print(np.nanmax(hourly_ds.XLONG))
lat_min = print(np.nanmin(hourly_ds.XLONG))





vmin , vmax = 70, 100


proj_ = ccrs.NorthPolarStereo(central_longitude=center_lon)

lat, lon, ffmc = np.array(hourly_ds.XLONG), np.array(hourly_ds.XLAT), np.array(hourly_ds.F[18])

fig = plt.figure()
ax = fig.gca(projection=proj_)
contourf = ax.pcolormesh(lat, lon, ffmc,\
                             vmin = vmin, vmax = vmax, transform = ccrs.Mercator())

ax.set_xlim(40,63.5)
ax.set_ylim(-140,-61)
    
    # plt.show()
fig.savefig(f"/bluesky/archive/fireweather/test/static/images/{day}.png", transparent=True)

# ### Timer
print("Run Time: ", datetime.now() - startTime)