#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
# from utils.geoutils import jsonmask, delete3D, delete2D, latlngmask
from dev_geoutils import jsonmask
import string

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

# hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020082000.zarr") 
# daily_file_dir = str(xr_dir) + str("/fwf-daily-2020082000.zarr")

### Open datasets
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)



### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))

### Round all vars to third decimal...save on file size
hourly_ds = hourly_ds.round(2)
daily_ds = daily_ds.round(2)

## Mask out oceans, lakes and snow cover
hourly_ds = jsonmask(hourly_ds, wrf_file_dir)
daily_ds  = jsonmask(daily_ds, wrf_file_dir)


print(f"{str(datetime.now())} ---> start to convert datasets to np arrays" )

### Convert from xarry to np array and cutt off ocean data on the east west
time = np.array(hourly_ds.Time.dt.strftime('%Y-%m-%dT%H'))
ffmc = hourly_ds.F.values
ffmc = ffmc[:,:,50:1210]
# ffmc = np.array(ffmc,dtype = '<U6')

isi = hourly_ds.R.values
isi = isi[:,:,50:1210]
# isi = np.array(isi, dtype = '<U8')

fwi = hourly_ds.S.values
fwi = fwi[:,:,50:1210]
# fwi = np.array(fwi, dtype = '<U8')

dsr = hourly_ds.DSR.values
dsr = dsr[:,:,50:1210]
# dsr = np.array(dsr, dtype = '<U8')

dmc = daily_ds.P.values
dmc = dmc[:,:,50:1210]
# dmc = np.array(dmc, dtype = '<U8')

dc = daily_ds.D.values
dc = dc[:,:,50:1210]
# dc = np.array(dc, dtype = '<U8')

bui = daily_ds.U.values
bui = bui[:,:,50:1210]
# bui = np.array(bui, dtype = '<U8')


day = np.array(daily_ds.Time.dt.strftime('%Y-%m-%d'))


xlat = np.round(daily_ds.XLAT.values,5)
xlat= xlat[:,50:1210]
# xlat = np.array(xlat, dtype = '<U8')

xlong = np.round(daily_ds.XLONG.values,5)
xlong= xlong[:,50:1210]
# xlong = np.array(xlong, dtype = '<U8')

print(f"{str(datetime.now())} ---> end of convert datasets to np arrays" )


# # ### Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')


# # ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
make_dir = Path("/bluesky/fireweather/fwf/web_dev/data/plot/")
# # # make_dir.mkdir(parents=True, exist_ok=True)


abc = list(string.ascii_lowercase)
ff = np.arange(0,10)
for i in ff:
    # print(i)
    for j in ff:
        x1, y1 = (51 * i), (116 * j)
        x2, y2 = (51 * ( i + 1)), (116 * ( j + 1))
        fwf = {
                'FFMC': ffmc[:,x1:x2,y1:y2].tolist(),
                'DMC': dmc[:,x1:x2,y1:y2].tolist(),
                'DC': dc[:,x1:x2,y1:y2].tolist(),
                'ISI': isi[:,x1:x2,y1:y2].tolist(),
                'BUI': bui[:,x1:x2,y1:y2].tolist(),
                'FWI': fwi[:,x1:x2,y1:y2].tolist(),
                'DSR': dsr[:,x1:x2,y1:y2].tolist(),
                'XLAT': xlat[x1:x2,y1:y2].tolist(),
                'XLONG': xlong[x1:x2,y1:y2].tolist(),
                'Time': time.tolist(),
                'Day':  day.tolist()
                }

        ### Write json file to defind dir 
        with open(str(make_dir) + f"/fwf-{abc[i]+abc[j]}-{timestamp}.json","w") as f:
            json.dump(fwf,f, default=json_util.default, separators=(',', ':'), indent=None)

        print(f"{str(datetime.now())} ---> wrote json fwf {abc[i]+abc[j]} to:  " + str(make_dir) + f"/fwf-{abc[i]+abc[j]}-{timestamp}.json")


        print("i ", abc[i])
        print("j ", abc[j])



# ### Timer
print("Run Time: ", datetime.now() - startTime)