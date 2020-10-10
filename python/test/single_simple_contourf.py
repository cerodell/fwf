import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
# from geoutils import mask, contourf_to_geojson
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()


import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES)

### Open color map json
with open('/bluesky/fireweather/fwf/json/colormaps-new.json') as f:
  cmaps = json.load(f)



### BRing in zarr FWF forecast data 
hourly_file_dir = str(xr_dir) + str("/current/fwf-hourly-current.zarr") 
daily_file_dir = str(xr_dir) + str("/current/fwf-daily-current.zarr") 

hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

center_lon = float(hourly_ds.CEN_LON)
### Bring in WRF Data and open

wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = '/20061700/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


wrf_file = Dataset(wrf_file_dir[-1],'r')


### Get Land Mask and Lake Mask data
LANDMASK        = getvar(wrf_file, "LANDMASK")
LANDMASK        = getvar(wrf_file, "LANDMASK")
LAKEMASK        = getvar(wrf_file, "LAKEMASK")
SNOWC           = getvar(wrf_file, "SNOWC")
proj_ = get_cartopy(SNOWC)

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

# hourly_ds = mask(hourly_ds, LANDMASK, LAKEMASK, SNOWC)
# daily_ds  = mask(daily_ds, LANDMASK, LAKEMASK, SNOWC)


# proj_ = crs.NorthPolarStereo(central_longitude=center_lon)



fig = plt.figure(frameon=False)
ax = plt.axes()
day  = str(np.array(hourly_ds.Time[-1], dtype ='datetime64[h]'))
colors = cmaps['SNW']['colors']
levels = cmaps['SNW']['levels']
vmin, vmax = cmaps['SNW']['vmin'], cmaps['SNW']['vmax']

snw = np.array(hourly_ds.SNW[-1])

lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
Cnorm = matplotlib.colors.Normalize(vmin= 0, vmax =140)

cs = ax.contourf(lons, lats, snw, colors = colors, norm = Cnorm, \
     levels=levels, extend="both")
clb = fig.colorbar(cs, fraction=0.054, pad=0.04)

fig.savefig(str(root_dir) + "/images/weather/snw-" + day  + ".png", dpi = 300)

# clb = fig.colorbar(C, ax = ax, fraction=0.054, pad=0.04)
# plt.title(title + f" max {round(np.nanmax(snw),1)}  min {round(np.nanmin(snw),1)} mean {round(np.mean(snw),1)}")

# isi = np.array(hourly_ds.R[18])
# title = "ISI"
# C = ax[1][0].pcolormesh(lons, lats, isi, cmap = cmap, vmin = 0, vmax = 15)
# clb = fig.colorbar(C, ax = ax[1][0], fraction=0.054, pad=0.04)
# ax[1][0].set_title(title + f" max {round(np.nanmax(isi),1)}  min {round(np.nanmin(isi),1)} mean {round(np.mean(isi),1)}")

# fwi = np.array(hourly_ds.S[18])
# title = "FWI"
# C = ax[2][0].pcolormesh(lons, lats, fwi, cmap = cmap, vmin = 0, vmax = 30)
# clb = fig.colorbar(C, ax = ax[2][0], fraction=0.054, pad=0.04)
# ax[2][0].set_title(title + f" max {round(np.nanmax(fwi),1)}  min {round(np.nanmin(fwi),1)} mean {round(np.mean(fwi),1)}")

# dmc = np.array(daily_ds.P[0])
# title = "DMC"
# C = ax[0][1].pcolormesh(lons, lats, dmc, cmap = cmap, vmin = 0, vmax = 60)
# clb = fig.colorbar(C, ax = ax[0][1], fraction=0.054, pad=0.04)
# ax[0][1].set_title(title + f" max {round(np.nanmax(dmc),1)}  min {round(np.nanmin(dmc),1)} mean {round(np.mean(dmc),1)}")

# dc = np.array(daily_ds.D[0])
# title = "DC"
# C = ax[1][1].pcolormesh(lons, lats, dc, cmap = cmap, vmin = 40, vmax = 400)
# clb = fig.colorbar(C, ax = ax[1][1], fraction=0.054, pad=0.04)
# ax[1][1].set_title(title + f" max {round(np.nanmax(dc),1)}  min {round(np.nanmin(dc),1)} mean {round(np.mean(dc),1)}")


# bui = np.array(daily_ds.U[0])
# title = "BUI"
# C = ax[2][1].pcolormesh(lons, lats, bui, cmap = cmap, vmin = 0, vmax = 90)
# clb = fig.colorbar(C, ax = ax[2][1], fraction=0.054, pad=0.04)
# ax[2][1].set_title(title + f" max {round(np.nanmax(bui),1)}  min {round(np.nanmin(bui),1)} mean {round(np.mean(bui),1)}")

# fig.savefig(str(root_dir) + "/Images/" + day  + ".png", transparent=True, bbox_inches='tight', pad_inches=0)

plt.show()
print("Run Time: ", datetime.now() - startTime)


