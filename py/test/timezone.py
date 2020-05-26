import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from fwi.utils.wrf.read_wrfout import readwrf
from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir
import timezonefinder, pytz
from datetime import datetime
from pathlib import Path


folder = "/2019-08-19T00_ds_wrf.zarr"
ds_wrf_file = str(xr_dir) + folder
ds_wrf = xr.open_zarr(ds_wrf_file)

folder = "/ds_zone.zarr"
ds_zone_file = str(xr_dir) + folder
ds_zone = xr.open_zarr(ds_zone_file)




# shape = ds_wrf.T.shape
# shape = shape[1:]
# print(shape, "SHAPE")
# # i,j = 0, -1
# # Lat = float(ds_wrf.XLAT[i,j])
# # print(Lat, "lat")
# # Long = float(ds_wrf.XLONG[i,j])
# # print(Long, "long")

# tf = timezonefinder.TimezoneFinder()


# def mytimezone(Lat,Long):
#     timezone_str = tf.closest_timezone_at(lat=Lat, lng=Long, delta_degree=5)
#     common_name = pytz.timezone(timezone_str)
#     abbr = common_name.localize(datetime.now(), is_dst=None)
#     zone_abbr = abbr.tzname()
#     if zone_abbr is None:
#         zone_abbr = np.NaN
#         print ("Could not determine the time zone")
#     elif zone_abbr == "AKDT":
#         zone_abbr = 8
#     elif zone_abbr == "AKST":
#         zone_abbr = 8
#     elif zone_abbr == "PDT":
#         zone_abbr = 7
#     elif zone_abbr == "PST":
#         zone_abbr = 7
#     elif zone_abbr == "MDT":
#         zone_abbr = 6
#     elif zone_abbr == "MST":
#         zone_abbr = 6
#     elif zone_abbr == "CDT":
#         zone_abbr = 5
#     elif zone_abbr == "CST":
#         zone_abbr = 5
#     elif zone_abbr == "EDT":
#         zone_abbr = 4
#     elif zone_abbr == "EST":
#         zone_abbr = 4
#     elif zone_abbr == "ADT":
#         zone_abbr = 3
#     elif zone_abbr == "AST":
#         zone_abbr = 3
#     elif zone_abbr == "NDT":
#         zone_abbr = 3
#     elif zone_abbr == "NST":
#         zone_abbr = 3
#     else:
#         pass
#     return zone_abbr


# i_list = []
# for i in range(shape[0]):
#     print(f"{i} I of shape {shape[0]}" )
#     j_list = []
#     for j in range(shape[1]):
#         Lat = float(ds_wrf.XLAT[i,j])
#         Long = float(ds_wrf.XLONG[i,j])
#         # print(f"{Lat},{Long}")
#         timezone_str = mytimezone(Lat,Long)
#         j_list.append(timezone_str)
#     i_list.append(j_list)

# timezone_array = np.stack(i_list)


# make_dir = Path(str(xr_dir) + str('/') +  str(f"ds_zone.zarr"))

# da_zone = xr.DataArray(timezone_array, name='Zone', dims=('south_north', 'west_east'))
# ds_zone = xr.Dataset()

# # ds = xr.Dataset({})
# ds_zone['Zone'] = (('south_north', 'west_east'), da_zone)
# make_dir.mkdir(parents=True, exist_ok=True)

# ds_zone.compute()
# ds_zone.to_zarr(make_dir, "w")


# # print(ds_zone)

