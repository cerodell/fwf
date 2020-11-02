import context
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from glob import glob

import matplotlib.colors
import matplotlib.pyplot as plt

from utils.fireutils import firestats, read_zarr, extract_poly_coords
from datetime import datetime, date, timedelta
from context import data_dir




filein = str(data_dir) + '/shp/' + "perimeters.shp"
df = gpd.read_file(filein)
df = df.to_crs(epsg=4326)
df = firestats(df)
df = df.loc[df['AREA'] > df['AREA'].mean()]
fire_id = df['UID'].values

# fire_ds_dir = str(data_dir) + str(f'/xr/fwf-fireid-5143029.zarr/')
# fire_ds = xr.open_zarr(fire_ds_dir)

fire_ds_dir = str(data_dir) + str(f'/xr/fwf-fireid-*')
paths = sorted(glob(fire_ds_dir))

fire_ds_list, fireID_list = [], []
for path in paths:
    fire_ds = xr.open_zarr(path)
    fireID_list.append(fire_ds.fireID)
    fire_ds_list.append(fire_ds)


df = df[df['UID'].isin(fireID_list)]
fire_id = df['UID'].values

index_list = []
for i in range(len(fire_id)):
    index = fireID_list.index(fire_id[i])
    index_list.append(index)


fig, ax = plt.subplots(1,1, figsize=(12,8))
for i in index_list:
    ax.plot(fire_ds_list[i].F.mean(dim = ('south_north', 'west_east' )))



# index = fireID_list.index(5141900)

# test_ds = fire_ds_list[index]
# mean_ds = test_ds.mean(dim = ('south_north', 'west_east' ))


# # hours = mean_ds.Time.values
# # hours = hours[:-1]
# # days = np.arange(hours[0], hours[-1], timedelta(days=1))
# # days = days[::-1]
# # hours24 = np.arange(0,24,1)

# # # hours = np.reshape(hours, (len(days), 24))

# # hhours, ddays = np.meshgrid(hours24, days)
# # ffmc  =mean_ds.F.values[:-2]
# # ffmc = np.reshape(ffmc[::-1], hhours.shape)


# # fig, ax = plt.subplots(1,1, figsize=(12,8))
# # cmap = plt.cm.jet
# # C = ax.pcolormesh(hhours, ddays, ffmc, cmap = cmap)
# # clb = fig.colorbar(C, ax = ax, fraction=0.054, pad=0.04)



# test_df = df.loc[df['UID'] == 5141900]
# # Plot_Title = "ALL FWI:  "
# fig, ax = plt.subplots(1,1, figsize=(12,8))
# # fig, ax = plt.subplots( figsize=(12,8))
# # fig.suptitle(Plot_Title + day, fontsize=16)
# fig.subplots_adjust(hspace=0.8)
# lats, lons = np.array(test_ds.XLAT), np.array(test_ds.XLONG)
# cmap = plt.cm.jet
# from descartes import PolygonPatch


# ffmc = np.array(test_ds.F[0])
# title = "FFMC"
# C = ax.pcolormesh(lons, lats, ffmc, cmap = cmap, vmin = 70, vmax = 100)
# clb = fig.colorbar(C, ax = ax, fraction=0.054, pad=0.04)
# ax.set_title(title + f" max {round(np.nanmax(ffmc),1)}  min {round(np.nanmin(ffmc),1)} mean {round(np.mean(ffmc),1)}")
# # ax.add_patch(PolygonPatch(test_df['geometry'], alpha=0.5, zorder=2 ))
# test_df.plot(ax= ax)