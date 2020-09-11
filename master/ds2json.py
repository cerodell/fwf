#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from utils.geoutils import jsonmask
import string

from context import data_dir, xr_dir, wrf_dir, root_dir, tzone_dir
from datetime import datetime, date, timedelta
startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
# from wrf import (getvar, g_uvmet)

### Time Zone classification method
tzdict  = {"AKDT": {'zone_id':8, 'noon':20 , 'plus': 21, 'minus':19},
            "PDT": {'zone_id':7, 'noon':19 , 'plus': 20, 'minus':18},
            "MDT": {'zone_id':6, 'noon':18 , 'plus': 19, 'minus':17},
            "CDT": {'zone_id':5, 'noon':17 , 'plus': 18, 'minus':16},
            "EDT": {'zone_id':4, 'noon':16 , 'plus': 17, 'minus':15},
            "ADT": {'zone_id':3, 'noon':15 , 'plus': 16, 'minus':14}}

### Open time zones dataset
tzone_ds = xr.open_zarr(str(tzone_dir) + "/ds_tzone.zarr")
zones = np.array(tzone_ds.Zone)


### Get Path to most recent FWI forecast and open 
hourly_file_dir = str(xr_dir) + str("/current/hourly.zarr") 
daily_file_dir = str(xr_dir) + str("/current/daily.zarr") 

### Open datasets
hourly_ds = xr.open_zarr(hourly_file_dir)
daily_ds = xr.open_zarr(daily_file_dir)


### Get noon local values of DSR and FWi
fwi = np.array(hourly_ds.S)
zero_full = np.zeros_like(fwi[0,:,:])
data_vars = ['S', 'DSR']
files_ds = []
for i in range(0,48,24):

    sum_list = []
    for key in tzdict.keys():
        zone_id, noon, plus, minus = tzdict[key]['zone_id'], tzdict[key]['noon'], tzdict[key]['plus'], tzdict[key]['minus']

        mean_da = []
        for var in data_vars:
            # print(hourly_ds[var])
            var_mean = hourly_ds[var][minus+i:plus+i].mean(axis=0)
            var_da = xr.where(tzone_ds != zone_id, zero_full, var_mean)
            var_da = np.array(var_da.Zone)
            day    = np.array(hourly_ds.Time[noon + i], dtype ='datetime64[D]')
            var_da = xr.DataArray(var_da, name=var, 
                    dims=('south_north', 'west_east'), coords= hourly_ds.isel(time = i).coords)
            var_da["Time"] = day
            mean_da.append(var_da)

        mean_ds = xr.merge(mean_da)
        sum_list.append(mean_ds)
    sum_ds = sum(sum_list)
    files_ds.append(sum_ds)

    fwi_dsr_ds = xr.combine_nested(files_ds, 'time')

### Get Path to most recent WRF run for most uptodate snowcover info
wrf_folder = date.today().strftime('/%y%m%d00/')
filein = str(wrf_dir) + wrf_folder
wrf_file_dir = sorted(Path(filein).glob('wrfout_d03_*'))

### Round all vars to second decimal...save on file size...maybe make everything ints? idk 
hourly_ds = hourly_ds.round(2)
daily_ds = daily_ds.round(2)
fwi_dsr_ds = fwi_dsr_ds.round(2)

# ## Mask out oceans, lakes and snow cover
hourly_ds = jsonmask(hourly_ds, wrf_file_dir)
daily_ds  = jsonmask(daily_ds, wrf_file_dir)
fwi_dsr_ds  = jsonmask(fwi_dsr_ds, wrf_file_dir)



print(f"{str(datetime.now())} ---> start to convert datasets to np arrays" )

### Convert from xarry to np array and cutt off ocean data on the east west
time = np.array(hourly_ds.Time.dt.strftime('%Y-%m-%dT%H'))

### Hourly forecast products 
ffmc = hourly_ds.F.values
ffmc = ffmc[:,10:,47:]

isi = hourly_ds.R.values
isi = isi[:,10:,47:]

wsp = hourly_ds.W.values
wsp = wsp[:,10:,47:]

wdir = hourly_ds.WD.values
wdir = wdir[:,10:,47:]

temp = hourly_ds.T.values
temp = temp[:,10:,47:]

rh = hourly_ds.H.values
rh = rh[:,10:,47:]

qpf = hourly_ds.r_o.values
qpf = qpf[:,10:,47:]


### Daily forecast products 
fwi = fwi_dsr_ds.S.values
fwi = fwi[:,10:,47:]

dsr = fwi_dsr_ds.DSR.values
dsr = dsr[:,10:,47:]

dmc = daily_ds.P.values
dmc = dmc[:,10:,47:]

dc = daily_ds.D.values
dc = dc[:,10:,47:]

bui = daily_ds.U.values
bui = bui[:,10:,47:]

day = np.array(daily_ds.Time.dt.strftime('%Y-%m-%d'))


xlat = np.round(daily_ds.XLAT.values,5)
xlat= xlat[10:,47:]
shape = xlat.shape
print("Shape ", shape )
# xlat = np.array(xlat, dtype = '<U8')

xlong = np.round(daily_ds.XLONG.values,5)
xlong= xlong[10:,47:]
# xlong = np.array(xlong, dtype = '<U8')

print(f"{str(datetime.now())} ---> end of convert datasets to np arrays" )


# ### Get first timestamp of forecast and make dir to store files
timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

# ### make dir for that days forecast files to be sotred...along woth index.html etc!!!!!
make_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(timestamp) + "/data/plot")
make_dir.mkdir(parents=True, exist_ok=True)

abc = list(string.ascii_lowercase)
nfile = 25
ff = np.arange(0,nfile)
xx = int(shape[0]/nfile)
yy = int(shape[1]/nfile)
for i in ff:
    # print(i)
    for j in ff:
        x1, y1 = (xx * i), (yy * j)
        x2, y2 = (xx * ( i + 1)), (yy * ( j + 1))
        fwf = {
                'FFMC': ffmc[:,x1:x2,y1:y2].tolist(),
                'DMC': dmc[:,x1:x2,y1:y2].tolist(),
                'DC': dc[:,x1:x2,y1:y2].tolist(),
                'ISI': isi[:,x1:x2,y1:y2].tolist(),
                'BUI': bui[:,x1:x2,y1:y2].tolist(),
                'FWI': fwi[:,x1:x2,y1:y2].tolist(),
                'DSR': dsr[:,x1:x2,y1:y2].tolist(),
                'wsp': wsp[:,x1:x2,y1:y2].tolist(),
                'wdir': wdir[:,x1:x2,y1:y2].tolist(),
                'temp': temp[:,x1:x2,y1:y2].tolist(),
                'rh': rh[:,x1:x2,y1:y2].tolist(),
                'qpf': qpf[:,x1:x2,y1:y2].tolist(),

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