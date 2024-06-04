#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import wrf
import salem
import json
import pickle
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import matplotlib.pyplot as plt

from context import data_dir

ds = salem.open_xr_dataset(str(data_dir) + '/fwf-data/fwf-hourly-d02-2024060306.nc')



fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(1, 1, 1)
colors = np.vstack(
    ([1, 1, 1, 1], plt.get_cmap("YlOrRd")(np.linspace(0, 1, 256)))
)  # Add white at the start
custom_cmap = LinearSegmentedColormap.from_list("custom_YlOrRd", colors)
ds['FRP'].isel(time = 18).salem.quick_map(
    cmap=custom_cmap, vmin=10, vmax=1000, ax=ax,
)
# ax.set_title(f'Fire Radiative Power (MW) \n {str(frp_i.time.values)[:13]}')
ax.set_title(f"Fire Radiative Power (MW) \n")


fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(1, 1, 1)
ds['S'].isel(time = 18).salem.quick_map(
    cmap='jet',  ax=ax,
)
# # from wrf import omp_set_num_threads, omp_get_max_threads

# # omp_set_num_threads(8)
# # print(f"read files with {omp_get_max_threads()} threads")

# startTime = datetime.now()

# g = 9.81  # gravity
# pm_ef = 21.05  # boreal wildfire emission factor Urbanski (2014)
# zstep = 20.0  # vertical step to interpolate to
# BLfrac = 0.75  # fraction of BL height to set zs at
# interpz = np.arange(0, 4000, zstep)
# interpz[0] = 2
# interpz = np.insert(interpz, 1, 10)


# ncfile = Dataset("/bluesky/fireweather/fwf/data/wrfout_d01_2019-05-11_17:49:11")
# # ncfile = Dataset(str(vol_dir) + "/sfire/unit5/wrfout_d01_0001-01-01_00:00:00")
# save_dir = "/bluesky/fireweather/fwf/data/"


# # startCache= datetime.now()
# # my_cache = wrf.extract_vars(ncfile, wrf.ALL_TIMES, ( "PSFC", "PH", "PHB"))
# # print("Cache time: ", datetime.now() - startCache)

# startInterp = datetime.now()

# print(f"Start of Interoplation ---> {datetime.now()}")
# startVar = datetime.now()
# # tr17_1 = wrf.getvar(ncfile, "tr17_1", wrf.ALL_TIMES)
# interp_tr17_1 = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "tr17_1", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate tracer time: ", datetime.now() - startVar)

# startVar = datetime.now()
# # qvapor = wrf.getvar(ncfile, "QVAPOR", wrf.ALL_TIMES)
# interp_qvapor = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "QVAPOR", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate qvapor time: ", datetime.now() - startVar)

# startVar = datetime.now()
# # temp = wrf.getvar(ncfile, "temp", wrf.ALL_TIMES)
# interp_temp = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "temp", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     field_type="tk",
#     # cache=my_cache
# )
# print("Interpolate temp time: ", datetime.now() - startVar)

# startVar = datetime.now()
# # td = wrf.getvar(ncfile, "td", wrf.ALL_TIMES)
# interp_td = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "td", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     field_type="tk",
#     # cache=my_cache
# )
# print("Interpolate td time: ", datetime.now() - startVar)

# startVar = datetime.now()
# # theta_e = wrf.getvar(ncfile, "theta_e", wrf.ALL_TIMES)
# interp_theta_e = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "theta_e", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     field_type="tk",
#     # cache=my_cache
# )
# print("Interpolate theta_e time: ", datetime.now() - startVar)

# startVar = datetime.now()
# # rh = wrf.getvar(ncfile, "rh", wrf.ALL_TIMES)
# interp_rh = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "rh", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate rh time: ", datetime.now() - startVar)

# startVar = datetime.now()
# # U = wrf.getvar(ncfile, "ua", wrf.ALL_TIMES)
# interp_U = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "ua", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate U time: ", datetime.now() - startVar)


# startVar = datetime.now()
# # V = wrf.getvar(ncfile, "va", wrf.ALL_TIMES)
# interp_V = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "va", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate V time: ", datetime.now() - startVar)


# startVar = datetime.now()
# # W = wrf.getvar(ncfile, "wa", wrf.ALL_TIMES)
# interp_W = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "wa", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate W time: ", datetime.now() - startVar)


# startVar = datetime.now()
# # pressure = wrf.getvar(ncfile, "pressure", wrf.ALL_TIMES)
# interp_pressure = wrf.vinterp(
#     ncfile,
#     field=wrf.getvar(ncfile, "pressure", wrf.ALL_TIMES),
#     vert_coord="ght_msl",
#     interp_levels=interpz / 1000,
#     extrapolate=True,
#     log_p=True,
#     timeidx=wrf.ALL_TIMES,
#     # cache=my_cache
# )
# print("Interpolate pressure time: ", datetime.now() - startVar)


# def compressor(ds):
#     """
#     this function comresses datasets
#     """
#     # print('loading')
#     # ds = ds.load()
#     print("zipping")
#     comp = dict(zlib=True, complevel=9)
#     print("encoding")
#     encoding = {var: comp for var in ds.data_vars}
#     return ds, encoding


# interp_ds = xr.merge(
#     [
#         interp_tr17_1,
#         interp_qvapor,
#         interp_temp,
#         interp_td,
#         interp_theta_e,
#         interp_rh,
#         interp_U,
#         interp_V,
#         interp_W,
#         interp_pressure,
#     ]
# )
# interp_ds.attrs = {
#     "description": "WRF SFIRE UNIT 5 MOISTURE OFF",
#     "dx": "25 m",
#     "dy": "25 m",
#     "dz": "20 m",
# }
# for var in interp_ds.data_vars:
#     interp_ds[var].attrs["projection"] = str(interp_ds[var].attrs["projection"])
# print("Interpolate time: ", datetime.now() - startInterp)

# startCompress = datetime.now()
# comp_ds, encoding = compressor(interp_ds)
# print("Compress time: ", datetime.now() - startCompress)

# startWrite = datetime.now()
# ## write the new dataset
# comp_ds.to_netcdf(
#     str(save_dir) + "/interp_unit5.nc",
#     encoding=encoding,
#     mode="w",
# )
# print("Write time: ", datetime.now() - startWrite)

# print("Total run time: ", datetime.now() - startTime)
