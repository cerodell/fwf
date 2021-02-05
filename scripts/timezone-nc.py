#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Creates a time zone mask for each grid point in model domain.

NOTE: I hate this script, take hours to run by using lat/lng for
each gird in model and find offset from utc. There must be a better way to do this.......

Thankfully it only needs to be run once as its save mask as a netcdf file :)
"""

import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from context import data_dir, xr_dir, wrf_dir, tzone_dir, wrf_dir_new
import timezonefinder, pytz
from pathlib import Path
import matplotlib.pyplot as plt


from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


wrf_domain = "d03"
filein = f"/20121600/wrfout_{wrf_domain}_2020-12-18_05:00:00"
ds_wrf_file = str(wrf_dir_new) + filein
ds_wrf = xr.open_dataset(ds_wrf_file)


shape = ds_wrf.XLAT.shape
shape = shape[1:]
print(shape, "SHAPE")

tf = timezonefinder.TimezoneFinder()


def mytimezone(Lat, Long):
    timezone_str = tf.closest_timezone_at(lat=Lat, lng=Long, delta_degree=20)
    timezone = pytz.timezone(timezone_str)
    dt = datetime.utcnow()
    offset = timezone.utcoffset(dt)
    seconds = offset.total_seconds()
    hours = abs(int(seconds // 3600))
    return hours


XLAT = ds_wrf.XLAT.values
XLAT = XLAT[0, :, :]
XLAT = XLAT.flatten()


XLONG = ds_wrf.XLONG.values
XLONG = XLONG[0, :, :]
XLONG = XLONG.flatten()

loopTime = datetime.now()
hours_list = []
for i in range(len(XLONG)):
    hours = mytimezone(XLAT[i], XLONG[i])
    hours_list.append(hours)
    if i % shape[0] == 0:
        print(f"{i} of {len(XLONG)}")
        print("Lapsed Time: ", datetime.now() - loopTime)
        loopTime = datetime.now()

hours_array = np.array(hours_list)
timezone_array = np.reshape(hours_array, shape)


ds_zone = xr.DataArray(timezone_array, name="Zone", dims=("south_north", "west_east"))
make_dir = Path(str(tzone_dir) + str("/") + str(f"tzone_wrf_{wrf_domain}.nc"))

ds_zone.compute()
ds_zone.to_netcdf(make_dir, "w")
### Timer
print("Run Time: ", datetime.now() - startTime)


# # @jit('float64(int64)', nopython=False, nogil=False)
# # def tzone_loop(n):
# #     i_list = []
# #     for i in range(n):
# #         # loopTime = datetime.now()
# #         # print(f"{i} of {n}" )
# #         j_list = []
# #         for j in range(shape[1]):
# #             Lat = float(XLAT[i,j])
# #             Long = float(XLONG[i,j])
# #             j_list.append(mytimezone(Lat,Long))
# #         # print("Lapsed Time: ", datetime.now() - loopTime)
# #         i_list.append(j_list)
# #     timezone_array = np.stack(i_list)

# #     return timezone_array

# # timezone_array = tzone_loop(shape[0])

# # vfunc = np.vectorize(mytimezone)
# # hours_list = []
# # for i in range(shape[0]):
# #     loopTime = datetime.now()
# #     print(f"{i} of {shape[0]}")
# #     out = vfunc(XLAT[i,:], XLONG[i,:])
# #     hours_list.append(out)
# #     print("Lapsed Time: ", datetime.now() - loopTime)

# # timezone_array = np.stack(hours_list)
