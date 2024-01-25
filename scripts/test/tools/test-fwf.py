import context
import json
import salem
import numpy as np
import dask
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy import stats
from pathlib import Path
import plotly.express as px
import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime
from utils.open import read_dataset

from context import data_dir, root_dir


runTime = datetime.now()
doi = pd.Timestamp("2023-11-01")

ds = xr.open_dataset(
    f'/Volumes/WFRT-Ext25/ecmwf/era5-land/{doi.strftime("%Y%m")}/era5-land-{doi.strftime("%Y%m%d%H")}.nc'
)

config = dict(
    model="ecmwf",
    domain="era5-land",
    trail_name="04",
    initialize=False,
    initialize_hffmc=False,
    overwinter=False,
    fbp_mode=False,
    correctbias=False,
)


if config["model"] == "eccc":
    config["root_dir"] = "/Volumes/WFRT-Ext23/fwf-data"
elif config["model"] == "ecmwf":
    if config["domain"] == "era5":
        config["root_dir"] = "/Volumes/ThunderBay/CRodell/ecmwf/era5/"
    elif config["domain"] == "era5-land":
        config["root_dir"] = "/Volumes/WFRT-Ext25/ecmwf/era5-land/"
elif config["model"] == "wrf":
    if int(doi.strftime("%Y")) >= 2023:
        config["root_dir"] = "/Volumes/WFRT-Ext23/fwf-data"
    else:
        config["root_dir"] = "/Volumes/Scratch/fwf-data"
else:
    raise ValueError(
        "YIKES! Sorry this model is not supported yet, you'll need to run /tools/build-static-ds.py"
    )

config["doi"] = doi

model = config["model"]
domain = config["domain"]
int_ds = read_dataset(config).chunk("auto")

hourly_ds = xr.open_dataset(
    f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
)
hourly_climo = salem.open_xr_dataset(
    "/Volumes/WFRT-Ext22/ecmwf/era5-land/S-hourly-climatology-19910101-20201231-quant.zarr"
)

# shape = np.shape(int_ds.T[0, :, :])
# static_ds = xr.open_dataset(
#     str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
# )
# var_list = list(int_ds)
# carryover_rain=True
# offset_noon=False

# dailyTime = datetime.now()
# print('---------------------------------------------------')
# print("Obtain noon local weather data")
# ### Call on variables
# tzone = static_ds.ZoneST.values

# # correct for places on int dateline
# tzone[tzone <= -12] *= -1

# ## create I, J for quick indexing
# I, J = np.ogrid[: shape[0], : shape[1]]

# ## determine index for looping based on length of time array and initial time
# time_array = int_ds.Time.values
# int_time = int(pd.Timestamp(time_array[0]).hour)
# length = len(time_array) + 1
# num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
# index = [
#     i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
# ]
# print(f"For NWP with {str(int_time).zfill(2)}Z, will use index(s) of {index} as index(s) to represent 12Z")

# times = xr.DataArray(12 + tzone.values+ offset_noon, dims= ('south_north', 'west_east'))
# south_north = xr.DataArray(I[:,0], dims= 'time')
# west_east = xr.DataArray(J[0,:], dims= 'time')

# # test = int_ds[12 + tzone.values+ offset_noon]
# test = int_ds.isel(time=times)# south_north =south_north, west_east = west_east)


# ## this is to get the index for the desired time of day offset from noon. When used a 1 is added to get in the local daily light time, as the fwi is built on standard time
# if offset_noon == False:
#     offset_noon = 0
# elif type(offset_noon) == int:
#     offset_noon = offset_noon + 1
# else:
#     raise ValueError(f"Invalided offset_noon of {offset_noon}")
# ## loop every 24 hours at noon local
# files_ds = []
# for i in index:
#     # print(i)
#     ## loop each variable
#     # print(f"offset_noon {offset_noon}")
#     mean_da = []
#     for var in var_list:
#         var_array = int_ds[var].values
#         noon = var_array[(i + tzone + offset_noon), I, J]
#         day = np.array(int_ds.Time[i + 1], dtype="datetime64[D]")
#         var_da = xr.DataArray(
#             noon,
#             name=var,
#             dims=("south_north", "west_east"),
#             coords=int_ds.isel(time=i).coords,
#         )
#         var_da["Time"] = day
#         mean_da.append(var_da)
#     mean_ds = xr.merge(mean_da)
#     files_ds.append(mean_ds)

# noon_ds = xr.combine_nested(files_ds, "time")


# if carryover_rain == True:
#     ## create datarray for carry over rain, this will be added to the next days rain totals
#     ## NOTE: this is rain that fell from noon local until 23 hours past the model initial time ie 00Z, 06Z..
#     r_o_tomorrow_i = int_ds.r_o.values[22] - noon_ds.r_o.values[0]
#     r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
#     r_o_tomorrow = np.stack(r_o_tomorrow)
#     r_o_tomorrow_da = xr.DataArray(
#         r_o_tomorrow,
#         name="r_o_tomorrow",
#         dims=("time", "south_north", "west_east"),
#         coords=noon_ds.coords,
#     )
#     r_o_tomorrow_da = xr.where(r_o_tomorrow_da > 1e-4, r_o_tomorrow_da, 0.0)

#     noon_ds["r_o_tomorrow"] = r_o_tomorrow_da

#     ## create daily 24 accumulated precipitation totals
#     x_prev = 0
#     for i, x_val in enumerate(noon_ds.r_o):
#         noon_ds.r_o[i] -= x_prev
#         x_prev = x_val
#     # print("Daily ds done")
# elif (carryover_rain == False) and (offset_noon == False):
#     var_dict = {var_list[i]: "h" + var_list[i] for i in range(len(var_list))}
#     noon_ds = noon_ds.rename(var_dict)
#     for var in var_list:
#         noon_ds["h" + var].attrs = int_ds[var].attrs
#         noon_ds["h" + var].attrs["description"] = (
#             "HOURLY NOON " + int_ds[var].attrs["description"]
#         )
#     # print("Noon ds done")
# elif (carryover_rain == False) and (offset_noon != False):
#     hourname = f"h{12 + offset_noon -1}"
#     var_dict = {
#         var_list[i]: hourname + var_list[i] for i in range(len(var_list))
#     }
#     print(var_dict)
#     noon_ds = noon_ds.rename(var_dict)
#     for var in var_list:
#         noon_ds[hourname + var].attrs = int_ds[var].attrs
#         noon_ds[hourname + var].attrs["description"] = (
#             f"{hourname.upper()}00 Hour " + int_ds[var].attrs["description"]
#         )
#     # print("Offset Noon ds done")
# else:
#     raise ValueError(
#         f"Invalided carryover_rain option: {carryover_rain}. Only supports boolean inputs \n Please try with True or False :)"
#     )
# print("Time to obtain noon local weather data:  ",  datetime.now() - dailyTime)
# print('---------------------------------------------------')


# # runTime = datetime.now()
# # ## Define the latitude and longitude arrays in degrees
# # lons_rad = np.deg2rad(ds["XLONG"])
# # lats_rad = np.deg2rad(ds["XLAT"])

# # ## Calculate rotation angle
# # theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

# # ## Calculate sine and cosine of rotation angle
# # sin_theta = np.sin(theta)
# # cos_theta = np.cos(theta)

# # ## Define the u and v wind components in domain coordinates
# # u_domain = ds["U10"]
# # v_domain = ds["V10"]

# # ## Rotate the u and v wind components to Earth coordinates
# # u_earth = u_domain * cos_theta - v_domain * sin_theta
# # v_earth = u_domain * sin_theta + v_domain * cos_theta

# # ## Solve for wind speed
# # wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
# # ds["W"] = wsp

# # ## Solve for wind direction on Earth coordinates
# # wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
# # ds["WD"] = wdir
# # old_m = wdir
# # print('Run time:  ', datetime.now()- runTime)


# # runTime = datetime.now()

# # ## Define the latitude and longitude arrays in degrees
# # lons_rad = dask.array.deg2rad(ds["XLONG"])
# # lats_rad = dask.array.deg2rad(ds["XLAT"])

# # ## Calculate rotation angle
# # theta = dask.array.arctan2(dask.array.cos(lats_rad) * dask.array.sin(lons_rad), dask.array.sin(lats_rad))

# # ## Calculate sine and cosine of rotation angle
# # sin_theta = dask.array.sin(theta)
# # cos_theta = dask.array.cos(theta)

# # ## Define the u and v wind components in domain coordinates
# # u_domain = ds["U10"]
# # v_domain = ds["V10"]

# # ## Rotate the u and v wind components to Earth coordinates
# # u_earth = u_domain * cos_theta - v_domain * sin_theta
# # v_earth = u_domain * sin_theta + v_domain * cos_theta

# # ## Solve for wind speed
# # wsp = dask.array.sqrt(u_earth ** 2 + v_earth ** 2)
# # ds["W"] = wsp

# # ## Solve for wind direction on Earth coordinates
# # wdir = 180 + ((180 / np.pi) * dask.array.arctan2(u_earth, v_earth))
# # ds["WD"] = wdir
# # new_m = wdir
# # print('Run time:  ', datetime.now()- runTime)


# # ds["tp"][0] = ds["tp"][0] - ds_yesterday["tp"].values
# # old_tp = ds["tp"]
# # r_oi = np.array(ds["tp"])
# # r_o_plus1 = np.dstack((np.zeros_like(ds["tp"][0]).T, r_oi.T)).T
# # r_hourly_list = []
# # for i in range(len(ds.time)):
# #     r_hour = r_oi[i] - r_o_plus1[i]
# #     r_hourly_list.append(r_hour)
# # r_hourly = np.stack(r_hourly_list)
# # r_hourly = xr.DataArray(r_hourly, name="tp", dims=("time", "latitude", "longitude"))
# # ds["tp"] = r_hourly
# # old_m = r_hourly
# # print('Run time:  ', datetime.now()- runTime)


# # runTime = datetime.now()
# # filein = '/Volumes/WFRT-Ext25/ecmwf/era5-land/'
# # domain = 'era5-land'
# # file_yesterday = f"{filein}{(doi + pd.Timedelta(days=-1)).strftime('%Y%m')}/{domain}-{(doi + pd.Timedelta(days=-1)).strftime('%Y%m%d00.nc')}"
# # file = f"{filein}{(doi).strftime('%Y%m')}/{domain}-{(doi).strftime('%Y%m%d00.nc')}"

# # ds_yesterday = xr.open_dataset(file_yesterday).isel(time=23).chunk("auto")
# # ds = xr.open_dataset(file).chunk("auto")
# # ds["tp"][0] = ds["tp"][0] - ds_yesterday["tp"].values
# # old_tp = ds["tp"]
# # r_oi = ds["tp"]

# # r_o_plus1 = dask.array.dstack((dask.array.zeros_like(ds["tp"][0]).T, r_oi.T)).T
# # r_hourly_list = []
# # for i in range(len(ds.time)):
# #     r_hour = r_oi[i] - r_o_plus1[i]
# #     r_hourly_list.append(r_hour)
# # r_hourly = dask.array.stack(r_hourly_list)
# # r_hourly = xr.DataArray(r_hourly, name="tp", dims=("time", "latitude", "longitude"))
# # ds["tp"] = r_hourly
# # new_m = r_hourly

# # print('Run time:  ', datetime.now()- runTime)


# # for i in range(len(ds['time'])):
# #     print(np.nanmin((new_m.isel(time = i) - old_m.isel(time = i)).values))
# #     print(np.nanmax((new_m.isel(time = i) - old_m.isel(time = i)).values))

# # test = xr.open_dataset(
# #     "/Volumes/WFRT-Ext22/frp/goes/g18/2023/OR_ABI-L2-FDCF-M6_G18_s20232440050219_e20232440059527_c20232440100027.nc"
# # )
# # previous_daily_ds = xr.open_dataset(
# #     "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-daily-d02-2021011006.nc"
# # )


# # daily_ds = xr.open_dataset(
# #     "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-daily-d02-2021011106.nc"
# # )

# # hourly_ds = xr.open_dataset(
# #     "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-hourly-d02-2021011106.nc"
# # )
# # hourly_ds_old = xr.open_dataset(
# #     "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-hourly-d02-2021011106-copy.nc"
# # )

# # BUI = previous_daily_ds["U"].isel(time=0)
# # try:
# #     BUI = BUI.drop(["time"])
# # except:
# #     pass

# # daily_ds_i = daily_ds["U"]
# # daily_ds_i = daily_ds_i.drop(["XTIME"])
# # daily_ds_i = xr.combine_nested([BUI, daily_ds_i], "time")
# # daily_ds_i["time"] = daily_ds_i["Time"] + np.timedelta64(18, "h")

# # # Convert daily data to hourly intervals
# # hourly_dates = hourly_ds.Time.values
# # daily_dsH = daily_ds_i.resample(time="1H").interpolate("linear")

# # # Extrapolate forward in time
# # daily_dsH = daily_dsH.reindex(time=hourly_dates)
# # # Forward fill the extrapolated values
# # U = daily_dsH.ffill(dim="time")
# # U = U.transpose("time", "south_north", "west_east")

# # # U.isel(south_north = 50, west_east = 100).plot()

# # S_interp = hourly_ds_old["S"].mean(dim=("south_north", "west_east"))
# # S_old = hourly_ds["S"].mean(dim=("south_north", "west_east"))

# # (S_interp - S_old).plot()

# # S_interp.plot()
# # S_old.plot()


# # S_interp = hourly_ds_old["S"].mean(dim=("time"))
# # S_old = hourly_ds["S"].mean(dim=("time"))

# # (S_interp - S_old).plot()
# # S_old.plot()


# # f_D = xr.where(
# #     U > 80,
# #     1000 / (25 + 108.64 * np.exp(-0.023 * U)),
# #     (0.626 * np.power(U, 0.809)) + 2,
# # )
# # f_D.isel(south_north = 50, west_east = 100).plot()

# # U.isel(south_north = 50, west_east = 100).plot()

# # hourly_ds.isel(south_north = 50, west_east = 100)['S'].plot()
# # hourly_ds.isel(south_north = 50, west_east = 100)['R'].plot()
