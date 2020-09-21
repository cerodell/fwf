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

xr_dir = '/Volumes/cer/fireweather/data/rerun/'

hourly_file_dir  = str(xr_dir) + "/fwf-hourly-2020090100.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = str(xr_dir) + "/fwf-daily-2020090100.zarr"
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
# ax = plt.axes(projection=cart_proj)
fig.suptitle(Plot_Title + day, fontsize=16)
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
cmap = plt.cm.jet


ffmc = np.array(hourly_ds.F[18])
title = "FFMC"
C = ax[0][0].pcolormesh(lons, lats, ffmc, cmap = cmap, vmin = 40, vmax = 100)
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].set_title(title + f" max {np.round(np.max(ffmc))}  min {np.round(np.nanmin(ffmc))} mean {np.round(np.mean(ffmc))}")

isi = np.array(hourly_ds.R[18])
title = "ISI"
C = ax[1][0].pcolormesh(lons, lats, isi, cmap = cmap, vmin = 0, vmax = 20)
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].set_title(title + f" max {np.round(np.max(isi))}  min {np.round(np.nanmin(isi))} mean {np.round(np.mean(isi))}")

fwi = np.array(hourly_ds.S[18])
title = "FWI"
C = ax[2][0].pcolormesh(lons, lats, fwi, cmap = cmap, vmin = 0, vmax = 30)
clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
ax[2][0].set_title(title + f" max {np.round(np.max(fwi))}  min {np.round(np.nanmin(fwi))} mean {np.round(np.mean(fwi))}")

dmc = np.array(daily_ds.P[0])
title = "DMC"
C = ax[0][1].pcolormesh(lons, lats, dmc, cmap = cmap, vmin = 0, vmax = 100)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].set_title(title + f" max {np.round(np.max(dmc))}  min {np.round(np.nanmin(dmc))} mean {np.round(np.mean(dmc))}")

dc = np.array(daily_ds.D[0])
title = "DC"
C = ax[1][1].pcolormesh(lons, lats, dc, cmap = cmap, vmin = 40, vmax = 500)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].set_title(title + f" max {np.round(np.max(dc))}  min {np.round(np.nanmin(dc))} mean {np.round(np.mean(dc))}")


bui = np.array(daily_ds.U[0])
title = "BUI"
C = ax[2][1].pcolormesh(lons, lats, bui, cmap = cmap, vmin = 0, vmax = 120)
clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
ax[2][1].set_title(title + f" max {np.round(np.max(bui))}  min {np.round(np.nanmin(bui))} mean {np.round(np.mean(bui))}")


fig.savefig(str(root_dir) + "/images/all_fwi/" + day  + ".png", dpi = 300)


Plot_Title = "ALL WX:  "
day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
fig, ax = plt.subplots(3,2, figsize=(12,8))
# ax = plt.axes(projection=cart_proj)
fig.suptitle(Plot_Title + day, fontsize=16)
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
cmap = plt.cm.jet


temp = np.array(hourly_ds.T[18])
print(np.round(np.max(temp)))

title = "TEMP C"
C = ax[0][0].pcolormesh(lons, lats, temp, cmap = cmap)
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].set_title(title + f" max {np.round(np.max(temp))}  min {np.round(np.nanmin(temp))} mean {np.round(np.mean(temp))}")

rh = np.array(hourly_ds.H[18])
title = "RH %"
cmap = plt.cm.YlGn
C = ax[1][0].pcolormesh(lons, lats, rh, cmap = cmap)
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].set_title(title + f" max {np.round(np.max(rh))}  min {np.round(np.nanmin(rh))} mean {np.round(np.mean(rh))}")

wsp = np.array(hourly_ds.W[18])
title = "WSP km/hr"
cmap = plt.cm.jet

C = ax[2][0].pcolormesh(lons, lats, wsp, cmap = cmap)
clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
ax[2][0].set_title(title + f" max {np.round(np.max(wsp))}  min {np.round(np.nanmin(wsp))} mean {np.round(np.mean(wsp))}")

qpf = np.array(hourly_ds.r_o[18])
title = "RAIN mm"
C = ax[0][1].pcolormesh(lons, lats, qpf, cmap = cmap, vmin = 0, vmax = 60)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].set_title(title + f" max {np.round(np.max(qpf))}  min {np.round(np.nanmin(qpf))} mean {np.round(np.mean(qpf))}")


cwc = (hourly_ds.T - 30) - (hourly_ds.H - 30) + (hourly_ds.W - 30)
cmap = plt.cm.RdYlBu_r

cwc = np.array(cwc[18])
title = "CWC"
C = ax[1][1].pcolormesh(lons, lats, cwc, cmap = cmap)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].set_title(title + f" max {np.round(np.max(cwc))}  min {np.round(np.nanmin(cwc))} mean {np.round(np.mean(cwc))}")

cross = hourly_ds.T - hourly_ds.H


cross = np.array(cross[18])
title = "Cross Over"
C = ax[2][1].pcolormesh(lons, lats, cross, cmap = cmap)
clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
ax[2][1].set_title(title + f" max {np.round(np.max(cross))}  min {np.round(np.nanmin(cross))} mean {np.round(np.mean(cross))}")


fig.savefig(str(root_dir) + "/images/all_fwi/" + day  + "-wx.png", dpi = 300)






print("Run Time: ", datetime.now() - startTime)


