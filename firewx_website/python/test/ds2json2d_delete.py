#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from geoutils import jsonmask, delete3D, delete2D, latlngmask
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
xlat = latlngmask(xlat,wrf_file_dir)
xlong = np.round(np.array(daily_ds.XLONG),5)
xlong = latlngmask(xlong,wrf_file_dir)

print(f"{str(datetime.now())} ---> end of convert datasets to np arrays" )

# ### set skip to make file size smaller
skip = 4
ffmc_skip = delete3D(ffmc[:,0::skip,0::skip])
isi_skip = delete3D(isi[:,0::skip,0::skip])
fwi_skip = delete3D(fwi[:,0::skip,0::skip])
dsr_skip = delete3D(dsr[:,0::skip,0::skip])
dmc_skip = delete3D(dmc[:,0::skip,0::skip])
dc_skip = delete3D(dc[:,0::skip,0::skip])
bui_skip = delete3D(bui[:,0::skip,0::skip])
xlat_skip = delete2D(xlat[0::skip,0::skip])
xlong_skip = delete2D(xlong[0::skip,0::skip])


print(f"{str(datetime.now())} ---> build fwf skip dictonary" )
fwfskip = {
        'FFMC': ffmc_skip.tolist(),
        'DMC': dmc_skip.tolist(),
        'DC': dc_skip.tolist(),
        'ISI': isi_skip.tolist(),
        'BUI': bui_skip.tolist(),
        'FWI': fwi_skip.tolist(),
        'DSR': dsr_skip.tolist(),
        'XLAT': xlat_skip.tolist(),
        'XLONG': xlong_skip.tolist(),
        'Time': time.tolist(),
        'Day':  day.tolist()
        }

# ### truncate arrays to make file size smaller and only over bc
east = 400
west = 50
ffmc_bc = delete3D(ffmc[:,west:east,west:east])
isi_bc = delete3D(isi[:,west:east,west:east])
fwi_bc = delete3D(fwi[:,west:east,west:east])
dsr_bc = delete3D(dsr[:,west:east,west:east])
dmc_bc = delete3D(dmc[:,west:east,west:east])
dc_bc = delete3D(dc[:,west:east,west:east])
bui_bc = delete3D(bui[:,west:east,west:east])
xlat_bc = delete2D(xlat[west:east,west:east])
xlong_bc = delete2D(xlong[west:east,west:east])

print(f"{str(datetime.now())} ---> build fwf bc dictonary" )
fwfbc = {
        'FFMC': ffmc_bc.tolist(),
        'DMC': dmc_bc.tolist(),
        'DC': dc_bc.tolist(),
        'ISI': isi_bc.tolist(),
        'BUI': bui_bc.tolist(),
        'FWI': fwi_bc.tolist(),
        'DSR': dsr_bc.tolist(),
        'XLAT': xlat_bc.tolist(),
        'XLONG': xlong_bc.tolist(),
        'Time': time.tolist(),
        'Day':  day.tolist()
        }



# ### Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')


# ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
# make_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(timestamp))
# make_dir.mkdir(parents=True, exist_ok=True)

# ### this is for testing....
make_dir = str("/bluesky/archive/fireweather/test/json/plotly")



print(f"{str(datetime.now())} ---> write fwfskip dictonary to json" )
### Write json file to defind dir 
with open(str(make_dir) + f"/fwf-all-{timestamp}.json","w") as f:
    json.dump(fwfskip,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote json fwfskip to:  " + str(make_dir) + f"/fwf-all-{timestamp}.json")



print(f"{str(datetime.now())} ---> write fwfbc dictonary to json" )
### Write json file to defind dir 
with open(str(make_dir) + f"/fwf-bc-{timestamp}.json","w") as f:
    json.dump(fwfbc,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote fwfbc json fwfskip to:  " + str(make_dir) + f"/fwf-bc-{timestamp}.json")


# ### Timer
print("Run Time: ", datetime.now() - startTime)