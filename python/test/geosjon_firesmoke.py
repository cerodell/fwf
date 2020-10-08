import context
import sys
import json
import numpy as np
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from geoutils import mask, contourf_to_geojson
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import data_dir, xr_dir, wrf_dir, root_dir



### Open color map json
with open('/bluesky/fireweather/fwf/firewx_website/json/colormaps-new.json') as f:
  cmaps = json.load(f)



### Get WRF 
wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = '/20062300/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d02_*'))
ds_wrf = xr.open_dataset(wrf_file_dir[0])

### Get Smoke
filein = "/bluesky/fireweather/fwf/data/wrf/dispersion.nc"
ds = xr.open_dataset(filein)



temp = np.array(ds_wrf.T2)
temp = temp[0,:,:]

xlat = np.array(ds_wrf.XLAT)
xlat = xlat[0,:,:]

xlong = np.array(ds_wrf.XLONG)
xlong = xlong[0,:,:]


timestamp  = str(np.array(ds_wrf.Time[0], dtype ='datetime64[h]'))
timestamp = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
colors = cmaps['F']["colors15"]
geojson_filepath = str("Temp_20200630")
levels = len(colors)
fig = plt.figure(frameon=False)
contourf = plt.contourf(xlong, xlat ,temp , levels = levels, \
                        linestyles = 'None', vmin = 273, vmax = 309, colors = colors)
plt.close()
fig.savefig("/bluesky/archive/fireweather/test/images/Temp_20200630.png", transparent=True, bbox_inches='tight', pad_inches=0)


geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    min_angle_deg=3.0,
    ndigits=2,
    stroke_width=0.2,
    fill_opacity=0.95,
    unit=timestamp, 
    geojson_filepath = f'/bluesky/fireweather/fwf/data/geojson/{geojson_filepath}.geojson')

print(f'wrote geojson to: /bluesky/fireweather/fwf/data/geojson/{geojson_filepath}.geojson')


# ### Timer
print("Run Time: ", datetime.now() - startTime)









# print(np.max(ds.PM25[0]))
# print(ds.PM25.ROW)
# timestamp  = str(np.array(ds.TFLAG['DATE-TIME'][0], dtype ='datetime64[h]'))
# timestamp = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

# x_west = ds.XCENT - (abs(ds.XCENT)- abs(ds.XORIG))
# x_east = ds.XORIG
# dx     = ds.XCELL
# ncol    = len(ds.COL)
# x = np.arange(x_east, x_west+0.1, 0.1)

# y_north = ds.YCENT + (abs(ds.YCENT)- abs(ds.YORIG))
# y_south = ds.YORIG
# nrow    = len(ds.ROW)
# y = np.arange(y_south, y_north+0.1, 0.1)

# xx, yy = np.meshgrid(x,y)

# pm25 = np.array(ds.PM25)
# pm25 = pm25[0,0,:,:]


# timestamp  = str(np.array(ds.TSTEP[0], dtype ='datetime64[h]'))
# timestamp = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
# colors = cmaps['F']["colors15"]
# geojson_filepath = str("PM25_" + timestamp)
# levels = len(colors)
# fig = plt.figure(frameon=False)
# contourf = plt.contourf(xx,yy ,pm25 , levels = levels, \
#                         linestyles = 'None', vmin = 0, vmax = 250, colors = colors)
# plt.close()
# fig.savefig("/bluesky/archive/fireweather/test/images/pm25.png", transparent=True, bbox_inches='tight', pad_inches=0)



