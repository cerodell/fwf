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
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir

startTime = datetime.now()



# %%

wrf_file_dir = "/Volumes/CER/WFRT/FWI/Data/20190819_05/"

wrf_ds, xy_np = readwrf(wrf_file_dir)




fwf_file_dir  = str(xr_dir) + "/2019-08-20T00_daily_ds.zarr"

ffmc_ds = xr.open_zarr(fwf_file_dir)

time_ind = -18
time = np.datetime_as_string(ffmc_ds.Time[time_ind], unit='h')
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

cmap = plt.cm.jet
level = np.arange(70,100,0.01)

ffmc_ds.F[-1].plot(cmap = cmap, levels = level)
# plt.show()

# lats, lons = latlon_coords(ffmc_ds.F)
# cart_proj = get_cartopy(wrf_ds.H)

# fig = plt.figure(figsize=(6,8))
# ax2 = plt.axes(projection=cart_proj)

# # Download and create the states, land, and oceans using cartopy features
# states = cfeature.NaturalEarthFeature(category='cultural', scale='50m',
#                                         facecolor='none',
#                                         name='admin_1_states_provinces_shp')
# land = cfeature.NaturalEarthFeature(category='physical', name='land',
#                                     scale='50m',
#                                     facecolor=cfeature.COLORS['land'])
# ocean = cfeature.NaturalEarthFeature(category='physical', name='ocean',
#                                     scale='50m',
#                                         facecolor=cfeature.COLORS['water'])
# lake = cfeature.NaturalEarthFeature(category='physical', name='lakes',
#                                         scale='50m',
#                                         facecolor=cfeature.COLORS['water'])

# ax2.add_feature(states, linewidth=.5, edgecolor="black")
# #ax2.add_feature(land)
# ax2.add_feature(ocean)              
# ax2.add_feature(lake, linewidth=.25, edgecolor="black")

# #ax2.add_feature(cart.feature.OCEAN, zorder=100, edgecolor='#A9D0F5')
# #ax2.add_feature(cart.feature.LAKES, zorder=100, edgecolor='#A9D0F5')
# ax2.coastlines('50m', linewidth=0.8)


# # colors = ["#0000FF","#00E000","#FFFF00", "#E0A000", "#FF0000"]
# # cmap= matplotlib.colors.ListedColormap(colors)
# # bounds = [0, 74, 84, 88, 91, math.inf]
# # norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

# # plt.contourf(to_np(lons), to_np(lats),ffmc_ds.F[-1], extend = 'both',
# #                 transform=crs.PlateCarree(), norm = norm, cmap=cmap)



# locs={"Vancouver":[-1003900, 3089000 ], "Prince George":[-122.7497,53.9171]}


# # locs={"Vancouver":[4, 40], "Prince George":[40,56]}

# # TASK 1.2 - add labels
# for key in locs.keys():
#     x=float(locs[key][0]); y=float(locs[key][1])
#     plt.scatter(x,y,c='r')
#     plt.annotate(key, xy = (x,y),color='w',xytext = (x,y+0.3),\
#                  bbox = dict(boxstyle="square", fc="black", ec="b",alpha=0.5), zorder = 10)

# cmap = plt.cm.jet
# level = np.arange(70,101,1)

# C = plt.contourf(to_np(lons), to_np(lats),ffmc_ds.F[time_ind], extend = 'both',
#                 transform=crs.PlateCarree(), levels = level, cmap=cmap, zorder = 1)

# clb = fig.colorbar(C, ax = ax2, fraction=0.04, pad=0.02)
# clb.set_label("FFMC", fontsize = 8)
# clb.ax.tick_params(labelsize= 8)

# # Add the gridlines
# #gl = ax2.gridlines(color="black", linestyle="dotted")
# #gl.xformatter = LONGITUDE_FORMATTER
# #gl.yformatter = LATITUDE_FORMATTER
# #gl.xlabel_style = {'size': 15, 'color': 'gray'}

# #ax2.axis("off")

# # plt.xticks([-1772000,-849900,-1125,831400,1737000,2754000],
# #             ('130'u"\u00b0"" W", '120'u"\u00b0"" W", '110'u"\u00b0"" W", '100'u"\u00b0"" W", '90'u"\u00b0"" W", '80'u"\u00b0"" W"))
# # plt.yticks([-4520000,-4143000,-3753000,-3372000,-2991000],
# #             ('45'u"\u00b0"" N", '48'u"\u00b0"" N", '51'u"\u00b0"" N", '54'u"\u00b0"" N", '57'u"\u00b0"" N"))

# plt.xlim(-1453900,-253900)
# plt.ylim(-4448000,-2789000)

plt.show()


# plt.title(r"Fine Fuel Moisture Code" + "\n" + "Init: " +  path_str[0][-19:-3] + "Z        --->   Valid: " + path_str[i][-19:-3]+"Z")
# fig.savefig(save + path_str[i][-19:-6])
# #    plt.close('all')
# plt.tight_layout(pad=1.08, h_pad=0.4, w_pad=None, rect=None)

# print(path_str[i][-19:-6])

# plot_stop = datetime.now() # current date and time
# diff = plot_stop - plot_start

# print(diff)


# plt.close('all')

print("Run Time: ", datetime.now() - startTime)



# %%
