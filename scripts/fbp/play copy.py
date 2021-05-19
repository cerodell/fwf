import context
import json
import salem
import pickle
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt


from context import data_dir, vol_dir, gog_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

PA = 360
cor = 0.6 * PA + 2.5
cor = 1.6 * PA - 194

# daily_ds = xr.open_zarr(
#     str(fwf_zarr_dir) + f"/fwf-daily-{domain}-{forecast_date}.zarr"
# )


# P_h = hourly_ds.P.values
# maxindex = P_h.argmax()
# ind_h = np.unravel_index(P_h.argmax(), P_h.shape)
# P_d = daily_ds.P.values
# maxindex = P_d.argmax()
ind_d = np.unravel_index(P_d.argmax(), P_d.shape)


static_ds = xr.open_zarr(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
)

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)

ds = ds.sel(wmo=71689)
ds = ds.sel(time=slice("2019-05-06", "2019-06-30"))
date_range = pd.date_range("2019-05-06", "2019-06-30")

fig = plt.figure(figsize=[6, 4])
ax = fig.add_subplot(1, 1, 1)
ax.plot(date_range, ds.fwi.values)
ax.plot(date_range, ds.fwi_day1.values)

fig = plt.figure(figsize=[6, 4])
ax = fig.add_subplot(1, 1, 1)
ax.plot(date_range, ds.precip.values)
ax.plot(date_range, ds.precip_day1.values)

fig = plt.figure(figsize=[6, 4])
ax = fig.add_subplot(1, 1, 1)
ax.plot(date_range, ds.rh.values)
ax.plot(date_range, ds.rh_day1.values)

# ## Path to fuels data terrain data
# static_filein = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
# ## Open datsets: gridded static and FWF
# static_ds = xr.open_zarr(static_filein)

# ds = xr.open_zarr(str(vol_dir) + "/fwf-hourly-d02-2019040100-2019100100.zarr")


# hourly_ds['time'] = hourly_ds.Time.values
# ds_daily['time'] = ds_daily.Time.values


# fwf_tree, fwf_locs = pickle.load(open(str(data_dir) + "/kdtree/fwf_tree.p", "rb"))
# # test = ds.sel(time = slice('2019-05-11-T12', '2019-05-12-T12'))
# hourly_ds = hourly_ds.sel(time = '2019-05-12-T01')
# ds_daily = ds_daily.sel(time = '2019-05-11')


# single_fuel_loc = np.array([56., -113.540]).reshape(1, -1)
# fwf_dist, fwf_ind = fwf_tree.query(single_fuel_loc, k=1)

# FUELS = static_ds.FUELS.values.ravel()
# var_h = hourly_ds.H.values.ravel()
# var_d = ds_daily.U.values.ravel()

# print(var_h[fwf_ind])
# print(var_d[fwf_ind])
# print(FUELS[fwf_ind])

# another_arr = ROS.reshape(-1, ROS.shape[0])

# plt.plot(another_arr[fwf_ind[0],:][-1])

# test.D.plot()
