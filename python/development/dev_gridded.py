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
# hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
# daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020082000.zarr") 
daily_file_dir = str(xr_dir) + str("/fwf-daily-2020082000.zarr")

### Open datasets
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)


# # ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
make_dir = Path("/bluesky/fireweather/fwf/web_dev/")
# # # make_dir.mkdir(parents=True, exist_ok=True)

xlat = np.round(daily_ds.XLAT.values,5)
xlat= xlat[:,50:1210]
shape = xlat.shape

xlat = np.array(xlat, dtype = '<U8')
# xlat = xlat.ravel()

xlong = np.round(daily_ds.XLONG.values,5)
xlong= xlong[:,50:1210]
xlong = np.array(xlong, dtype = '<U8')
# xlong = xlong.ravel()

abc = list(string.ascii_lowercase)
ff = np.arange(0,10)

empty = np.empty([shape[0],shape[1]], dtype = '<U2')


for i in ff:
    # print(i)
    for j in ff:
        x1, y1 = (51 * i), (116 * j)
        x2, y2 = (51 * ( i + 1)), (116 * ( j + 1))
        zone = str((abc[i]+abc[j]))
        # print(zone)
        empty[x1:x2,y1:y2] = zone

# empty = empty.ravel()


fwf = {
        'ZONE': empty.tolist(),
        'XLAT': xlat.tolist(),
        'XLONG': xlong.tolist(),
        }

## Write json file to defind dir 
with open(str(make_dir) + f"/fwf-zone.json","w") as f:
    json.dump(fwf,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote json fwf zone to:  " + str(make_dir) + f"/fwf-zone.json")



# ### Timer
print("Run Time: ", datetime.now() - startTime)