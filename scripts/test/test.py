import context
import salem
import json
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from utils.wrf import read_wrf
from utils.eccc import read_eccc
from netCDF4 import Dataset

from context import data_dir


model = "eccc"
domain = "hrdps"
doi = pd.Timestamp("2021-01-01T00")


grid_ds = xr.open_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")

static_ds = xr.open_dataset(str(data_dir) + f"/static/static-vars-{model}-{domain}.nc")
# landmask = static_ds['LAND']

ds = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/01/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
).isel(time=0)

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds['HFI'].isel(time = 24).salem.quick_map(ax=ax, cmap="coolwarm")
# # condition_broadcast = xr.broadcast(landmask, ds['F'])[0]


###################################################################################################
###################################################################################################

tzone_shp = str(data_dir) + "/shp/buffed_oceans/buffed_oceans.shp"
df = salem.read_shapefile(tzone_shp)

name = df.loc[df["featurecla"] == "Ocean"]
dsr = ds["F"].salem.roi(shape=name, all_touched=True)

array_values = dsr.values * 0
# array_values[np.isnan(array_values)] = 1


ds["mask"] = (("south_north", "west_east"), array_values)
ds["mask"].attrs["pyproj_srs"] = ds["F"].attrs["pyproj_srs"]

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)
ds["mask"].salem.quick_map(ax=ax, cmap="coolwarm")

# ## 1 is for land 0 is for ocean
masked_arr = np.ma.masked_where(ds["mask"] == 0, ds["mask"])

for var in static_ds:
    result = np.ma.array(
        static_ds[var], mask=masked_arr.mask
    )  # fill_value=masked_arr.fill_value)
    static_ds[var] = (("south_north", "west_east"), result)
    static_ds[var].attrs["pyproj_srs"] = ds["F"].attrs["pyproj_srs"]
    grid_ds[var] = static_ds[var]  # .to_masked_array()
    # grid_ds[var].mask = masked_arr.mask
grid_ds["LAND"] = (("south_north", "west_east"), masked_arr.mask)
grid_ds["LAND"].attrs["pyproj_srs"] = ds["F"].attrs["pyproj_srs"]
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(1, 1, 1)
grid_ds["LAND"].salem.quick_map(ax=ax, cmap="coolwarm")
grid_ds.to_netcdf(str(data_dir) + f"/static/static-vars-{model}-{domain}-test.nc")

###################################################################################################
###################################################################################################


# test = xr.where(condition_broadcast, ds['F'], 0)

# .isel(time = -1)
# ds

# ds = ds.chunk('auto')
# ds = ds.chunk('auto')

# startTime = datetime.now()
# for var in ds:
#     masked_array = ds[var].to_masked_array()
#     masked_array.mask = landmask
#     masked_array.fill_value = 0
#     ds[var] = (('time','south_north', 'west_east'), masked_array)
#     ds[var].attrs['pyproj_srs'] = ds.attrs['pyproj_srs']
# print("Mask: ", datetime.now() - startTime)

# startTime = datetime.now()
# ds = ds.fillna(0)
# print("Fillnan: ", datetime.now() - startTime)

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds['T'].isel(time = 24).salem.quick_map(ax=ax, cmap="coolwarm")


# test = ds.where(landmask)


# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds['S'].salem.quick_map(ax=ax, cmap="coolwarm")


# W = ds['W']
# W = np.ma.array(W, mask=landmask, fill_value=0)

# ds['W'] = (('south_north', 'west_east'), W)
# ds['W'].attrs['pyproj_srs'] = ds['F'].attrs['pyproj_srs']

# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds['W'].salem.quick_map(ax=ax, cmap="coolwarm")


# test_ds = salem.open_xr_dataset(str(data_dir)+f"/static/static-vars-{model}-{domain}.nc")


# test_ds['LAND'].salem.quick_map(cmap = 'terrain')
# tester = test_ds['LAND'].to_masked_array()


# result = np.ma.array(ds['F'], mask=tester.mask,) #fill_value=masked_arr.fill_value)
# ds['result'] = (('south_north', 'west_east'), result)
# ds['result'].attrs['pyproj_srs'] = ds['F'].attrs['pyproj_srs']
# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# ds['result'].salem.quick_map(ax=ax, cmap="coolwarm")

# grid = grid.astype(bool)


# # Create a NumPy array with a mask
# a = np.array([1, 2, 3, 4])
# mask = np.array([True, False, False, True])

# # Create a masked array in xarray
# xa = xr.DataArray(a, dims='dim', coords={'dim': range(len(a))}).to_masked_array()
# xa.fill_value = 0
# xa.mask = mask

# # Print the masked array
# print(xa)


# grid = ~grid

# # Find all 0s next to a 1
# mask = (grid[:-1, :] == 1) & (grid[1:, :] == 0)
# mask = np.pad(mask, ((1, 0), (0, 0)), mode='constant', constant_values=False)

# # Set all masked values to 1
# grid = np.where(mask, 1, grid)


# # Convert the binary array to a masked array
# masked_array = np.ma.masked_where(grid == 1,wrf_ds['F'])


# ds['F_masked'] = (('south_north', 'west_east'), masked_array)


# fig = plt.figure(figsize=(12, 6))
# ax = fig.add_subplot(1, 1, 1)
# dsr.salem.quick_map(ax=ax, cmap="coolwarm")

# # test = data * 1000

# # Print the masked array
# print(masked_array)


# # # Create a binary grid
# # grid = np.array([[1, 0, 0, 1],
# #                  [0, 0, 1, 0],
# #                  [1, 1, 0, 1],
# #                  [1, 0, 0, 0]])
# # print(grid)

# # Find all 0s next to a 1
# # mask = (grid[:-1, :] == 1) & (grid[1:, :] == 0)
# # mask = np.pad(mask, ((1, 0), (0, 0)), mode='constant', constant_values=False)

# # # Set all masked values to 1
# # grid2 = np.where(mask, 0, grid)

# # # Print the updated grid
# # print(grid2)


# # Create a binary grid
# grid = np.array([[1, 0, 0, 1],
#                  [0, 0, 1, 0],
#                  [1, 1, 0, 1],
#                  [1, 0, 0, 0]])

# # Find all 0s next to a 1
# for i in range(0,10):
#     mask = (grid[:-1, :] == 1) & (grid[1:, :] == 0)
#     mask = np.pad(mask, ((1, 0), (0, 0)), mode='constant', constant_values=False)

#     # Set all masked values to 1
#     grid = np.where(mask, 1, grid)

#     # Print the updated grid
#     print(grid)

# # ds = salem.open_xr_dataset(
# #     f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/01/fwf-daily-{domain}-{doi.strftime('%Y%m%d%H')}.nc"
# # )

# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ds.isel(time=0)["D"].salem.quick_map(ax=ax, cmap="coolwarm",vmin =0 , vmax =800)


# # int_ds = salem.open_xr_dataset(
# #         f"/Volumes/Scratch/fwf-data/{model}/d02/202108/fwf-hourly-{domain}-2021080106.nc"

# # )

# # int_ds = salem.open_xr_dataset(
# #         f"/Volumes/Scratch/fwf-data/{model}/d02/202108/fwf-daily-{domain}-2021080106.nc"

# # )

# # # int_ds = int_ds.isel(time =0)
# # time_interval = int_ds.Time.values


# # # Calculate the time delta
# # if time_interval.size == 1:
# #     daily_ds = int_ds
# #     print("This is dataset is a has a daily time step, will solve FWI without finding noon local")
# # else:
# #     delta = time_interval[1] - time_interval[0]
# #     hours = delta.astype('timedelta64[h]')
# #     print('Time interval in hours:', hours)
# #     if hours == 1:
# #         print("This is dataset is a has a hourly time interval, will solve FWI by finding noon local")
# #     elif hours == 24:
# #         daily_ds = int_ds
# #         print("This is dataset is a has a daily time interval, will solve FWI without finding noon local")
# #     else:
# #         raise ValueError(f"Sadly this is an incompatible time interval of {hours}. FWF currently only works with hourly or daily time intervals")


# # from netCDF4 import Dataset
# # from wrf import (
# #     getvar,
# # )

# # ## open domain config file with variable names and attributes
# # with open(str(data_dir) + "/json/eccc-config.json") as f:
# #     econfig = json.load(f)


# # def solve_TD(ds):
# #     p = ds["P0"].values  # *.01
# #     qv = ds["QV"].values
# #     qv[qv < 0] = 0
# #     tdc = qv * p / (0.622 + qv)
# #     td = (243.5 * np.log(tdc) - 440.8) / (19.48 - np.log(tdc))
# #     ds["TD"] = (("south_north", "west_east"), td)
# #     return ds


# # def solve_RH(ds):
#     TD = ds.TD.values
#     T = ds.T.values
#     RH = (
#         (6.11 * 10 ** (7.5 * (TD / (237.7 + TD))))
#         / (6.11 * 10 ** (7.5 * (T / (237.7 + T))))
#         * 100
#     )
#     RH = xr.where(RH > 100, 100, RH)
#     ds["H"] = (("south_north", "west_east"), RH)
#     if np.min(ds.H) > 90:
#         raise ValueError("ERROR: Check TD unphysical RH values")
#     return ds


# def rename_vars(ds):
#     var_dict = econfig[domain]
#     var_list = list(ds)
#     for key in list(var_dict.keys()):
#         # Check if the key is not in the list of valid keys
#         if key not in var_list:
#             # Remove the key from the dictionary
#             del var_dict[key]
#     ds = ds.rename(var_dict)
#     ds = ds.rename(
#         {
#             "rlon": "west_east",
#             "rlat": "south_north",
#         }
#     )
#     var_list = list(ds)
#     if "TD" not in var_list:
#         ds = solve_TD(ds)
#     if "H" not in var_list:
#         ds = solve_RH(ds)
#     if "SNOWH" not in var_list:
#         ds["SNOWH"] = (("south_north", "west_east"), np.zeros_like(ds["T"].values))
#     ds = ds.chunk("auto")
#     return ds


# startTime = datetime.now()

# model = "eccc"
# domain = "hrdps"

# save_dir = f"/Volumes/WFRT-Ext24/{model}/{domain}/"
# doi = pd.Timestamp("2022-01-14")
# i = 20
# path = (
#     f'{save_dir}{doi.strftime("%Y%m")}/{doi.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
# )
# hrdps_ds = xr.open_dataset(
#     f'{save_dir}{doi.strftime("%Y%m")}/{doi.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
# )

# save_dir1 = f"/Volumes/WFRT-Ext24/{model}/rdps/"
# path1 = (
#     f'{save_dir1}{doi.strftime("%Y%m")}/{doi.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
# )
# rdps_ds = xr.open_dataset(path1, chunks="auto").isel(height1=0, height2=0, sfctype=0)
# rdps_ds = rdps_ds.rename(econfig["rdps"])

# # print(list(hrdps_ds.dims))


# ds = xr.open_dataset(path, chunks="auto")
# dim_list = list(ds.dims)
# dim_dict = {
#     "time": -1,
#     "level": 0,
#     "height1": 0,
#     "height2": 0,
#     "sfctype": 0,
#     "time1": -1,
#     "time2": -1,
#     "height": 0,
# }
# for key in list(dim_dict.keys()):
#     # Check if the key is not in the list of valid keys
#     if key not in dim_list:
#         # Remove the key from the dictionary
#         del dim_dict[key]
# ds = rename_vars(ds.isel(dim_dict))
# if "time" in list(dim_dict):
#     ds = ds.assign_coords(time=ds.time.values)
# elif "time2" in list(dim_dict):
#     ds = ds.assign_coords(time=ds.time2.values)
# ds = ds.expand_dims(dim="time")

# ds


# ds['SD'] = (("south_north", "west_east"), np.zeros_like(ds["TT"].values))
# ds = ds.assign_coords(time=ds.time2.values)
# ds = ds.expand_dims(dim ='time')
# ds = ds.rename(econfig[domain])

# df = pd.read_csv(str(data_dir)+f'/{model}/{domain}/check.csv')

# filtered_df = df.loc[df['good_nc'] == -99]

# date_range = pd.date_range(f"2021-01-01", f"2021-03-01")
# # ds = xr.open_dataset(save_dir_i)
# path_in_str = str(data_dir)+'/wrf/wrfout_d02_2021-01-14_00:00:00'
# wrf_ds = xr.open_dataset(path_in_str).isel(Time = 0)

# wrf_file = Dataset(path_in_str, "r")
# #
# TD = getvar(wrf_file, "rh2")

# p = wrf_ds['PSFC'].values*.01
# qv = wrf_ds['Q2'].values
# qv[qv < 0] = 0

# tdc = qv*p/ (0.622+qv)
# td = (243.5 * np.log(tdc)- 440.8) / (19.48 - np.log(tdc))


# omp_set_num_threads(8)
# print(f"read files with {omp_get_max_threads()} threads")
# startTime = datetime.now()
# print("begin readwrf: ", str(startTime))

# path_in_str = str(str(data_dir) + '/wrf/uvic_d01_2020-09-01_07 00 00')
# print(path_in_str)
# wrf_file = Dataset(path_in_str, "r")

# T = getvar(wrf_file, "T2", meta=True) - 273.15
# TD = getvar(wrf_file, "td2", meta=True, units="degC")
# # H = getvar(wrf_file, "rh2", meta=True)

# wsp_wdir = g_uvmet.get_uvmet10_wspd_wdir(wrf_file, units="km h-1")
# wsp_array = np.array(wsp_wdir[0])
# wdir_array = np.array(wsp_wdir[1])
# W = xr.DataArray(wsp_array, name="W", dims=("south_north", "west_east"))
# WD = xr.DataArray(wdir_array, name="WD", dims=("south_north", "west_east"))
# U10 = getvar(wrf_file, "U10", meta=True)
# V10 = getvar(wrf_file, "V10", meta=True)

# ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run
# rain_c = getvar(wrf_file, "RAINC", meta=True)
# # rain_sh = getvar(wrf_file, "RAINSH", meta=True)
# rain_nc = getvar(wrf_file, "RAINNC", meta=True)
# # r_o_i = rain_c + rain_sh + rain_nc
# r_o_i = rain_c  + rain_nc

# r_o = xr.DataArray(r_o_i, name="r_o", dims=("south_north", "west_east"))

# SNW = getvar(wrf_file, "SNOWNC", meta=True)
# # SNOWC = getvar(wrf_file, "SNOWC", meta=True)
# SNOWH = getvar(wrf_file, "SNOWH", meta=True)

# # var_list = [T, TD, H, W, WD, r_o, SNW, SNOWC, SNOWH, U10, V10]
# var_list = [T, TD, W, WD, r_o, SNW, SNOWH, U10, V10]
# ds = xr.merge(var_list)

# ds_list.append(ds)

### Combine xarray and rename to match van wangers defs
# wrf_ds = xr.combine_nested(ds_list, "time")
# wrf_ds = ds
# wrf_ds = wrf_ds.rename_vars({"T2": "T", "td2": "TD", "SNOWNC": "SNW"})
# # wrf_ds["SNW"] = wrf_ds.SNW - wrf_ds.SNW.isel(time=0)
# # wrf_ds["r_o"] = wrf_ds.r_o - wrf_ds.r_o.isel(time=0)

# RH = (
#     (6.11 * 10 ** (7.5 * (wrf_ds.TD / (237.7 + wrf_ds.TD))))
#     / (6.11 * 10 ** (7.5 * (wrf_ds.T / (237.7 + wrf_ds.T))))
#     * 100
# )
# RH = xr.where(RH > 100, 100, RH)
# RH = xr.DataArray(RH, name="H", dims=( "south_north", "west_east"))
# wrf_ds["H"] = RH
# if np.min(wrf_ds.H) > 90:
#     raise ValueError("ERROR: Check TD unphysical RH values")

# wrf_file = Dataset(str(pathlist[0]), "r")
# nc_attrs = wrf_file.ncattrs()
# for nc_attr in nc_attrs:
#     wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

# print(list(wrf_ds))
# if wright == True:
#     print(wrf_ds)
#     time = np.array(wrf_ds.Time.dt.strftime("%Y-%m-%dT%H"))
#     timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")
#     wrf_ds = wrf_ds.load()
#     for var in list(wrf_ds):
#         wrf_ds[var].encoding = {}

#     wrf_ds_dir = str(save_dir) + str(f"wrfout-{domain}-{timestamp}.nc")
#     wrf_ds.to_netcdf(wrf_ds_dir, mode="w")
#     print(f"wrote {wrf_ds_dir}")
# else:
#     pass

# grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/uvic_d01_2020-09-01_07 00 00")
# grid_ds = grid_ds.copy()[['T2']].sel(Time = 0)

# wrf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
# for var in list(wrf_ds):
#     grid_ds[var] =  wrf_ds[var]
#     grid_ds[var].attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
#     fig = plt.figure(figsize=(12, 6))
#     ax = fig.add_subplot(1, 1, 1)
#     grid_ds[f"{var}"].salem.quick_map(
#         ax=ax, cmap="coolwarm", extend="both"
#     )
#     fig.savefig(
#         str(data_dir) + f'/images/downscale/{var}.png',
#         dpi=250,
#         bbox_inches="tight",
#     )
# print("readwrf run time: ", datetime.now() - startTime)
