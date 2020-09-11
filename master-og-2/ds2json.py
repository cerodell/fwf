#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from utils.geoutils import jsonmask, delete3D, delete2D, latlngmask
from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)



### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

### Open datasets
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)



### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))

### Round all vars to third decimal...save on file size
hourly_ds = hourly_ds.round(3)
daily_ds = daily_ds.round(3)

### Mask out oceans, lakes and snow cover
hourly_ds = jsonmask(hourly_ds, wrf_file_dir)
daily_ds  = jsonmask(daily_ds, wrf_file_dir)


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


# ### set skip to make file size smaller
skip = 8

print(f"{str(datetime.now())} ---> build fwf skip 16 dictonary" )
fwfskip32 = {
        'FFMC': ffmc[:,0::skip,0::skip].tolist(),
        'DMC': dmc[:,0::skip,0::skip].tolist(),
        'DC': dc[:,0::skip,0::skip].tolist(),
        'ISI': isi[:,0::skip,0::skip].tolist(),
        'BUI': bui[:,0::skip,0::skip].tolist(),
        'FWI': fwi[:,0::skip,0::skip].tolist(),
        'DSR': dsr[:,0::skip,0::skip].tolist(),
        'XLAT': xlat[0::skip,0::skip].tolist(),
        'XLONG': xlong[0::skip,0::skip].tolist(),
        'Time': time.tolist(),
        'Day':  day.tolist()
        }


# ### set skip to make file size smaller
skip = 4

print(f"{str(datetime.now())} ---> build fwf skip 16 dictonary" )
fwfskip16 = {
        'FFMC': ffmc[:,0::skip,0::skip].tolist(),
        'DMC': dmc[:,0::skip,0::skip].tolist(),
        'DC': dc[:,0::skip,0::skip].tolist(),
        'ISI': isi[:,0::skip,0::skip].tolist(),
        'BUI': bui[:,0::skip,0::skip].tolist(),
        'FWI': fwi[:,0::skip,0::skip].tolist(),
        'DSR': dsr[:,0::skip,0::skip].tolist(),
        'XLAT': xlat[0::skip,0::skip].tolist(),
        'XLONG': xlong[0::skip,0::skip].tolist(),
        'Time': time.tolist(),
        'Day':  day.tolist()
        }

# ### truncate arrays to make file size smaller and only over bc
west, east = 50, 350
south, north = 100,400

print(f"{str(datetime.now())} ---> build fwf 4 dictonary" )
fwfskip0 = {
        'FFMC': ffmc[:,south:north,west:east].tolist(),
        'DMC': dmc[:,south:north,west:east].tolist(),
        'DC': dc[:,south:north,west:east].tolist(),
        'ISI': isi[:,south:north,west:east].tolist(),
        'BUI': bui[:,south:north,west:east].tolist(),
        'FWI': fwi[:,south:north,west:east].tolist(),
        'DSR': dsr[:,south:north,west:east].tolist(),
        'XLAT': xlat[south:north,west:east].tolist(),
        'XLONG': xlong[south:north,west:east].tolist(),
        'Time': time.tolist(),
        'Day':  day.tolist()
        }



# ### Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
make_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(timestamp))
make_dir.mkdir(parents=True, exist_ok=True)



print(f"{str(datetime.now())} ---> write fwfskip 32 dictonary to json" )
### Write json file to defind dir 
with open(str(make_dir) + f"/fwf-32km-{timestamp}.json","w") as f:
    json.dump(fwfskip32,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote json fwfskip 32 to:  " + str(make_dir) + f"/fwf-32km-{timestamp}.json")



print(f"{str(datetime.now())} ---> write fwfskip 16 dictonary to json" )
### Write json file to defind dir 
with open(str(make_dir) + f"/fwf-16km-{timestamp}.json","w") as f:
    json.dump(fwfskip16,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote json fwfskip 16 to:  " + str(make_dir) + f"/fwf-16km-{timestamp}.json")



print(f"{str(datetime.now())} ---> write fwf4km dictonary to json" )
## Write json file to defind dir 
with open(str(make_dir) + f"/fwf-4km-{timestamp}.json","w") as f:
    json.dump(fwfskip0,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote fwfbc json fwf4km to:  " + str(make_dir) + f"/fwf-4km-{timestamp}.json")


# ### Timer
print("Run Time: ", datetime.now() - startTime)