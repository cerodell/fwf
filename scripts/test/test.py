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

from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()




model = "wrf"
domain = "d02"
date_range = pd.date_range("2023-05-15", "2023-05-15")

# static_ds = salem.open_xr_dataset('/bluesky/fireweather/fwf/data/fwf-data/fwf-daily-d03-2023051506.nc')

for domain in ['d02', 'd03']:
  static_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
  # tzone = static_ds["ZoneST"].values
  # masked_arr = np.ma.masked_where(static_ds["LAND"] == 1, static_ds["LAND"])

  for doi in date_range:
    ds = xr.open_dataset(str(data_dir) + f'/fwf-data/fwf-daily-{domain}-{doi.strftime("%Y%m%d06")}.nc')
    ds['south_north'] = static_ds['south_north']
    ds['west_east'] = static_ds['west_east']
    ds.to_netcdf(f'/bluesky/archive/fireweather/data/fwf-daily-{domain}-{doi.strftime("%Y%m%d06")}.nc', mode = 'w')

    ds = xr.open_dataset(str(data_dir) + f'/fwf-data/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc')
    ds['south_north'] = static_ds['south_north']
    ds['west_east'] = static_ds['west_east']
    ds.to_netcdf(f'/bluesky/archive/fireweather/data/fwf-hourly-{domain}-{doi.strftime("%Y%m%d06")}.nc', mode = 'w')

# var = 'mSt'
# masked_array = ds[var].to_masked_array()
# masked_array.mask = masked_arr.mask
# ds[var] = (("south_north", "west_east"), masked_array)
# ds[var] = ds[var] - 12
# ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
# ds[var].attrs["units"] = "Hours"
# ds[var].salem.quick_map(vmin= -12, vmax =12, cmap = 'coolwarm')
