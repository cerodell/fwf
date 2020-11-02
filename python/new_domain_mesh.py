import context
import numpy as np
import pandas as pd
import xarray as xr
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


### Get All Stations CSV
url = 'https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv'
stations_df = pd.read_csv(url, sep = ',')
stations_df = stations_df.drop_duplicates()
stations_df = stations_df.rename({'wmo': 'WMO', 'name': 'NAME'}, axis=1)
stations_df = stations_df.drop(columns=['tmm','ua', 'the_geom', 'h_bul','s_bul','hly','syn'])

df = stations_df.loc[stations_df['prov'] == 'NT']
df = df.drop_duplicates(subset=['id', 'WMO'], keep=False)



### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(data_dir) + str("/wrf/wrfout_d03_2020-10-09_00:00:00") 
hourly_ds = xr.open_dataset(hourly_file_dir)



### Make Mesh Plot over Canada 
# wesn=[-131.0495,-108.067,59.3222,69.0544] # nwt_v0
# wesn=[-119.8924,-114.4381,60.1057,63.4855] # nwt_v1
# wesn=[-117.3878,-114.2339,60.8629,62.6929] # nwt_v2
wesn=[-119.7705,-114.1071,59.8223,64.5041] # nwt_v2

df.loc[(df['lat'] >= wesn[2]) & (df['lat'] <= wesn[3])]


df = df.loc[(df['lat'] >= wesn[2]) & (df['lat'] <= wesn[3])]
df = df.loc[(df['lon'] >= wesn[0]) & (df['lon'] <= wesn[1])]


Plot_Title = "WRF Domain"
save_file = 'NWT-Grid-edge-v3'
fig, ax = plt.subplots(figsize = (14,6))
ax.set_title(Plot_Title , fontsize=20, weight='bold')
fig.subplots_adjust(hspace=0.8)
lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)

## skip every few indexe
skip = 8
lats, lons = lats[0::skip,0::skip], lons[0::skip,0::skip] 

png = str(data_dir) + '/images/nwt_v3.png'
img = mpimg.imread(png)
# Plot map
ax.imshow(img,extent=wesn)
ax.set_xlabel('Longitude [$^\circ$]', fontsize=16)
ax.set_ylabel('Latitude [$^\circ$]', fontsize=16)
############################################

for i in range(len(df['prov'])):
    x=float(df.lon.iloc[i]); y=float(df.lat.iloc[i])
    ax.scatter(x,y,c='red', zorder= 10)
    ax.annotate(df.id.iloc[i], xy = (x,y),color='k',xytext = (x+0.06,y+0.04),\
                 bbox = dict(boxstyle="Round4", fc="white", ec="red", alpha =0.8), \
                     fontsize=6, zorder= 10)
linew = 0.5
ax.plot(lons[0],lats[0], color ='grey', linewidth= linew, zorder=8, alpha =1)
ax.plot(lons[-1].T,lats[-1].T, color ='grey', linewidth= linew , zorder=8, alpha =1)
ax.plot(lons[:,0],lats[:,0], color ='grey', linewidth= linew, zorder=8, alpha =1)
ax.plot(lons[:,-1].T,lats[:,-1].T, color ='grey', linewidth= linew , zorder=8, alpha =1)

# ax.plot(lons,lats, color ='blue', linewidth= 0.55, zorder=8, alpha =0.6)
# ax.plot(lons.T,lats.T, color ='blue', linewidth= 0.55, zorder=8, alpha =0.6)


ax.set_ylim(wesn[2],wesn[3])
ax.set_xlim(wesn[0],wesn[1])

fig.savefig(str(root_dir) + "/images/domain/" + save_file  + ".png", dpi=500)

plt.show()

# %%
# Plot_Title = "NWT Weather Stations"
# save_file = 'NWT-WxStations'
# fig, ax = plt.subplots(figsize = (10,6))
# ax.set_title(Plot_Title , fontsize=20, weight='bold')
# fig.subplots_adjust(hspace=0.8)
# lats, lons = np.array(hourly_ds.XLAT), np.array(hourly_ds.XLONG)

# ## skip every few indexe
# skip = 8
# lats, lons = lats[0::skip,0::skip], lons[0::skip,0::skip] 

# png = str(data_dir) + '/images/nwt_v0.jpeg'
# img = mpimg.imread(png)
# # Plot map
# ax.imshow(img,extent=wesn)
# ax.set_xlabel('Longitude [$^\circ$]', fontsize=16)
# ax.set_ylabel('Latitude [$^\circ$]', fontsize=16)
# ############################################
# # locs={"Vancouver":[-123.1207, 49.2827 ], \
# #         "Edmonton":[-113.4938, 53.5461 ], \
# #              "Toronto":[-79.3832,43.6532]}

# for i in range(len(df['prov'])):
#     x=float(df.lon.iloc[i]); y=float(df.lat.iloc[i])
#     plt.scatter(x,y,c='red', zorder= 10)
#     ax.annotate(df.id.iloc[i], xy = (x,y),color='k',xytext = (x+0.06,y+0.04),\
#                  bbox = dict(boxstyle="Round4", fc="white", ec="red", alpha =0.8), \
#                      fontsize=6, zorder= 10)

# ax.set_ylim(wesn[2],wesn[3])
# ax.set_xlim(wesn[0],wesn[1])

# fig.savefig(str(root_dir) + "/images/domain/" + save_file  + ".png", dpi=500)

# plt.show()
