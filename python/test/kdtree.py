import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()
from scipy.spatial import cKDTree


import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES, xy_to_ll,ll_to_xy)



### BRing in zarr FWF forecast data 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)


center_lon = float(hourly_ds.CEN_LON)
### Bring in WRF Data and open

# wrf_folder = date.today().strftime('/%y%m%d00/')
wrf_folder = '/20070100/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


wrf_file = Dataset(wrf_file_dir[-1],'r')
LANDMASK    = getvar(wrf_file, "LANDMASK")

lat, lon = 50.6745, -120.3273
xy = ll_to_xy(wrf_file, lat, lon)
print("x wrf: ", np.array(xy[0]))
print("y wrf: ", np.array(xy[1]))


points = list(zip(xlat.ravel(), xlong.ravel()))

# ----- search nearest grid point ----- #
gridTree = cKDTree(list(zip(xlat.ravel(), xlong.ravel())))
grid_shape = xlong.shape
# for stnname, stnloc in stns.items():
dist, inds = gridTree.query((lat, lon))
print(np.unravel_index(inds, grid_shape))
