import context
import math
import pickle
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as crs
from netCDF4 import Dataset
import cartopy.feature as cfeature
import timezonefinder, pytz
from datetime import datetime, date
import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt
from context import root_dir, xr_dir, data_dir, wrf_dir
from wrf import (getvar, g_uvmet,get_cartopy, ll_to_xy)


startTime = datetime.now()

## Set path to data
filein = str(data_dir) + '/n_hem.csv'

## Read data
df = pd.read_csv(filein)

## Make 1D arrays of lat and lon
lat = np.array(df['lat_degr'])
lon = np.array(df['lon_degr'])




wrf_filein = date.today().strftime('/%y%m%d00/wrfout_d03_2020-10-25_12:00:00')
wrf_file_dir = str(wrf_dir) + wrf_filein
wrf_ds = xr.open_dataset(wrf_file_dir)

time = str(wrf_ds.Times.values[0])
valid = time[2:-1]
print(valid)

wrf_file = Dataset(wrf_file_dir,'r')

per_p = getvar(wrf_file, 'P')
per_p = per_p.values
base_p = getvar(wrf_file, 'PB')
base_p = base_p.values
p = base_p + per_p
p = p[0,:,:]



rh = getvar(wrf_file, "rh2")
rh = rh.values
temp = getvar(wrf_file, "tk")
temp = temp.values
temp = temp[0,:,:]

qv = getvar(wrf_file, "QVAPOR")
qv = qv.values
qv = qv[0,:,:]


xlim, ylim = [-134,-110], [44,58]

zorder, alpha, col, lwidth = 10, 1, 'k', 0.2

Plot_Title = "Valid:  "
fig, ax = plt.subplots(2,2, figsize=(12,8))
# ax = plt.axes(projection=cart_proj)
fig.suptitle(Plot_Title + valid, fontsize=12)
fig.subplots_adjust(hspace=0.8)
lats, lons = getvar(wrf_file, "XLAT"), getvar(wrf_file, "XLONG")
lats, lons = lats.values, lons.values
cmap = plt.cm.jet



print(np.round(np.max(temp)))

title = "Temp K 2m"
C = ax[0][0].pcolormesh(lons, lats, temp, cmap = cmap)
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[0][0].set_title(title + f" \n max {np.round(np.max(temp))}  min {np.round(np.nanmin(temp))} mean {np.round(np.mean(temp))}")
ax[0][0].set_xlim(xlim[0],xlim[1])
ax[0][0].set_ylim(ylim[0],ylim[1])

title = "RH % 2m"
cmap = plt.cm.YlGn
C = ax[1][0].pcolormesh(lons, lats, rh, cmap = cmap)
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[1][0].set_title(title + f" \n max {np.round(np.max(rh))}  min {np.round(np.nanmin(rh))} mean {np.round(np.mean(rh))}")
ax[1][0].set_xlim(xlim[0],xlim[1])
ax[1][0].set_ylim(ylim[0],ylim[1])

title = "Water vapor mixing ratio 2m kg kg-1"
cmap = plt.cm.YlGn

C = ax[1][1].pcolormesh(lons, lats, qv, cmap = cmap)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[1][1].set_title(title + f" \n max {np.round(np.max(qv),4)}  min {np.round(np.nanmin(qv),4)} mean {np.round(np.mean(qv), 4)}")
ax[1][1].set_xlim(xlim[0],xlim[1])
ax[1][1].set_ylim(ylim[0],ylim[1])


cmap = plt.cm.RdYlBu_r
title = "Full pressure (perturbation + base state pressure)"
C = ax[0][1].pcolormesh(lons, lats, p, cmap = cmap)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
ax[0][1].set_title(title + f" \n max {np.round(np.max(p))}  min {np.round(np.nanmin(p))} mean {np.round(np.mean(p))}")
ax[0][1].set_xlim(xlim[0],xlim[1])
ax[0][1].set_ylim(ylim[0],ylim[1])

# cmap = plt.cm.RdYlBu_r
# title = "qvapor"
# C = ax[1][1].pcolormesh(lons, lats, qvapor, cmap = cmap)
# clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
# ax[1][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
# ax[1][1].set_title(title + f" max {np.round(np.max(qvapor))}  min {np.round(np.nanmin(qvapor))} mean {np.round(np.mean(qvapor))}")
# ax[1][1].set_xlim(xlim[0],xlim[1])
# ax[1][1].set_ylim(ylim[0],ylim[1])

# cross = wrf_ds.T - wrf_ds.H


# cross = np.array(cross[time_ind])
# title = "Cross Over"
# C = ax[2][1].pcolormesh(lons, lats, cross, cmap = cmap)
# clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
# ax[2][1].plot(lon, lat, zorder =zorder , alpha = alpha, color = col, linewidth = lwidth )
# ax[2][1].set_title(title + f" max {np.round(np.max(cross))}  min {np.round(np.nanmin(cross))} mean {np.round(np.mean(cross))}")
# ax[2][1].set_xlim(xlim[0],xlim[1])
# ax[2][1].set_ylim(ylim[0],ylim[1])
# fig.tight_layout()

fig.savefig(str(root_dir) + "/images/all_fwi/" + valid  + "-wx.png", dpi = 300)






print("Run Time: ", datetime.now() - startTime)


