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

startTime = datetime.now()
# import dask
# from dask.distributed import Client
# client = Client(memory_limit='20GB',n_workers=3)
# client.close()
# ds = salem.open_xr_dataset("/bluesky/fireweather/fwf/data/fwf-data/fwf-daily-d03-2023073106.nc")

domain = 'd03'
doi = pd.Timestamp("2023-11-17")

filein = str(wrf_dir) + f'/{doi.strftime("%Y%m%d00")}/'
startTime = datetime.now()
print("begin readwrf: ", str(startTime))
pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))
if domain == "d02":
    pathlist = pathlist[6:61]
else:
    pathlist = pathlist[6:]


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
