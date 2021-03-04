# import context
# import json
# import numpy as np
# import pandas as pd
# import xarray as xr
# from pathlib import Path
# from netCDF4 import Dataset
# from utils.make_intercomp import daily_merge_ds

# import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# import matplotlib.colors
# import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# import scipy.ndimage as ndimage
# from scipy.ndimage.filters import gaussian_filter


# from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
# from datetime import datetime, date, timedelta

# startTime = datetime.now()
# print("RUN STARTED AT: ", str(startTime))

# ## Define model/domain and datetime of interest
# # date = pd.Timestamp("today")
# date = pd.Timestamp(2018, 7, 20)
# domain = "d02"
# wrf_model = "wrf3"

# ## Path to hourly/daily fwi data
# forecast_date = date.strftime("%Y%m%d06")
# hourly_file_dir = (
#     str(fwf_zarr_dir) + f"/fwf-hourly-{domain}-{forecast_date}.zarr"
# )
# daily_file_dir = (
#     str(fwf_zarr_dir) + f"/fwf-daily-{domain}-{forecast_date}.zarr"
# )
# wrf_file_dir = str(wrf_dir) + f"/wrfout-{domain}-{forecast_date}.zarr"

# ## Path to fuel converter spreadsheet
# fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
# ## Path to fuels data
# fuelsin = str(data_dir) + f"/fbp/fuels-{wrf_model}-{domain}.zarr"
# ## Path to terrain data
# terrain = str(data_dir) + f"/terrain/hgt-{wrf_model}-{domain}.nc"

# ## Open hourly/daily fwi data
# hourly_ds = xr.open_zarr(hourly_file_dir)
# daily_ds = xr.open_zarr(daily_file_dir)

# # daily_ds = daily_merge_ds(forecast_date, domain, wrf_model)
# wrf_ds = xr.open_zarr(wrf_file_dir)
# TD = wrf_ds.TD
# T = wrf_ds.T
# H = wrf_ds.H

# RH = ((6.11*10**(7.5*   (TD/ (237.7 + TD))))/ (6.11*10**(7.5*   (T/ (237.7 + T))))) * 100

# RH = xr.where(RH>100, 100, RH)

# plt.plot(wrf_ds.Time, RH.mean(dim = ('south_north', 'west_east')))
# plt.plot(wrf_ds.Time, H.mean(dim = ('south_north', 'west_east')))

# RHt = RH.values
# W, T, H, r_o, SNOWC = (
#     daily_ds.W,
#     daily_ds.T,
#     daily_ds.H,
#     daily_ds.r_o,
#     daily_ds.SNOWC,
# )

# T = xr.where(T < -1.1, -1.1, T)

# shape = hourly_ds.XLAT.shape

# ### Open tzone  domain
# filein = str(tzone_dir) + f"/tzone_{wrf_model}_{domain}.zarr"
# tzone_ds = xr.open_zarr(filein)


# ### Call on variables
# tzone = tzone_ds.Zone.values

# ## create I, J for quick indexing
# I, J = np.ogrid[: shape[0], : shape[1]]

# ## determine index for looping based on length of time array and initial time
# time_array = wrf_ds.Time.values
# int_time = int(pd.Timestamp(time_array[0]).hour)
# length = len(time_array) + 1
# num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
# index = [
#     i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
# ]
# print(f"index of times {index} with initial time {int_time}Z")

# ## loop every 24 hours at noon local
# files_ds = []
# for i in index:
#     # print(i)
#     ## loop each variable
#     mean_da = []
#     for var in wrf_ds.data_vars:
#         if var == "SNOWC":
#             var_array = wrf_ds[var].values
#             noon = var_array[(i + tzone), I, J]
#             day = np.array(wrf_ds.Time[i + 1], dtype="datetime64[D]")
#             var_da = xr.DataArray(
#                 noon,
#                 name=var,
#                 dims=("south_north", "west_east"),
#                 coords=wrf_ds.isel(time=i).coords,
#             )
#             var_da["Time"] = day
#             mean_da.append(var_da)
#         else:
#             var_array = wrf_ds[var].values
#             noon_minus = var_array[(i + tzone - 1), I, J]
#             noon = var_array[(i + tzone), I, J]
#             noon_pluse = var_array[(i + tzone + 1), I, J]
#             noon_mean = (noon_minus + noon + noon_pluse) / 3
#             day = np.array(wrf_ds.Time[i + 1], dtype="datetime64[D]")
#             var_da = xr.DataArray(
#                 noon_mean,
#                 name=var,
#                 dims=("south_north", "west_east"),
#                 coords=wrf_ds.isel(time=i).coords,
#             )
#             var_da["Time"] = day
#             mean_da.append(var_da)

#     mean_ds = xr.merge(mean_da)
#     files_ds.append(mean_ds)

# daily_ds = xr.combine_nested(files_ds, "time")

# ## create datarray for carry over rain, this will be added to the next days rain totals
# ## NOTE: this is rain that fell from noon local until 24 hours past the model initial time ie 00Z, 06Z..
# r_o_tomorrow_i = wrf_ds.r_o.values[23] - daily_ds.r_o.values[0]
# r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
# r_o_tomorrow = np.stack(r_o_tomorrow)
# r_o_tomorrow_da = xr.DataArray(
#     r_o_tomorrow,
#     name="r_o_tomorrow",
#     dims=("time", "south_north", "west_east"),
#     coords=daily_ds.coords,
# )
# r_o_tomorrow_da = xr.where(r_o_tomorrow_da > 1e-4, r_o_tomorrow_da, 0.0)

# daily_ds["r_o_tomorrow"] = r_o_tomorrow_da


# # ## create daily 24 accumulated precipitation totals
# # x_prev = 0
# # for i, x_val in enumerate(daily_ds.r_o):
# #     daily_ds.r_o[i] -= x_prev
# #     x_prev = x_val

# # print("Daily ds done")
# # test = daily_ds.r_o.values

# # zero_full = np.zeros(hourly_ds.XLAT.shape, dtype=float)


# # ### Solve for hourly rain totals in mm....will be used in ffmc calculation
# # r_oi = np.array(hourly_ds.r_o)
# # r_o_plus1 = np.dstack((zero_full.T, r_oi.T)).T
# # r_hourly_list = []
# # for i in range(len(hourly_ds.Time)):
# #     r_hour = hourly_ds.r_o[i] - r_o_plus1[i]
# #     r_hourly_list.append(r_hour)
# # r_hourly = np.stack(r_hourly_list)
# # r_hourly = xr.DataArray(
# #     r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
# # )
# # hourly_ds["r_o_hourly"] = r_hourly


# # r_hour = r_hourly.values
# # r_hour2 = hourly_ds.r_o.values
# # x_prev = 0
# # for i, x_val in enumerate(hourly_ds.r_o.values):
# #     hourly_ds.r_o[i].values -= x_prev
# #     x_prev = x_val
