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
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir

startTime = datetime.now()

ztone = str(tzone_dir) + "/ds_tzone.zarr"

wrf_file_dir = "/Volumes/CER/WFRT/FWI/Data/20190819_05/"

wrf_ds, xy_np = readwrf(wrf_file_dir)


zones = xr.open_zarr(ztone)
test = np.array(zones.Zone)
len(test[test==2])
u, indices = np.unique(np.array(zones.Zone), return_index=True)
# zones.Zone.plot()
# plt.show()
# r_o_list = []
# # r_o_list.append(0)
# r_o_list.append(0)
# r_o_list.append(1)
# r_o_list.append(2)

# da = xr.DataArray(np.random.rand(4, 3),
#                     [('time', pd.date_range('2000-01-01', periods=4)),
#                          ('space', ['IA', 'IL', 'IN'])])
# da[:2]
lats, lons = latlon_coords(wrf_ds.r_o)

cart_proj = get_cartopy(wrf_ds.r_o)

# test = pickle.dumps(wrf_ds.W.projection)
# back = pickle.loads(test)

# test2 = str(wrf_ds.W.projection) 


#  my_proj = crs.Stereographic(central_latitude=0.0, central_longitude=0.0, \
#      false_easting=0.0, false_northing=0.0, true_scale_latitude=None, scale_factor=None, globe=None)



# blah = [wrf_ds.W.projection]
# blah2 = tuple(wrf_ds.W.projection)

fig = plt.figure(figsize=(6,8))
# fig = plt.figure()

fig.suptitle('Fine Fuel Moisture Code', fontsize = 14, fontweight = 'bold')
ax = plt.axes(projection=cart_proj)

# title_fig = ("Init: " +  initial + "Z  -----> " +"Valid: " + valid + "Z")
# ax.set_title(str(title_fig), loc='left', fontsize = 12)

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
# ax.add_feature(ocean, zorder= 1)              
ax.add_feature(lake, linewidth=.25, edgecolor="black", zorder= 1)

ax.coastlines('50m', linewidth=0.8)
gl = ax.gridlines(draw_labels = True, color='gray', \
                alpha=0.3, linestyle='--', crs=crs.PlateCarree(), zorder= 3 )
gl.top_labels = False
# gl.xlabels_bottom = False
# gl.ylabels_right = False
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
level = [3,4,5,6,7,8,9]

C = plt.contourf(to_np(lons), to_np(lats),zones.Zone, extend = 'both',
                transform=crs.PlateCarree(), levels = level,  cmap=cmap, zorder = 1)

# C = plt.pcolormesh(to_np(lons), to_np(lats),ffmc_ds.F[time_ind], 
#                 transform=crs.PlateCarree(),  cmap=cmap, zorder = 1)

clb = fig.colorbar(C, ax = ax, fraction=0.054, pad=0.04)
clb.set_label("FFMC", fontsize = 12, fontweight = 'bold')
clb.ax.tick_params(labelsize= 10)


plt.show()
# fig.savefig(str(gsuite_dir) + "/FFMC/Contour/BC/" + valid  + ".pdf")


print("Run Time: ", datetime.now() - startTime)
