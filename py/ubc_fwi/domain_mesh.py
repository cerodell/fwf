import context
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs

from mpl_toolkits.basemap import Basemap

from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from datetime import datetime, date, timedelta

from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll)


from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir

startTime = datetime.now()





# %%

### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
# daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
hourly_ds = xr.open_zarr(hourly_file_dir)
# daily_ds = xr.open_zarr(daily_file_dir)


### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = "/200714/"
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))
wrf_file = Dataset(wrf_file_dir[0])
rain_ci   = getvar(wrf_file, "RAINC")

cart_proj = get_cartopy(rain_ci)

van_lat, van_lng = 49.2827, -123.1207
xy = ll_to_xy(wrf_file, van_lat, van_lng)
lat,lng = xy_to_ll(wrf_file, 176, 117)


# %%

# ### Make Mesh Plot over Vancouver metro region
# wesn=[-125.4946,-120.5464,47.4126,50.515] # picture frame
# xy1 = ll_to_xy(wrf_file, wesn[2], wesn[0])
# xy2 = ll_to_xy(wrf_file, wesn[3], wesn[1])

# Plot_Title = "WRF 4km Grid"
# save_file = 'BC-Grid'
# fig, ax = plt.subplots()
# ax.set_title(Plot_Title , fontsize=20, weight='bold')
# fig.subplots_adjust(hspace=0.8)
# lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)

# buf = 20
# lats = lats[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# lons = lons[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# png = str(data_dir) + '/images/van_nasa.png'
# img = mpimg.imread(png)
# # Plot map
# ax.imshow(img,extent=wesn)
# ax.set_xlabel('Longitude [$^\circ$]', fontsize=16)
# ax.set_ylabel('Latitude [$^\circ$]', fontsize=16)
# ############################################

# locs={"Vancouver":[-123.1207, 49.2827 ], \
#         "Whistler":[-122.9574,50.1163], \
#              "Victoria":[-123.3656,48.4284]}

# for key in locs.keys():
#     print(key)
#     x=float(locs[key][0]); y=float(locs[key][1])
#     plt.scatter(x,y,c='red', zorder= 10)
#     ax.annotate(key, xy = (x,y),color='k',xytext = (x-0.2,y+0.16),\
#                  bbox = dict(boxstyle="Round4", fc="white", ec="red", alpha =0.8), \
#                      fontsize=10, zorder= 10)

# ax.plot(lons,lats, color ='blue', linewidth= 0.4, zorder=8, alpha =0.55)
# ax.plot(lons.T,lats.T, color ='blue', linewidth= 0.4 , zorder=8, alpha =0.55)

# ax.set_ylim(wesn[2],wesn[3])
# ax.set_xlim(wesn[0],wesn[1])

# fig.savefig(str(root_dir) + "/Images/Domain/" + save_file  + ".png", dpi=500)

# plt.show()


# %%


### Make Mesh Plot over Edmonton metro region
# wesn=[-114.0969,-112.8356,53.0398,53.8506] # picture frame
# xy1 = ll_to_xy(wrf_file, wesn[2], wesn[0])
# xy2 = ll_to_xy(wrf_file, wesn[3], wesn[1])

# Plot_Title = "WRF 4km Grid"
# save_file = 'ED-Grid'
# fig, ax = plt.subplots()
# ax.set_title(Plot_Title , fontsize=20, weight='bold')
# fig.subplots_adjust(hspace=0.8)
# lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)

# buf = 20
# lats = lats[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# lons = lons[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# png = str(data_dir) + '/images/edmon_nasa.png'
# img = mpimg.imread(png)
# # Plot map
# ax.imshow(img,extent=wesn)
# ax.set_xlabel('Longitude [$^\circ$]', fontsize=16)
# ax.set_ylabel('Latitude [$^\circ$]', fontsize=16)
# ############################################

# locs={"Edmonton":[-113.4938, 53.5461 ], \
#         "Spruce Grove":[-113.9101,53.5411], \
#              "Fort Saskatchewan":[-113.2164,53.6963]}

# for key in locs.keys():
#     print(key)
#     x=float(locs[key][0]); y=float(locs[key][1])
#     plt.scatter(x,y,c='red', zorder= 10)
#     ax.annotate(key, xy = (x,y),color='k',xytext = (x-0.16,y+0.04),\
#                  bbox = dict(boxstyle="Round4", fc="white", ec="red", alpha =0.8), \
#                      fontsize=10, zorder= 10)

# ax.plot(lons,lats, color ='blue', linewidth= 0.6, zorder=8, alpha =0.55)
# ax.plot(lons.T,lats.T, color ='blue', linewidth= 0.6 , zorder=8, alpha =0.55)

# ax.set_ylim(wesn[2],wesn[3])
# ax.set_xlim(wesn[0],wesn[1])

# fig.savefig(str(root_dir) + "/Images/Domain/" + save_file  + ".png", dpi=500)

# plt.show()

# %%


### Make Mesh Plot over Alberta 
# wesn=[-120.3223,-109.6875,48.9902,60.1875] # picture frame
# xy1 = ll_to_xy(wrf_file, wesn[2], wesn[0])
# xy2 = ll_to_xy(wrf_file, wesn[3], wesn[1])

# Plot_Title = "WRF 32km Grid"
# save_file = 'AB-Grid32km'
# fig, ax = plt.subplots()
# ax.set_title(Plot_Title , fontsize=20, weight='bold')
# fig.subplots_adjust(hspace=0.8)
# lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
# skip = 8
# lats, lons = lats[0::skip,0::skip], lons[0::skip,0::skip] 
# # buf = 20
# # lats = lats[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# # lons = lons[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# png = str(data_dir) + '/images/alberta_nasa.png'
# img = mpimg.imread(png)
# # Plot map
# ax.imshow(img,extent=wesn)
# ax.set_xlabel('Longitude [$^\circ$]', fontsize=16)
# ax.set_ylabel('Latitude [$^\circ$]', fontsize=16)
# ############################################
# locs={"Calgary":[-114.0719, 51.0447 ], \
#         "Edmonton":[-113.4938, 53.5461 ], \
#              "High Level":[-117.1403,58.5071]}

# for key in locs.keys():
#     print(key)
#     x=float(locs[key][0]); y=float(locs[key][1])
#     plt.scatter(x,y,c='red', zorder= 10)
#     ax.annotate(key, xy = (x,y),color='k',xytext = (x+0.06,y+0.04),\
#                  bbox = dict(boxstyle="Round4", fc="white", ec="red", alpha =0.8), \
#                      fontsize=6, zorder= 10)

# ax.plot(lons,lats, color ='blue', linewidth= 0.6, zorder=8, alpha =0.55)
# ax.plot(lons.T,lats.T, color ='blue', linewidth= 0.6 , zorder=8, alpha =0.55)

# ax.set_ylim(wesn[2],wesn[3])
# ax.set_xlim(wesn[0],wesn[1])

# fig.savefig(str(root_dir) + "/Images/Domain/" + save_file  + ".png", dpi=500)

# plt.show()

# %%


### Make Mesh Plot over Canada 
wesn=[-144.9492,-52.558,33.8203,72.5625] # picture frame
xy1 = ll_to_xy(wrf_file, wesn[2], wesn[0])
xy2 = ll_to_xy(wrf_file, wesn[3], wesn[1])

Plot_Title = "WRF Domain"
save_file = 'CA-Grid-edge'
fig, ax = plt.subplots()
ax.set_title(Plot_Title , fontsize=20, weight='bold')
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)
skip = 8
lats, lons = lats[0::skip,0::skip], lons[0::skip,0::skip] 
# buf = 20
# lats = lats[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
# lons = lons[int(xy1[1]-buf):int(xy2[1]+buf),int(xy1[0]-buf):int(xy2[0]+buf)]
png = str(data_dir) + '/images/canada_nasa.png'
img = mpimg.imread(png)
# Plot map
ax.imshow(img,extent=wesn)
ax.set_xlabel('Longitude [$^\circ$]', fontsize=16)
ax.set_ylabel('Latitude [$^\circ$]', fontsize=16)
############################################
locs={"Vancouver":[-123.1207, 49.2827 ], \
        "Edmonton":[-113.4938, 53.5461 ], \
             "Toronto":[-79.3832,43.6532]}

for key in locs.keys():
    print(key)
    x=float(locs[key][0]); y=float(locs[key][1])
    plt.scatter(x,y,c='red', zorder= 10)
    ax.annotate(key, xy = (x,y),color='k',xytext = (x+0.06,y+0.04),\
                 bbox = dict(boxstyle="Round4", fc="white", ec="red", alpha =0.8), \
                     fontsize=6, zorder= 10)

ax.plot(lons[0],lats[0], color ='blue', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[-1].T,lats[-1].T, color ='blue', linewidth= 2 , zorder=8, alpha =1)
ax.plot(lons[:,0],lats[:,0], color ='blue', linewidth= 2, zorder=8, alpha =1)
ax.plot(lons[:,-1].T,lats[:,-1].T, color ='blue', linewidth= 2 , zorder=8, alpha =1)

# ax.plot(lons,lats, color ='blue', linewidth= 0.55, zorder=8, alpha =0.6)
# ax.plot(lons.T,lats.T, color ='blue', linewidth= 0.55, zorder=8, alpha =0.6)


ax.set_ylim(wesn[2],wesn[3])
ax.set_xlim(wesn[0],wesn[1])

fig.savefig(str(root_dir) + "/Images/Domain/" + save_file  + ".png", dpi=500)

# plt.show()

# %%
