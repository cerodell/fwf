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
with open('/bluesky/fireweather/fwf/firewx_website/json/colormaps.json') as f:
  cmaps = json.load(f)


### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)



### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = '/20062300/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


### Mask out oceans, lakes and snow cover
hourly_ds = mask(hourly_ds, wrf_file_dir)
daily_ds  = mask(daily_ds, wrf_file_dir)



timestamp  = str(np.array(hourly_ds.Time[0], dtype ='datetime64[h]'))
timestamp = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
for var in cmaps:
  name = cmaps[var]["name"]
  print(name)
  make_dir = Path("/bluesky/fireweather/fwf/data/geojson/" + str(timestamp[:-2]) + "/" + str(name))
  make_dir.mkdir(parents=True, exist_ok=True)


index = np.arange(0,66,6)
for i in index:
  contourf_to_geojson(cmaps, 'F', hourly_ds, i)
  contourf_to_geojson(cmaps, 'R', hourly_ds, i)
  contourf_to_geojson(cmaps, 'S', hourly_ds, i)

for i in range(len(daily_ds.Time)):
  contourf_to_geojson(cmaps, 'P', daily_ds, i)
  contourf_to_geojson(cmaps, 'D', daily_ds, i)
  contourf_to_geojson(cmaps, 'U', daily_ds, i)


# ### Make Geojson files with mask applied
# contourf_to_geojson(cmaps, 'F', hourly_ds, 18)
# contourf_to_geojson(cmaps, 'P', daily_ds, 0)
# contourf_to_geojson(cmaps, 'D', daily_ds, 0)
# contourf_to_geojson(cmaps, 'R', hourly_ds, 18)
# contourf_to_geojson(cmaps, 'U', daily_ds, 0)
# contourf_to_geojson(cmaps, 'S', hourly_ds, 18)


# ### Timer
print("Run Time: ", datetime.now() - startTime)









# def contourf_to_geojson(cmaps, var, ds, index):
#     day  = str(np.array(ds.Time[0], dtype ='datetime64[D]'))
#     vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
#     name, colors = cmaps[var]["name"], cmaps[var]["colors15"]
#     geojson_filepath = str(name + "_" + day)
#     levels = len(colors)
#     contourf = plt.contourf(np.array(ds.XLONG), np.array(ds.XLAT), np.array(ds[var][index]), levels = levels, \
#                             linestyles = 'None', vmin = vmin, vmax = vmax, colors = colors)
#     plt.close()

#     geojsoncontour.contourf_to_geojson(
#         contourf=contourf,
#         min_angle_deg=3.0,
#         ndigits=2,
#         stroke_width=0.2,
#         fill_opacity=0.95,
#         geojson_filepath = f'/Users/rodell/fireweather/json/{geojson_filepath}.geojson')

#     return

# # ### Make Geojson files
# contourf_to_geojson(cmaps, 'F', hourly_ds, 18)
# contourf_to_geojson(cmaps, 'P', daily_ds, 0)
# contourf_to_geojson(cmaps, 'D', daily_ds, 0)
# contourf_to_geojson(cmaps, 'R', hourly_ds, 18)
# contourf_to_geojson(cmaps, 'U', daily_ds, 0)
# contourf_to_geojson(cmaps, 'S', hourly_ds, 18)


# # ### Timer
# print("Run Time: ", datetime.now() - startTime)

# def mask(ds_unmasked, LANDMASK, LAKEMASK, SNOWC):
#     ds = xr.where(LANDMASK == 1, ds_unmasked, np.nan)
#     ds = ds.transpose("time", "south_north", "west_east")
#     ds = xr.where(LAKEMASK == 0, ds, np.nan)
#     ds = ds.transpose("time", "south_north", "west_east")
#     ds = xr.where(SNOWC == 0, ds, np.nan)
#     ds = ds.transpose("time", "south_north", "west_east")
#     ds['Time'] = ds_unmasked['Time']
#     return ds
# ### Timer
# print("Run Time: ", datetime.now() - startTime)