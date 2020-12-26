#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import bson
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
# from utils.geoutils import jsonmask, delete3D, delete2D, latlngmask
import string

from context import data_dir, xr_dir, wrf_dir, root_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
from wrf import (getvar, g_uvmet, geo_bounds)

domain = 'd02'

### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(data_dir) + str(f"/test/current/fwf-hourly-current-{domain}.zarr") 
daily_file_dir = str(data_dir) + str(f"/test/current/fwf-daily-current-{domain}.zarr") 

# hourly_file_dir = str(xr_dir) + str("/fwf-hourly-2020082000.zarr") 
# daily_file_dir = str(xr_dir) + str("/fwf-daily-2020082000.zarr")


coast_lines = str(data_dir) + "/n_hem.csv"
df_coast = pd.read_csv(coast_lines)

## Make 1D arrays of lat and lon
lats = np.array(df_coast["lat_degr"])
lons = np.array(df_coast["lon_degr"])


### Open datasets
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)

test = geo_bounds(hourly_ds.F)


ffmc = hourly_ds.F.values

ff = {"ffmc": ffmc[1,:,:].tolist()}

# Serializing json  
json_object = json.dumps(ff, default=json_util.default, separators=(',', ':'), indent=None) 
  
# Writing to sample.json 
with open(str(data_dir) + f"/test.json","w") as outfile:
    json.dump(ff,outfile, default=json_util.default, separators=(',', ':'), indent=None)

    outfile.write(json_object)

xlats = hourly_ds.XLAT.values
xlngs = hourly_ds.XLONG.values
shape = ffmc.shape
plt.contourf(xlngs, xlats, ffmc[0,:,:])
plt.plot(lons, lats, zorder=1, linewidth=0.6, color="grey")
plt.xlim([-175, -30])
plt.ylim([30, 88])


for i in range(1,100):
    if int(shape[1]) % i == 0:
        print(i)
    else:
        pass




# # ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
make_dir = Path("/bluesky/fireweather/fwf/web_dev/")
# # # make_dir.mkdir(parents=True, exist_ok=True)

xlat = np.round(daily_ds.XLAT.values,5)
xlat= xlat[10:,47:]
shape = xlat.shape

xlat = np.array(xlat, dtype = '<U8')
# xlat = xlat.ravel()

xlong = np.round(daily_ds.XLONG.values,5)
xlong= xlong[10:,47:]
xlong = np.array(xlong, dtype = '<U8')
# xlong = xlong.ravel()

abc = list(string.ascii_lowercase)
nfile = 25
ff = np.arange(0,nfile)
xx = int(shape[0]/nfile)
yy = int(shape[1]/nfile)
empty = np.empty([shape[0],shape[1]], dtype = '<U2')


for i in ff:
    # print(i)
    for j in ff:
        x1, y1 = (xx * i), (yy * j)
        x2, y2 = (xx * ( i + 1)), (yy * ( j + 1))
        zone = str((abc[i]+abc[j]))
        # print(zone)
        empty[x1:x2,y1:y2] = zone



fwf = {
        'ZONE': empty.tolist(),
        'XLAT': xlat.tolist(),
        'XLONG': xlong.tolist(),
        }

# Write json file to defind dir 
with open(str(make_dir) + f"/fwf-zone.json","w") as f:
    json.dump(fwf,f, default=json_util.default, separators=(',', ':'), indent=None)

print(f"{str(datetime.now())} ---> wrote json fwf zone to:  " + str(make_dir) + f"/fwf-zone.json")



# ### Timer
print("Run Time: ", datetime.now() - startTime)