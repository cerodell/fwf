import context
import math
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




fwf_file_dir  = str(xr_dir) + "/2019-08-20T00_daily_ds.zarr"

ffmc_ds = xr.open_zarr(fwf_file_dir)

time_ind = -18
time = np.datetime_as_string(ffmc_ds.Time[time_ind], unit='h')
initial = np.datetime_as_string(ffmc_ds.Time[0], unit='h')
valid = np.datetime_as_string(ffmc_ds.Time[time_ind], unit='h')
print(time)

# %%

# cmap = matplotlib.colors.ListedColormap(['b','g','y','r'])
# cmap = plt.cm.jet
# level = np.arange(0,60.5,0.5)
# # v_line = np.arange(0,61,0.5)
# # bounds = [0, 21, 27, 40, 60, 100]
# # norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
# test = ds_list[1]
# test.plot(cmap = cmap, levels = level)
# day  = str(np.array(ds_wrf.Time[0], dtype ='datetime64[D]'))
# plt.savefig(str(root_dir) + '/Images/' + day + '_P.png')

# # test = ds_wrf.sel(time=slice(0 ,2))


# %%

"############################# Make Plots #############################"


lats, lons = latlon_coords(ffmc_ds.F)
cart_proj = get_cartopy(wrf_ds.H)

fig = plt.figure(figsize=(6,8))
fig.suptitle('Fine Fuel Moisture Code', fontsize = 14, fontweight = 'bold')
ax = plt.axes(projection=cart_proj)

title_fig = ("Init: " +  initial + "Z  -----> " +"Valid: " + valid + "Z")
ax.set_title(str(title_fig), loc='left', fontsize = 12)

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
                alpha=0.5, linestyle='--', crs=crs.PlateCarree(), zorder= 3 )
# gl.xlabels_top = False
# gl.ylabels_left = False


## colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
## cmap= matplotlib.colors.ListedColormap(colors)
## bounds = [0, 74, 84, 88, 91, math.inf]
## norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
## plt.contourf(to_np(lons), to_np(lats),ffmc_ds.F[-1], extend = 'both',
##                 transform=crs.PlateCarree(), norm = norm, cmap=cmap)


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
level = np.arange(70,100.5,1)

C = plt.contourf(to_np(lons), to_np(lats),ffmc_ds.F[time_ind], extend = 'both',
                transform=crs.PlateCarree(), levels = level, cmap=cmap, zorder = 1)

clb = fig.colorbar(C, ax = ax, fraction=0.054, pad=0.04)
clb.set_label("FFMC", fontsize = 12, fontweight = 'bold')
clb.ax.tick_params(labelsize= 10)

plt.xlim(-1453900,-253900)
plt.ylim(-4448000,-2789000)

# ax.set_ylim(-135,-115)
# ax.set_xlim(50,60)

# plt.show()
fig.savefig(str(gsuite_dir) + "/FFMC/Contour/BC/" + valid  + ".png", dpi=300)


print("Run Time: ", datetime.now() - startTime)



# %%
