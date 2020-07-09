#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from geoutils import jsonmask
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

# from wrf import (to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ALL_TIMES)



### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)



### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
# wrf_folder = '/20070700/'
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))

### Round all vars to third decimal...save on file size
hourly_ds = hourly_ds.round(3)
daily_ds = daily_ds.round(3)

### Mask out oceans, lakes and snow cover
hourly_ds = jsonmask(hourly_ds, wrf_file_dir)
daily_ds  = jsonmask(daily_ds, wrf_file_dir)

### Test of truncated dataset 
# hourly_ds = hourly_ds.sel(time=slice(0 ,10), south_north=slice(0 ,2), west_east=slice(0 ,2))
# daily_ds = daily_ds.sel( south_north=slice(0 ,10), west_east=slice(0 ,2))

print(f"{str(datetime.now())} ---> start to convert datasets to np arrays" )

### Convert from xarry to np array
time = np.array(hourly_ds.Time.dt.strftime('%Y-%m-%dT%H'))
ffmc = np.array(hourly_ds.F)
isi = np.array(hourly_ds.R)
fwi = np.array(hourly_ds.S)
dsr = np.array(hourly_ds.DSR)
dmc = np.array(daily_ds.P)
dc = np.array(daily_ds.D)
bui = np.array(daily_ds.U)
day = np.array(daily_ds.Time.dt.strftime('%Y-%m-%d'))

xlat = np.round(np.array(daily_ds.XLAT),5)
xlong = np.round(np.array(daily_ds.XLONG),5)

print(f"{str(datetime.now())} ---> end of convert datasets to np arrays" )

### set skip to make file size smaller
# test = ffmc[:,0::skip,0::skip]
# skip = 8

print(f"{str(datetime.now())} ---> build dictonary" )
### Build dictionary to save to json
# fwf = {
#         'FFMC': ffmc[:,0::skip,0::skip].tolist(),
#         'DMC': dmc[:,0::skip,0::skip].tolist(),
#         'DC': dc[:,0::skip,0::skip].tolist(),
#         'ISI': isi[:,0::skip,0::skip].tolist(),
#         'BUI': bui[:,0::skip,0::skip].tolist(),
#         'FWI': fwi[:,0::skip,0::skip].tolist(),
#         'DSR': dsr[:,0::skip,0::skip].tolist(),
#         'XLAT': xlat[0::skip,0::skip].tolist(),
#         'XLONG': xlong[0::skip,0::skip].tolist(),
#         'Time': time.tolist(),
#         'Day':  day.tolist()
#         }

fwf = {
        'FFMC': ffmc.tolist(),
        'DMC': dmc.tolist(),
        'DC': dc.tolist(),
        'ISI': isi.tolist(),
        'BUI': bui.tolist(),
        'FWI': fwi.tolist(),
        'DSR': dsr.tolist(),
        'XLAT': xlat.tolist(),
        'XLONG': xlong.tolist(),
        'Time': time.tolist(),
        'Day':  day.tolist()
        }
### Print of ffmc lenght to make sure you have all the times
# print(len(fwf['FFMC']))


### Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')



### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
# make_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(timestamp))
# make_dir.mkdir(parents=True, exist_ok=True)

make_dir = str("/bluesky/archive/fireweather/test/json/plotly")
print(f"{str(datetime.now())} ---> write dictonary to json" )
### Write json file to defind dir 
with open(str(make_dir) + f"/fwf-all-{timestamp}.json","w") as f:
    json.dump(fwf,f, default=json_util.default, separators=(',', ':'))

print(f"{str(datetime.now())} ---> wrote json to:  " + str(make_dir) + f"/fwf-all-{timestamp}.json")

# ### Timer
print("Run Time: ", datetime.now() - startTime)