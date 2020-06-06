import context
import math
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from datetime import datetime, date, timedelta
startTime = datetime.now()

from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir,leaflet_dir, xr_dir

"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
# yesterday = date.today() - timedelta(days=1)
# zarr_filein = yesterday.strftime('%Y-%m-%dT00.zarr')
# zarr_filein = "2019-08-20T00_hourly_ds.zarr"
# hourly_file_dir = str(xr_dir) + str("/hourly/") + zarr_filein

##### Personal Comp path 
zarr_filein = "2019-08-20T00_hourly_ds.zarr"
hourly_file_dir = str(data_dir) + str("/xr/") + zarr_filein


ds = xr.open_zarr(hourly_file_dir)
lats, lons = ds.XLAT, ds.XLONG


center_lon = float(ds.CEN_LON)

# levels = np.arange(70,101,1)
vmin , vmax = 70, 100


proj_ = ccrs.NorthPolarStereo(central_longitude=center_lon)

lat, lon, ffmc = np.array(lons), np.array(lats), np.array(ds.F[18])

fig = plt.figure()
ax = fig.gca(projection=proj_)
contourf = ax.pcolormesh(lat, lon, ffmc,\
                             vmin = vmin, vmax = vmax, transform = ccrs.PlateCarree())

# plt.show()
fig.savefig("/Users/rodell/fwf/Images/test.png", transparent=True)

# fig.savefig("/bluesky/fireweather/fwf/Images/test.png")
# ### Timer
print("Run Time: ", datetime.now() - startTime)