import context
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from datetime import datetime, date, timedelta

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll)


from context import data_dir, root_dir

startTime = datetime.now()


## Set path to data
filein = str(data_dir) + '/domain/n_hem.csv'

## Read data
df = pd.read_csv(filein)

## Make 1D arrays of lat and lon
lat = np.array(df['lat_degr'])
lon = np.array(df['lon_degr'])

### Open old WRF domain
filein = str(data_dir) + '/domain/wrfout_d02_old.nc'
ds_wrf_old = xr.open_dataset(filein)

### Open new WRF domain
filein = str(data_dir) + '/domain/wrfout_d02_new.nc'
ds_wrf_new = xr.open_dataset(filein)

### Open new hysplit domain
filein = str(data_dir) + '/domain/dispersion.nc'
ds_hysplit = xr.open_dataset(filein)


Plot_Title = "Model Domains"
save_file = 'model-domains'
fig, ax = plt.subplots(figsize=[12,8])
ax.set_title(Plot_Title , fontsize=20, weight='bold')
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(ds_wrf_old.XLAT), np.array(ds_wrf_old.XLONG)
lats, lons = lats[0], lons[0]


ax.plot(lons[0],lats[0], color ='blue', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[-1].T,lats[-1].T, color ='blue', linewidth= 2 , zorder=8, alpha =1)
ax.plot(lons[:,0],lats[:,0], color ='blue', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[:,-1].T,lats[:,-1].T, color ='blue', linewidth= 2 , zorder=8, alpha =1, label = 'Current 12km WRF')

lats, lons = np.array(ds_wrf_new.XLAT), np.array(ds_wrf_new.XLONG)
lats, lons = lats[0], lons[0]
lons = np.where(lons < 179, lons, np.nan)

ax.plot(lons[0],lats[0], color ='red', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[-1].T,lats[-1].T, color ='red', linewidth= 2 , zorder=8, alpha =1)
ax.plot(lons[:,0],lats[:,0], color ='red', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[:,-1].T,lats[:,-1].T, color ='red', linewidth= 2 , zorder=8, alpha =1, label = 'New 12km WRF')



lat_i, lon_i = ds_hysplit.YORIG, ds_hysplit.XORIG
nrows, ncols = ds_hysplit.NROWS, ds_hysplit.NCOLS
xcell, ycell = ds_hysplit.XCELL, ds_hysplit.YCELL
lat_f = (nrows * ycell) + lat_i
lon_f = (ncols * xcell) + lon_i
lats = np.arange(lat_i,lat_f+ycell,ycell)
lons = np.arange(lon_i,lon_f+xcell,xcell)
lons, lats = np.meshgrid(lons, lats)


ax.plot(lons[0],lats[0], color ='k', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[-1].T,lats[-1].T, color ='k', linewidth= 2 , zorder=8, alpha =1)
ax.plot(lons[:,0],lats[:,0], color ='k', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[:,-1].T,lats[:,-1].T, color ='k', linewidth= 2 , zorder=8, alpha =1, label = 'Hysplit')

ax.plot(lon, lat)
ax.set_xlabel('Lon')
ax.set_ylabel('Lat')

ax.set_xlim([-190,-30])
ax.set_ylim([25,85])


ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, .98),
    ncol=3,
    fancybox=True,
    shadow=True,
)
fig.savefig(str(root_dir) + "/images/domain/" + save_file  + ".png", dpi=240)

# plt.show()

# %%
