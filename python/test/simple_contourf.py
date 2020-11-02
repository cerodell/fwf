import context
import math
import pickle
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as crs
import cartopy.feature as cfeature
import timezonefinder, pytz
from datetime import datetime
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt
from context import root_dir

startTime = datetime.now()

# xr_dir = '/Volumes/cer/fireweather/data/xr/'

# hourly_file_dir_old  = str(xr_dir) + "/fwf-hourly-2020091200.zarr"
# hourly_ds_old = xr.open_zarr(hourly_file_dir_old)

# daily_file_dir_old  = str(xr_dir) + "/fwf-daily-2020091200.zarr"
# daily_ds_old = xr.open_zarr(daily_file_dir_old)

# %%

# wrf_file_dir = "/Volumes/CER/WFRT/FWI/Data/20190819_05/"
# wrf_ds, xy_np = readwrf(wrf_file_dir)

# scp -r fwfop@bluesky2.eoas.ubc.ca:/bluesky/archive/fireweather/hourly/2020-06-07T00.zarr /Volumes/CER/WFRT/FWI/Data/hourly
# scp -r fwfop@bluesky2.eoas.ubc.ca:/bluesky/archive/fireweather/daily/2020-06-07T00.zarr /Volumes/CER/WFRT/FWI/Data/daily

xr_dir = '/Volumes/cer/fireweather/data/rerun/'

hourly_file_dir  = str(xr_dir) + "/fwf-hourly-2020091200.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = str(xr_dir) + "/fwf-daily-2020091200.zarr"
daily_ds = xr.open_zarr(daily_file_dir)

time_ind = 18
time = np.datetime_as_string(hourly_ds.Time[time_ind], unit='h')
initial = np.datetime_as_string(hourly_ds.Time[0], unit='h')
valid = np.datetime_as_string(hourly_ds.Time[time_ind], unit='h')
print(time)

# %%
Plot_Title = "ALL FWI:  "
day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
fig, ax = plt.subplots(3,2, figsize=(12,8))
# fig, ax = plt.subplots( figsize=(12,8))
fig.suptitle(Plot_Title + day, fontsize=16)
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
cmap = plt.cm.jet


ffmc = np.array(hourly_ds.F[18])
title = "FFMC"
C = ax[0][0].pcolormesh(lons, lats, ffmc, cmap = cmap, vmin = 70, vmax = 100)
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].set_title(title + f" max {round(np.nanmax(ffmc),1)}  min {round(np.nanmin(ffmc),1)} mean {round(np.mean(ffmc),1)}")

isi = np.array(hourly_ds.R[18])
title = "ISI"
C = ax[1][0].pcolormesh(lons, lats, isi, cmap = cmap, vmin = 0, vmax = 15)
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].set_title(title + f" max {round(np.nanmax(isi),1)}  min {round(np.nanmin(isi),1)} mean {round(np.mean(isi),1)}")

fwi = np.array(hourly_ds.S[18])
title = "FWI"
C = ax[2][0].pcolormesh(lons, lats, fwi, cmap = cmap, vmin = 0, vmax = 30)
clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
ax[2][0].set_title(title + f" max {round(np.nanmax(fwi),1)}  min {round(np.nanmin(fwi),1)} mean {round(np.mean(fwi),1)}")

dmc = np.array(daily_ds.P[0])
title = "DMC"
C = ax[0][1].pcolormesh(lons, lats, dmc, cmap = cmap, vmin = 0, vmax = 60)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].set_title(title + f" max {round(np.nanmax(dmc),1)}  min {round(np.nanmin(dmc),1)} mean {round(np.mean(dmc),1)}")

dc = np.array(daily_ds.D[0])
title = "DC"
C = ax[1][1].pcolormesh(lons, lats, dc, cmap = cmap, vmin = 40, vmax = 400)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].set_title(title + f" max {round(np.nanmax(dc),1)}  min {round(np.nanmin(dc),1)} mean {round(np.mean(dc),1)}")


bui = np.array(daily_ds.U[0])
title = "BUI"
C = ax[2][1].pcolormesh(lons, lats, bui, cmap = cmap, vmin = 0, vmax = 90)
clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
ax[2][1].set_title(title + f" max {round(np.nanmax(bui),1)}  min {round(np.nanmin(bui),1)} mean {round(np.mean(bui),1)}")






fig.savefig(str(root_dir) + "/images/ALL_FWI/" + day  + "-new.png")

plt.show()
print("Run Time: ", datetime.now() - startTime)


