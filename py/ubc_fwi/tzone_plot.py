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
from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet)


from fwi.utils.ubc_fwi.fwf import FWF
from fwi.utils.wrf.read_wrfout import readwrf
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir, gsuite_dir

startTime = datetime.now()



# %%

wrf_file_dir = "/Volumes/CER/WFRT/FWI/Data/20190819_05/"

wrf_ds, xy_np = readwrf(wrf_file_dir)




tzone_file_dir  = str(xr_dir) + "/ds_zone_test.zarr"

tzone_ds = xr.open_zarr(tzone_file_dir)

# time_ind = -18
# time = np.datetime_as_string(ffmc_ds.Time[time_ind], unit='h')
# initial = np.datetime_as_string(ffmc_ds.Time[0], unit='h')
# valid = np.datetime_as_string(ffmc_ds.Time[time_ind], unit='h')
# print(time)



"############################# Make Plots #############################"


lats, lons = latlon_coords(wrf_ds.r_o)
cart_proj = get_cartopy(wrf_ds.r_o)


fig = plt.figure(figsize=(12,8))
fig.suptitle('Time Zones', fontsize = 14, fontweight = 'bold')
ax = plt.axes(projection=cart_proj)

# Download and create the states, land, and oceans using cartopy features
states = cfeature.NaturalEarthFeature(category='cultural', scale='50m',
                                        facecolor='none',
                                        name='admin_1_states_provinces_shp')
land = cfeature.NaturalEarthFeature(category='physical', name='land',
                                    scale='50m',
                                    facecolor=cfeature.COLORS['land'])
ocean = cfeature.NaturalEarthFeature(category='physical', name='ocean',
                                    scale='50m',
                                        facecolor=cfeature.COLORS['water'])
lake = cfeature.NaturalEarthFeature(category='physical', name='lakes',
                                        scale='50m',
                                        facecolor=cfeature.COLORS['water'])

ax.add_feature(states, linewidth=.5, edgecolor="black", zorder= 4)
ax.add_feature(ocean, zorder= 1)              
ax.add_feature(lake, linewidth=.25, edgecolor="black", zorder= 1)

ax.coastlines('50m', linewidth=0.8)
gl = ax.gridlines(draw_labels = True, color='gray', \
                alpha=0.3, linestyle='--', crs=crs.PlateCarree(), zorder= 3 )
gl.top_labels = False

locs={"Vancouver":[-123.1207, 49.2827 ], "Prince George":[-122.7497,53.9171], \
    "Fort St John":[-120.8464,56.2524], "Kamloops":[-120.3273,50.6745], "Creston":[-116.5, 49.083], \
        "Prince Rupert": [-130.3208, 54.3150], "Atlin": [-133.6895,59.5780], "Tofino":[-125.9066,49.1530], \
            "Fort Nelson":[-122.6972,58.8050]}

for key in locs.keys():
    print(key)
    x=float(locs[key][0]); y=float(locs[key][1])
    plt.scatter(x,y,c='k', transform=crs.PlateCarree(), zorder= 10)
    ax.annotate(key, xy = (x,y),color='w',xytext = (x,y+0.3),\
                 bbox = dict(boxstyle="square", fc="black", ec="b", alpha = 0.5), \
                     fontsize=6, xycoords=crs.PlateCarree()._as_mpl_transform(ax), zorder= 10)

cmap = plt.cm.jet
# level = np.arange(3,9,1)

C = plt.contourf(to_np(lons), to_np(lats),tzone_ds.Zone, extend = 'both',
                transform=crs.PlateCarree(), cmap=cmap, zorder = 1)


clb = fig.colorbar(C, ax = ax)
clb.set_label("Tzone", fontsize = 12, fontweight = 'bold')
clb.ax.tick_params(labelsize= 10)

# plt.xlim(-1453900,-253900)
# plt.ylim(-4448000,-2789000)


plt.show()

print("Run Time: ", datetime.now() - startTime)



