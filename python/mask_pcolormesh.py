import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from utils.geoutils import mask, mycontourf_to_geojson
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()


import matplotlib as mpl
import matplotlib.colors
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES)



### BRing in zarr FWF forecast data 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
# hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020071700.zarr") 
# daily_file_dir = str(xr_dir) + str("/fwf-daily-2020071700.zarr")
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

### Bring in WRF Data and open
# 
# wrf_folder = date.today().strftime('/%y%m%d00/')
wrf_folder = '/20071700/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


wrf_file = Dataset(wrf_file_dir[-1],'r')


### Get Land Mask and Lake Mask data
LANDMASK        = getvar(wrf_file, "LANDMASK")
LAKEMASK        = getvar(wrf_file, "LAKEMASK")
SNOWC           = getvar(wrf_file, "SNOWC")
SNOWC[:,:600]   = 0

def mask(ds_unmasked, LANDMASK, LAKEMASK, SNOWC):
    ds = xr.where(LANDMASK == 1, ds_unmasked, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    # ds = xr.where(LAKEMASK == 0, ds, np.nan)
    # ds = ds.transpose("time", "south_north", "west_east")
    ds = xr.where(SNOWC == 0, ds, np.nan)
    ds = ds.transpose("time", "south_north", "west_east")
    ds['Time'] = ds_unmasked['Time']
    return ds

hourly_ds = mask(hourly_ds, LANDMASK, LAKEMASK, SNOWC)
daily_ds  = mask(daily_ds, LANDMASK, LAKEMASK, SNOWC)


# %%
# Plot_Title = "ALL FWI:  "
# day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
# fig, ax = plt.subplots()
# fig.suptitle(Plot_Title + day, fontsize=16)
# fig.subplots_adjust(hspace=0.8)
# lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
# cmap = plt.cm.jet
# Cnorm = matplotlib.colors.Normalize(vmin= 50, vmax =100)
# levels = np.array([0, 50, 60, 70, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 100 ])



# ffmc = np.array(hourly_ds.F[0])
# title = "FFMC"
# C = ax.contourf(lons, lats, ffmc, cmap = cmap, norm = Cnorm, levels=levels, extend="both")
# clb = fig.colorbar(C, ax = ax, fraction=0.054, pad=0.04)
# ax.set_title(title + f" max {round(np.nanmax(ffmc),1)}  min {round(np.nanmin(ffmc),1)} mean {round(np.nanmean(ffmc),1)}")

# fig.savefig(str(root_dir) + "/images/ffmc/" + day  + "-ffmc.png", dpi = 300)


# %%

Plot_Title = "ALL FWI:  "
day  = str(np.array(daily_ds.Time[0], dtype ='datetime64[D]'))
fig, ax = plt.subplots(3,2, figsize=(12,8))
fig.suptitle(Plot_Title + day, fontsize=16)
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
cmap = plt.cm.jet

Cnorm = matplotlib.colors.Normalize(vmin= 60, vmax =100)
levels = np.array([0, 60, 68, 72, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 100 ])

ffmc = np.array(hourly_ds.F[18])
title = "FFMC"
C = ax[0][0].contourf(lons, lats, ffmc, cmap = cmap, norm = Cnorm, levels=levels, extend="both")
clb = fig.colorbar(C, ax = ax[0][0], fraction=0.054, pad=0.04)
ax[0][0].set_title(title + f" max {round(np.nanmax(ffmc),1)}  min {round(np.nanmin(ffmc),1)} mean {round(np.nanmean(ffmc),1)}")




vmin, vmax = 0, 15
levels = np.linspace(vmin,vmax,15)
Cnorm = matplotlib.colors.Normalize(vmin= vmin, vmax =vmax)
isi = np.array(hourly_ds.R[18])
title = "ISI"
C = ax[1][0].contourf(lons, lats, isi, cmap = cmap,  norm = Cnorm, levels=levels, extend="both")
clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
ax[1][0].set_title(title + f" max {round(np.nanmax(isi),1)}  min {round(np.nanmin(isi),1)} mean {round(np.nanmean(isi),1)}")


fwi = np.array(hourly_ds.S[18])
title = "FWI"
vmin, vmax = 0, 30
levels = np.linspace(vmin,vmax,15)
Cnorm = matplotlib.colors.Normalize(vmin= vmin, vmax =vmax)
# levels = np.array([0, 4, 8, 12, 16, 20, 24, 26, 28, 30, 45, 65, 80 ])
C = ax[2][0].contourf(lons, lats, fwi, cmap = cmap, norm = Cnorm, levels=levels, extend="both")
clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
ax[2][0].set_title(title + f" max {round(np.nanmax(fwi),1)}  min {round(np.nanmin(fwi),1)} mean {round(np.nanmean(fwi),1)}")

dmc = np.array(daily_ds.P[0])
title = "DMC"
C = ax[0][1].pcolormesh(lons, lats, dmc, cmap = cmap, vmin = 0, vmax = 60)
clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
ax[0][1].set_title(title + f" max {round(np.nanmax(dmc),1)}  min {round(np.nanmin(dmc),1)} mean {round(np.nanmean(dmc),1)}")

dc = np.array(daily_ds.D[0])
title = "DC"
C = ax[1][1].pcolormesh(lons, lats, dc, cmap = cmap, vmin = 40, vmax = 400)
clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
ax[1][1].set_title(title + f" max {round(np.nanmax(dc),1)}  min {round(np.nanmin(dc),1)} mean {round(np.nanmean(dc),1)}")


bui = np.array(daily_ds.U[0])
title = "BUI"
C = ax[2][1].pcolormesh(lons, lats, bui, cmap = cmap, vmin = 0, vmax = 90)
clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
ax[2][1].set_title(title + f" max {round(np.nanmax(bui),1)}  min {round(np.nanmin(bui),1)} mean {round(np.nanmean(bui),1)}")

fig.savefig(str(root_dir) + "/images/all_fwi/" + day  + ".png")

# plt.show()
print("Run Time: ", datetime.now() - startTime)

# %%
