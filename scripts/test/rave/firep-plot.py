#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from context import root_dir, data_dir
from utils.rave import RAVE
from utils.fwx import FWX
from utils.viirs import VIIRS
from utils.firep import FIREP
from utils.frp import set_axis_postion
from scipy import stats
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import DateFormatter
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.dates as mdates
import cartopy.crs as ccrs

ID = 25586618
# Configuration dictionary for the RAVE and FWX models
config = dict(
    model="wrf",
    trail_name="01",
    method="hourly",
    year="2022",
)

# Initialize RAVE, FWX and VIIRS data with the configuration
firep = FIREP(config=config)
firep_df = firep.open_firep()
fire_i = firep_df.iloc[12:13]
i = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[i : i + 1]


ds = xr.open_zarr(f"/Volumes/WFRT-Ext23/fire/hfi/{config['year']}-{ID}.zarr")
# ## update config to get dates of interest for a fire permitter
# config.update(
#     date_range=[fire_i['initialdat'].to_list()[0],  fire_i['finaldate'].to_list()[0]],
#     fire_i = fire_i
# )
# rave = RAVE(config=config)
# rave_ds = rave.open_rave()

# fwx = FWX(config=config)
# fwx_ds = fwx.open_fwx(var_list=['S', 'HFI'])

# viirs = VIIRS(config=config)
# ndvi_ds = viirs.open_ndvi()
# lai_ds = viirs.open_lai()


# # Subset the datasets for the region of interest (ROI) and compute the results
# rave_roi = rave_ds["FRP_MEAN"].salem.subset(shape=fire_i, margin=1, all_touched=True)
# rave_roi = rave_roi.salem.roi(shape=fire_i, all_touched=True).compute()
# # rave_roi = rave_roi.compute()


# def tranform_ds(ds, rave_roi, fire_i, margin):
#     ds = ds.salem.subset(shape=fire_i, margin=margin, all_touched=True)
#     ds = rave_roi.salem.transform(ds, interp="linear")  # Apply a spatial transform to align datasets
#     ds = ds.salem.roi(shape=fire_i, all_touched=True)
#     try:
#         ds = ds.drop_vars('Time')  # Finalize the FWX dataset
#     except:
#         pass
#     return ds

# fwx_roi = tranform_ds(fwx_ds, rave_roi, fire_i, margin= 1).compute()
# ndvi_roi = tranform_ds(ndvi_ds['NDVI'], rave_roi, fire_i, margin= 20).compute()
# lai_roi = tranform_ds(lai_ds['LAI'], rave_roi, fire_i, margin= 20).compute()


# # rave_roi_daily = rave_roi.resample(time='D').mean()
# # rave_roi_daily = xr.combine_nested([rave_roi_daily.sel(time = i, method = 'nearest') for i in ndvi_roi.time.values], concat_dim='time')
# # rave_roi_daily.coords['time'] = ndvi_roi.time.values

# # Replace zeros with NaN to handle areas without fire data
# # ndvi_roi = xr.where(rave_roi_daily == 0, np.nan, ndvi_roi)
# fwx_roi = xr.where(rave_roi == 0, np.nan, fwx_roi)
# rave_roi = xr.where(rave_roi == 0, np.nan, rave_roi)

# %%
plt.rcParams.update({"font.size": 14})
# Visualization
# doi = pd.Timestamp('2022-05-02T20')
# Create a figure
fig = plt.figure(figsize=(16, 12))

# Create a gridspec layout
# The first row (for maps) is twice the height of the second row (for line plots)
gs = gridspec.GridSpec(2, 2, height_ratios=[3, 1])
g = salem.GoogleVisibleMap(
    x=[fire_i.min_x, fire_i.max_x],
    y=[fire_i.min_y, fire_i.max_y],
    scale=2,  # scale is for more details
    maptype="satellite",
)  # try out also: 'terrain'


ds_time_avg = ds.mean(dim="time")
# First map on the top left
ax = fig.add_subplot(gs[0, 0])
ax.set_title("HEAD FIRE INTENSITY MEAN (kW/m)")
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd")
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_avg["HFI"], overplot=True)
# sm.set_data(fwx_roi.sel(time = doi), overplot=True)
sm.set_scale_bar(
    location=(0.88, 0.94),
)
sm.visualize(ax=ax)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# Second map on the top right
ax = fig.add_subplot(gs[0, 1])
ax.set_title("FIRE RADIATIVE POWER MEAN (MW)")
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd")
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_avg["FRP"], overplot=True)
# sm.set_data(rave_roi.sel(time = doi), overplot=True)
sm.set_scale_bar(location=(0.88, 0.94))
sm.visualize(ax=ax)
ax.set_yticklabels([])
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")


ds_space_avg = ds.mean(dim=("y", "x"))

# First line plot on the bottom left
ax = fig.add_subplot(gs[1, :])
ax.plot(ds_space_avg.time, ds_space_avg["FWI"], color="tab:blue", label="FWI")
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
set_axis_postion(ax, "FWI")


ax = ax.twinx()
ax.plot(ds_space_avg.time, ds_space_avg["HFI"], color="tab:green", label="HFI")
ax.xaxis.set_major_formatter(DateFormatter("%Y-%m-%d"))
plt.setp(ax.get_xticklabels(), rotation=30, ha="left")
set_axis_postion(ax, "HFI (kW/m)", offset=80, side="left")

# Second line plot on the bottom right
ax = ax.twinx()
ax.plot(ds_space_avg.time, ds_space_avg["FRP"], color="tab:red", label="FRP")
set_axis_postion(ax, "FRP (MW)")
ds_nan_free = ds_space_avg.dropna("time")
ax.set_title(
    "FWI pearsonr: "
    + str(np.round(stats.pearsonr(ds_nan_free["FRP"], ds_nan_free["FWI"])[0], 2))
    + "\n HFI pearsonr: "
    + str(np.round(stats.pearsonr(ds_nan_free["FRP"], ds_nan_free["HFI"])[0], 2)),
    loc="right",
)

# Adjust layout for a better fit
fig.tight_layout()
plt.show()
fig.savefig(str(data_dir) + f'/images/rave/{fire_i["id"].values[0]}.png')


# # %%
# fig = plt.figure(figsize=(16, 12))


# GrBrw = LinearSegmentedColormap.from_list('GrBrw', ['#7f4908', '#cb9a4c', '#81c97c', '#00532f'])

# # Create a gridspec layout
# # The first row (for maps) is twice the height of the second row (for line plots)
# gs = gridspec.GridSpec(2, 2, height_ratios=[1, 1])
# g = salem.GoogleVisibleMap(x=[fire_i.min_x, fire_i.max_x], y=[fire_i.min_y, fire_i.max_y],
#                      scale=2,  # scale is for more details
#                      maptype='satellite')  # try out also: 'terrain'


# # First map on the top left
# ax = fig.add_subplot(gs[0, 0])
# ax.set_title('Norm. Diff. Vegetation Index \n'  + f'{str(ndvi_roi["time"].values[0])[:10]}')
# sm = salem.Map(g.grid, factor=1, countries=False, vmin = 0.2, vmax = 1.0, cmap = GrBrw)
# sm.set_shapefile(fire_i, lw=1.5, color='tab:red')
# sm.set_data(ndvi_roi.isel(time = 0), overplot=True)
# sm.set_scale_bar(location=(0.88, 0.94))
# sm.visualize(ax=ax)
# ax.set_xticklabels([])

# # Second map on the top right
# ax = fig.add_subplot(gs[0, 1])
# ax.set_title('Leaf Area Index \n' + f'{str(lai_roi["time"].values[0])[:10]}')
# sm = salem.Map(g.grid, factor=1, countries=False, vmin = 0, vmax = 4, cmap = 'YlGn')
# sm.set_shapefile(fire_i, lw=1.5, color='tab:red')
# sm.set_data(lai_roi.isel(time = 0), overplot=True)
# sm.set_scale_bar(location=(0.88, 0.94))
# sm.visualize(ax=ax)
# ax.set_yticklabels([])
# ax.set_xticklabels([])


# # First map on the top left
# ax = fig.add_subplot(gs[1, 0])
# ax.set_title(f'{str(ndvi_roi["time"].values[1])[:10]}')
# sm = salem.Map(g.grid, factor=1, countries=False, vmin = 0.2, vmax = 1.0, cmap = GrBrw)
# sm.set_shapefile(fire_i, lw=1.5, color='tab:red')
# sm.set_data(ndvi_roi.isel(time = 1), overplot=True)
# sm.set_scale_bar(location=(0.88, 0.94))
# sm.visualize(ax=ax)
# plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

# # Second map on the top right
# ax = fig.add_subplot(gs[1, 1])
# ax.set_title(f'{str(lai_roi["time"].values[1])[:10]}')
# sm = salem.Map(g.grid, factor=1, countries=False, vmin = 0, vmax = 4, cmap = 'YlGn')
# sm.set_shapefile(fire_i, lw=1.5, color='tab:red')
# sm.set_data(lai_roi.isel(time = 1), overplot=True)
# sm.set_scale_bar(location=(0.88, 0.94))
# sm.visualize(ax=ax)
# ax.set_yticklabels([])
# plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
# fig.tight_layout()
# fig.savefig(str(data_dir) + f'/images/rave/{fire_i["id"]}-ndvi-lai.png')

# # %%

# %%
