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
from context import root_dir, xr_dir, data_dir


startTime = datetime.now()

## Set path to data
filein = str(data_dir) + '/n_hem.csv'

## Read data
df = pd.read_csv(filein)

## Make 1D arrays of lat and lon
lat = np.array(df['lat_degr'])
lon = np.array(df['lon_degr'])


hourly_file_dir  = str(xr_dir) + "/current/fwf-hourly-current.zarr"
hourly_ds = xr.open_zarr(hourly_file_dir)

daily_file_dir  = str(xr_dir) + "/current/fwf-daily-current.zarr"
daily_ds = xr.open_zarr(daily_file_dir)

time_ind = -1
time = np.datetime_as_string(hourly_ds.Time[time_ind], unit='h')
initial = np.datetime_as_string(hourly_ds.Time[0], unit='h')
valid = np.datetime_as_string(hourly_ds.Time[time_ind], unit='h')
print(time)

# %%
Plot_Title = "ALL FWI:  "
day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
fig, ax = plt.subplots(3,2, figsize=(12,8))
# ax = plt.axes(projection=cart_proj)
fig.suptitle(Plot_Title + day, fontsize=12)
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
cmap = plt.cm.jet

xlim, ylim = [-134,-110], [44,58]
zorder, alpha, col, lwidth = 10, 1, 'k', 0.2
ffmc = np.array(hourly_ds.F[time_ind])
title = "FFMC"
C = ax[0][0].pcolormesh(lons, lats, ffmc, cmap = cmap, vmin = 40, vmax = 100)
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth)
ax[0][0].set_title(title + f" max {np.round(np.max(ffmc))}  min {np.round(np.nanmin(ffmc))} mean {np.round(np.mean(ffmc))}")
ax[0][0].set_xlim(xlim[0],xlim[1])
ax[0][0].set_ylim(ylim[0],ylim[1])


isi = np.array(hourly_ds.R[time_ind])
title = "ISI"
C = ax[1][0].pcolormesh(lons, lats, isi, cmap = cmap, vmin = 0, vmax = 20)
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[1][0].set_title(title + f" max {np.round(np.max(isi))}  min {np.round(np.nanmin(isi))} mean {np.round(np.mean(isi))}")
ax[1][0].set_xlim(xlim[0],xlim[1])
ax[1][0].set_ylim(ylim[0],ylim[1])

fwi = np.array(hourly_ds.S[time_ind])
title = "FWI"
C = ax[2][0].pcolormesh(lons, lats, fwi, cmap = cmap, vmin = 0, vmax = 30)
clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
ax[2][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[2][0].set_title(title + f" max {np.round(np.max(fwi))}  min {np.round(np.nanmin(fwi))} mean {np.round(np.mean(fwi))}")
ax[2][0].set_xlim(xlim[0],xlim[1])
ax[2][0].set_ylim(ylim[0],ylim[1])

dmc = np.array(daily_ds.P[0])
title = "DMC"
C = ax[0][1].pcolormesh(lons, lats, dmc, cmap = cmap, vmin = 0, vmax = 100)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[0][1].set_title(title + f" max {np.round(np.max(dmc))}  min {np.round(np.nanmin(dmc))} mean {np.round(np.mean(dmc))}")
ax[0][1].set_xlim(xlim[0],xlim[1])
ax[0][1].set_ylim(ylim[0],ylim[1])

dc = np.array(daily_ds.D[0])
title = "DC"
C = ax[1][1].pcolormesh(lons, lats, dc, cmap = cmap, vmin = 40, vmax = 500)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[1][1].set_title(title + f" max {np.round(np.max(dc))}  min {np.round(np.nanmin(dc))} mean {np.round(np.mean(dc))}")
ax[1][1].set_xlim(xlim[0],xlim[1])
ax[1][1].set_ylim(ylim[0],ylim[1])

bui = np.array(daily_ds.U[0])
title = "BUI"
C = ax[2][1].pcolormesh(lons, lats, bui, cmap = cmap, vmin = 0, vmax = 120)
clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
ax[2][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[2][1].set_title(title + f" max {np.round(np.max(bui))}  min {np.round(np.nanmin(bui))} mean {np.round(np.mean(bui))}")
ax[2][1].set_xlim(xlim[0],xlim[1])
ax[2][1].set_ylim(ylim[0],ylim[1])


fig.tight_layout()
fig.savefig(str(root_dir) + "/images/all_fwi/" + day  + ".png", dpi = 300)


Plot_Title = "ALL WX:  "
day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
fig, ax = plt.subplots(3,2, figsize=(12,8))
# ax = plt.axes(projection=cart_proj)
fig.suptitle(Plot_Title + day, fontsize=12)
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
cmap = plt.cm.jet


temp = np.array(hourly_ds.T[time_ind])
print(np.round(np.max(temp)))

title = "TEMP C"
C = ax[0][0].pcolormesh(lons, lats, temp, cmap = cmap)
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[0][0].set_title(title + f" max {np.round(np.max(temp))}  min {np.round(np.nanmin(temp))} mean {np.round(np.mean(temp))}")
ax[0][0].set_xlim(xlim[0],xlim[1])
ax[0][0].set_ylim(ylim[0],ylim[1])

rh = np.array(hourly_ds.H[time_ind])
title = "RH %"
cmap = plt.cm.YlGn
C = ax[1][0].pcolormesh(lons, lats, rh, cmap = cmap)
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[1][0].set_title(title + f" max {np.round(np.max(rh))}  min {np.round(np.nanmin(rh))} mean {np.round(np.mean(rh))}")
ax[1][0].set_xlim(xlim[0],xlim[1])
ax[1][0].set_ylim(ylim[0],ylim[1])

wsp = np.array(hourly_ds.W[time_ind])
title = "WSP km/hr"
cmap = plt.cm.jet

C = ax[2][0].pcolormesh(lons, lats, wsp, cmap = cmap)
clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
ax[2][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[2][0].set_title(title + f" max {np.round(np.max(wsp))}  min {np.round(np.nanmin(wsp))} mean {np.round(np.mean(wsp))}")
ax[2][0].set_xlim(xlim[0],xlim[1])
ax[2][0].set_ylim(ylim[0],ylim[1])

qpf = np.array(hourly_ds.r_o[time_ind])
title = "RAIN mm"
C = ax[0][1].pcolormesh(lons, lats, qpf, cmap = cmap, vmin = 0, vmax = 60)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[0][1].set_title(title + f" max {np.round(np.max(qpf))}  min {np.round(np.nanmin(qpf))} mean {np.round(np.mean(qpf))}")
ax[0][1].set_xlim(xlim[0],xlim[1])
ax[0][1].set_ylim(ylim[0],ylim[1])

cwc = (hourly_ds.T - 30) - (hourly_ds.H - 30) + (hourly_ds.W - 30)
cmap = plt.cm.RdYlBu_r

cwc = np.array(cwc[time_ind])
title = "CWC"
C = ax[1][1].pcolormesh(lons, lats, cwc, cmap = cmap)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[1][1].set_title(title + f" max {np.round(np.max(cwc))}  min {np.round(np.nanmin(cwc))} mean {np.round(np.mean(cwc))}")
ax[1][1].set_xlim(xlim[0],xlim[1])
ax[1][1].set_ylim(ylim[0],ylim[1])

cross = hourly_ds.T - hourly_ds.H


cross = np.array(cross[time_ind])
title = "Cross Over"
C = ax[2][1].pcolormesh(lons, lats, cross, cmap = cmap)
clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
ax[2][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[2][1].set_title(title + f" max {np.round(np.max(cross))}  min {np.round(np.nanmin(cross))} mean {np.round(np.mean(cross))}")
ax[2][1].set_xlim(xlim[0],xlim[1])
ax[2][1].set_ylim(ylim[0],ylim[1])
fig.tight_layout()

fig.savefig(str(root_dir) + "/images/all_fwi/" + day  + "-wx.png", dpi = 300)






print("Run Time: ", datetime.now() - startTime)


