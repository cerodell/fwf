#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import json
import numpy as np
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from geoutils import mask, mycontourf_to_geojson
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

hourly_vars = ['F','R','S','DSR']
for var in hourly_vars:
  hourly_ds[var] = xr.where(hourly_ds[var]< cmaps[var]['vmax'], hourly_ds[var], int(cmaps[var]['vmax'] + 1))

daily_vars = ['D','P','U']
for var in daily_vars:
  daily_ds[var] = xr.where(daily_ds[var]< cmaps[var]['vmax'], daily_ds[var], int(cmaps[var]['vmax'] + 1))


### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))


### Mask out oceans, lakes and snow cover
hourly_ds = mask(hourly_ds, wrf_file_dir)
daily_ds  = mask(daily_ds, wrf_file_dir)


## Get first timestamp of forecast and make dir to store files
timestamp  = str(np.array(hourly_ds.Time[0], dtype ='datetime64[h]'))
folderdate = datetime.strptime(str(timestamp), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
make_dir = Path("/bluesky/fireweather/fwf/data/geojson/" + str(folderdate))
make_dir.mkdir(parents=True, exist_ok=True)


## Make geojson of ffmc, isi, fwf every 6 hours
print(f"{str(datetime.now())} ---> start loop of hourly fwf products" )

index = np.arange(0,66,6)
for i in index:
  mycontourf_to_geojson(cmaps, 'F', hourly_ds, i, folderdate, "colors15")
  mycontourf_to_geojson(cmaps, 'R', hourly_ds, i, folderdate, "colors15")
  mycontourf_to_geojson(cmaps, 'S', hourly_ds, i, folderdate, "colors15")

print(f"{str(datetime.now())} ---> end loop of hourly fwf products" )


# ## Make geojson of dmc, dc, bui at noon local for the two day forecast period
print(f"{str(datetime.now())} ---> start loop of daily fwf products" )


for i in range(len(daily_ds.Time)):
  mycontourf_to_geojson(cmaps, 'P', daily_ds, i, folderdate, "colors15")
  mycontourf_to_geojson(cmaps, 'D', daily_ds, i, folderdate, "colors15")
  mycontourf_to_geojson(cmaps, 'U', daily_ds, i, folderdate, "colors15")

print(f"{str(datetime.now())} ---> end loop of daily fwf products" )



###############################################################################
###############################################################################
## Make geojson of ffmc, isi, fwf every 6 hours
# print(f"{str(datetime.now())} ---> start loop of hourly fwf products" )

# index = np.arange(0,66,6)
# for i in index:
#   mycontourf_to_geojson(cmaps, 'F', hourly_ds, i, folderdate, "colors30")
#   mycontourf_to_geojson(cmaps, 'R', hourly_ds, i, folderdate, "colors30")
#   mycontourf_to_geojson(cmaps, 'S', hourly_ds, i, folderdate, "colors30")

# print(f"{str(datetime.now())} ---> end loop of hourly fwf products" )

# # ## Make geojson of dmc, dc, bui at noon local for the two day forecast period
# print(f"{str(datetime.now())} ---> start loop of daily fwf products" )


# for i in range(len(daily_ds.Time)):
#   mycontourf_to_geojson(cmaps, 'P', daily_ds, i, folderdate, "colors30")
#   mycontourf_to_geojson(cmaps, 'D', daily_ds, i, folderdate, "colors30")
#   mycontourf_to_geojson(cmaps, 'U', daily_ds, i, folderdate, "colors30")

# print(f"{str(datetime.now())} ---> end loop of daily fwf products" )
###############################################################################
###############################################################################

# ### Timer
print("Run Time: ", datetime.now() - startTime)



