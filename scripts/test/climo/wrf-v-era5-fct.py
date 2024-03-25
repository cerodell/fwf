import context
import salem
import json
import numpy as np
import pandas as pd
import xarray as xr
import seaborn as sns

import matplotlib.pyplot as plt

from context import data_dir, root_dir
from utils.geoutils import make_KDtree

plt.rcParams["text.usetex"] = False


save_fig = False
doi = pd.Timestamp("2021-06-29")
domain = "d02"
model = "wrf"


## Open gridded static
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model.lower()}-{domain}.nc"
)

era_F = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/{doi.strftime('%Y%m')}/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc"
).isel(time=slice(6, 24))
era_W = xr.open_dataset(
    f'/Volumes/WFRT-Ext25/ecmwf/era5-land/{doi.strftime("%Y%m")}/era5-land-{doi.strftime("%Y%m%d%H")}.nc'
).isel(time=slice(6, 24))
era_W["W"] = ((era_W["v10"] ** 2 + era_W["u10"] ** 2) ** 0.5) * 3.6

wrf_F = salem.open_xr_dataset(
    f"/Volumes/WFRT-Ext21/fwf-data/wrf/{domain}/01/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc"
).isel(time=slice(0, 18))

# try:
#     wrf_W = salem.open_xr_dataset(f"/Volumes/Scratch/fwf-data/wrf/{domain}/{doi.strftime('%Y%m')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc").isel(time=slice(0,18))[['W','T','H','r_o']].transpose(('time', 'west_east', 'south_north'))
# except:
#     wrf_W = salem.open_xr_dataset(f"/Volumes/WFRT-Ext23/fwf-data/wrf/{domain}/{doi.strftime('%Y%m')}/fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc").isel(time=slice(0,18))[['W','T','H','r_o']]
wrf_W = wrf_F[["W", "T", "H", "r_o"]]
# mask = xr.open_dataset("/Volumes/WFRT-Ext25/ecmwf/era5-land/202201/era5-land-2022010100.nc").isel(time =0).notnull().rename({'t2m': 'S'})['S'].values


era_F = wrf_F.salem.transform(era_F)
era_W = wrf_F.salem.transform(era_W)

wrf_F = wrf_F.where(era_F["F"].notnull().isel(time=0).values)
wrf_W = wrf_W.where(era_F["F"].notnull().isel(time=0).values)


dff_ds = era_W.mean("time") - wrf_W.mean("time")
dff_ds.attrs = wrf_W.attrs
dff_ds["W"].attrs = wrf_W.attrs

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(1, 1, 1)
dff_ds["W"].salem.quick_map(ax=ax, vmin=-20, vmax=20, cmap="coolwarm", extend="both")

wrf_WSP = wrf_W["W"].values.ravel()
wrf_WSP = wrf_WSP[~np.isnan(wrf_WSP)]
wrf_WSP = wrf_WSP[np.isfinite(wrf_WSP)]

era_WSP = era_W["W"].values.ravel()
era_WSP = era_WSP[~np.isnan(era_WSP)]
era_WSP = era_WSP[np.isfinite(era_WSP)]


fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(1, 1, 1)
sc = ax.hexbin(wrf_WSP, era_WSP, cmap="cubehelix_r")
ax.axline((0, 0), slope=1, color="k", lw=0.5)
ax.set_xlabel("WRF")
ax.set_ylabel("ERA-Land")
ax.set_title("Wind Speed")

# Create color bar
cbar = fig.colorbar(sc, ax=ax)
cbar.set_label("Count")
