import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from context import data_dir, xr_dir, wrf_dir, tzone_dir, wrf_dir_new
import timezonefinder, pytz
from pathlib import Path
from netCDF4 import Dataset

import matplotlib.pyplot as plt
from dev_utils.read_wrfout import readwrf
import time
from wrf import (getvar, ALL_TIMES, extract_vars,
                 omp_set_num_threads, omp_get_max_threads, g_uvmet)

from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))



domain = 'd02'

# wrf_filein = date.today().strftime('/%y%m%d00/')
wrf_filein = '/20121500/'

wrf_dir_new = "/Users/rodell/fwf/data/test"
wrf_file_dir = str(wrf_dir_new) + wrf_filein


omp_set_num_threads(6)
print(f"read files with {omp_get_max_threads()} threads")
startTime = datetime.now()
print("begin readwrf: ", str(startTime))
ds_list, time_list, attributes = [], [], []

pathlist = sorted(Path(wrf_file_dir).glob(f'wrfout_{domain}_*00'))
if domain == 'd02':
    pathlist = pathlist[:61]
else:
    pass
for path in pathlist:
    loop_time = datetime.now()
    path_in_str = str(path)
    wrf_file = Dataset(path_in_str,'r')

    # slp_time = datetime.now()
    # SLPi           = getvar(wrf_file, "slp", units = "hPa", meta=False)
    # SLP            = xr.DataArray(SLPi, name='SLP', dims=('south_north', 'west_east'))
    # # SLP.attrs      = Ti.attrs
    # SLP.attrs['description'] = "SEA LEVEL PRESSURE"
    # SLP.attrs['units'] = "hPa"
    # print("slp run time: ", datetime.now() - slp_time)

    time          = getvar(wrf_file, "times", timeidx=0)
    lats          = getvar(wrf_file, "XLAT")
    lngs          = getvar(wrf_file, "XLONG")
    # xtime         = getvar(wrf_file, "XTIME")


    Ti           = getvar(wrf_file, "T2")
    T            = Ti-273.15
    T.attrs      = Ti.attrs
    T.attrs['description'] = "2m TEMP"
    T.attrs['units'] = "C"

    TDi            = getvar(wrf_file, "td2", units = "degC", meta= False)
    TD            = xr.DataArray(TDi, name='TD', dims=('south_north', 'west_east'))
    TD.attrs      = Ti.attrs
    TD.attrs['description'] = "2m DEW POINT TEMP"
    TD.attrs['units'] = "C"


    Hi           = getvar(wrf_file, "rh2",  meta= False)
    H            = xr.DataArray(Hi, name='H', dims=('south_north', 'west_east'))
    H.attrs      = Ti.attrs
    H.attrs['units'] = "(%)"
    H.attrs['description'] = "2m RELATIVE HUMIDITY"

    wsp_wdir     = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1')
    wsp_array    = np.array(wsp_wdir[0])
    wdir_array   = np.array(wsp_wdir[1])
    W            = xr.DataArray(wsp_array, name='W', dims=('south_north', 'west_east'))
    WD           = xr.DataArray(wdir_array, name='WD', dims=('south_north', 'west_east'))
    W.attrs      = wsp_wdir.attrs
    W.attrs['description'] = "10m WIND SPEED"
    WD.attrs      = wsp_wdir.attrs
    WD.attrs['description'] = "10m WIND DIRECTION"
    WD.attrs['units'] = "degrees"

    U10i             = getvar(wrf_file, "U10", meta= False) 
    U10            = xr.DataArray(U10i, name='U10', dims=('south_north', 'west_east'))
    U10.attrs      = Ti.attrs
    U10.attrs['units'] = "m s-1"
    U10.attrs['description'] = "U at 10 M"

    V10i           = getvar(wrf_file, "V10",meta= False)
    V10            = xr.DataArray(V10i, name='V10', dims=('south_north', 'west_east'))
    V10.attrs      = Ti.attrs
    V10.attrs['units'] = "m s-1"
    V10.attrs['description'] = "V at 10 M"

    ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
    rain_ci   = getvar(wrf_file, "RAINC")
    rain_c    = rain_ci.values
    rain_sh   = getvar(wrf_file, "RAINSH", meta=False)
    rain_nc   = getvar(wrf_file, "RAINNC", meta=False)
    qpf_i     = rain_c + rain_sh + rain_nc
    qpf       = np.where(qpf_i>0,qpf_i, qpf_i*0)
    r_o       = xr.DataArray(qpf, name='r_o', dims=('south_north', 'west_east'))
    r_o.attrs = rain_ci.attrs
    r_o.attrs['description'] = "ACCUMULATED TOTAL PRECIPITATION"

    SNWi             = getvar(wrf_file, "SNOWNC", meta= False)
    SNW            = xr.DataArray(SNWi, name='SNW', dims=('south_north', 'west_east'))
    SNW.attrs      = Ti.attrs
    SNW.attrs['units'] = "cm"
    SNW.attrs['description'] = "ACCUMULATED TOTAL GRID SCALE SNOW AND ICE"

    SNOWCi             = getvar(wrf_file, "SNOWC", meta= False)
    SNOWC            = xr.DataArray(SNOWCi, name='SNOWC', dims=('south_north', 'west_east'))
    SNOWC.attrs      = Ti.attrs
    SNOWC.attrs['units'] = ""
    SNOWC.attrs['description'] = "FLAG INDICATING SNOW COVERAGE (1 FOR SNOW COVER)"

    SNOWHi             = getvar(wrf_file, "SNOWH",  meta= False)
    SNOWH            = xr.DataArray(SNOWHi, name='SNOWH', dims=('south_north', 'west_east'))
    SNOWH.attrs      = Ti.attrs
    SNOWH.attrs['units'] = "m"
    SNOWH.attrs['description'] = "PHYSICAL SNOW DEPTH"


    var_list = [H,T,W,WD,r_o, SNW, SNOWC, SNOWH, U10, V10]
    ds = xr.merge(var_list)
    ds_list.append(ds)
    time_list.append(time)
    attributes.append(path_in_str)
    print("loop time: ", datetime.now() - loop_time)

### Combine xarrays and rename to match van wangers defs 
wrf_ds = xr.combine_nested(ds_list, 'time')
wrf_ds = wrf_ds.rename_vars({"T2":"T"})

wrf_file = Dataset(attributes[0],'r')
nc_attrs = wrf_file.ncattrs()
for nc_attr in nc_attrs:
    # print('\t%s:' % nc_attr, repr(wrf_file.getncattr(nc_attr)))
    wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))


print("readwrf run time: ", datetime.now() - startTime)
