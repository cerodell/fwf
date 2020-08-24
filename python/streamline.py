import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from utils.geoutils import mask, mycontourf_to_geojson
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()


import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES)

import warnings
warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")


### Open color map json
with open('/bluesky/fireweather/fwf/json/dev_colormaps.json') as f:
  cmaps = json.load(f)

### BRing in zarr FWF forecast data 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
# hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020071700.zarr") 
# daily_file_dir = str(xr_dir) + str("/fwf-daily-2020071700.zarr")
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)



wsp = hourly_ds.W.values
wsp = wsp[:,:,50:1210]

wdir = hourly_ds.WD.values
wdir = wdir[:,:,50:1210]

u = -abs(wsp) * np.sin(np.pi*180/wdir)
v = -abs(wsp) * np.cos(np.pi*180/wdir)

day = np.array(daily_ds.Time.dt.strftime('%Y-%m-%d'))


xlat = np.round(daily_ds.XLAT.values,5)
xlat= xlat[:,50:1210]
# xlat = np.array(xlat, dtype = '<U8')

xlong = np.round(daily_ds.XLONG.values,5)
xlong= xlong[:,50:1210]







# fwf = {
#         'u': u.tolist(),
#         'v': v.tolist(),
#         'xlats': xlats.tolist(),
#         'xlong': xlong.tolist(),
#         'Time': time.tolist()
# }


