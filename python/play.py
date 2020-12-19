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
# import time
# from wrf import (getvar, ALL_TIMES, extract_vars,
#                  omp_set_num_threads, omp_get_max_threads)

from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))



domain = 'd02'
filein = f'/20121600/wrfout_{domain}_2020-12-18_05:00:00'
ds_wrf_file = str(wrf_dir_new) + filein


wrf_filein = date.today().strftime('/%y%m%d00/')
wrf_filein = '/20121100/'
wrf_file_dir = str(wrf_dir_new) + wrf_filein



filein = wrf_file_dir

wrf_ds, xy_np = readwrf(filein,domain)



# pathlist = sorted(Path(filein).glob(f'wrfout_{domain}_*00'))
# if domain == 'd02':
#     pathlist = pathlist[:61]
# else:
#     pass
# ds = xr.open_dataset(pathlist[0])
# wrfin = [Dataset(x) for x in pathlist]

# start = time.time()
# my_cache = extract_vars(wrfin, ALL_TIMES, ("T2", "U10", "V10", "RAINC", "RAINSH",
#                                            "RAINNC", "SNOWNC", "SNOWC", "SNOWH"))

# end = time.time()
# print ("Time taken to build cache: ", (end-start), "s")

# omp_set_num_threads(4)
# print (omp_get_max_threads())

# vars = ("rh2", "uvmet10_wspd_wdir")

# # No cache
# start = time.time()
# for var in vars:
#     v = getvar(wrfin, var, ALL_TIMES)
# end = time.time()
# no_cache_time = (end-start)

# print ("Time taken without variable cache: ", no_cache_time, "s")

# With a cache
# start = time.time()
# for var in vars:
#     v = getvar(wrfin, var, ALL_TIMES, cache=my_cache)
# end = time.time()
# cache_time = (end-start)

# print ("Time taken with variable cache: ", cache_time, "s")

# improvement = ((no_cache_time-cache_time)/no_cache_time) * 100
# print ("The cache decreased computation time by: ", improvement, "%")

# print('Begin reeadwrf')
# ds_list, time_list, attributes = [], [], []
# pathlist = sorted(Path(filein).glob(f'wrfout_{domain}_*00'))


# def preproc(ds):
#     ds = ds.assign({'stime': (['time'], ds.time)}).drop('time').rename({'time': 'ntime'})
#     # we might need to tweak this a bit further, depending on the actual data layout
#     return ds

# DS = xr.open_mfdataset( 'eraINTERIM_t2m_*.nc', concat_dim='cases', preprocess=preproc)




# ds_list = []
# for path in pathlist:
#     path_in_str = str(path)
#     ds = xr.open_dataset(path_in_str) 
#     ds_list.append(ds)   

# ds_test = xr.combine_nested(ds_list, 'time')

### Timer
print("Run Time: ", datetime.now() - startTime)


#     wrf_file = Dataset(path_in_str,'r')

#     time         = getvar(wrf_file, "times", timeidx=0)
#     Ti           = getvar(wrf_file, "T2")
#     T            = Ti-273.15
#     T.attrs      = Ti.attrs
#     T.attrs['description'] = "2m TEMP"
#     T.attrs['units'] = "C"
#     Hi           = np.array(getvar(wrf_file, "rh2")) * 1.0
#     H            = xr.DataArray(Hi, name='H', dims=('south_north', 'west_east'))
#     H.attrs      = Ti.attrs
#     H.attrs['units'] = "(%)"
#     H.attrs['description'] = "2m RELATIVE HUMIDITY"
#     wsp_wdir     = g_uvmet.get_uvmet10_wspd_wdir(wrf_file,units='km h-1')
#     wsp_array    = np.array(wsp_wdir[0])
#     wdir_array   = np.array(wsp_wdir[1])
#     W            = xr.DataArray(wsp_array, name='W', dims=('south_north', 'west_east'))
#     WD           = xr.DataArray(wdir_array, name='WD', dims=('south_north', 'west_east'))
#     W.attrs      = wsp_wdir.attrs
#     W.attrs['description'] = "10m WIND SPEED"
#     WD.attrs      = wsp_wdir.attrs
#     WD.attrs['description'] = "10m WIND DIRECTION"
#     WD.attrs['units'] = "degrees"

#     U10i           = np.array(getvar(wrf_file, "U10")) *1.0
#     U10            = xr.DataArray(U10i, name='U10', dims=('south_north', 'west_east'))
#     U10.attrs      = Ti.attrs
#     U10.attrs['units'] = "m s-1"
#     U10.attrs['description'] = "U at 10 M"

#     V10i           = np.array(getvar(wrf_file, "V10")) *1.0
#     V10            = xr.DataArray(V10i, name='V10', dims=('south_north', 'west_east'))
#     V10.attrs      = Ti.attrs
#     V10.attrs['units'] = "m s-1"
#     V10.attrs['description'] = "V at 10 M"

#     ##varied parameterization scheme to forecast rain..note this is a sum of rain from the starts of the model run  
#     rain_ci   = getvar(wrf_file, "RAINC")
#     rain_c    = np.array(rain_ci)
#     rain_sh   = np.array(getvar(wrf_file, "RAINSH"))
#     rain_nc   = np.array(getvar(wrf_file, "RAINNC"))
#     qpf_i     = rain_c + rain_sh + rain_nc
#     qpf       = np.where(qpf_i>0,qpf_i, qpf_i*0)
#     r_o       = xr.DataArray(qpf, name='r_o', dims=('south_north', 'west_east'))
#     r_o.attrs = rain_ci.attrs
#     r_o.attrs['description'] = "ACCUMULATED TOTAL PRECIPITATION"

#     SNWi           = np.array(getvar(wrf_file, "SNOWNC")) *1.0
#     SNW            = xr.DataArray(SNWi, name='SNW', dims=('south_north', 'west_east'))
#     SNW.attrs      = Ti.attrs
#     SNW.attrs['units'] = "cm"
#     SNW.attrs['description'] = "ACCUMULATED TOTAL GRID SCALE SNOW AND ICE"

#     SNOWCi           = np.array(getvar(wrf_file, "SNOWC")) *1.0
#     SNOWC            = xr.DataArray(SNOWCi, name='SNOWC', dims=('south_north', 'west_east'))
#     SNOWC.attrs      = Ti.attrs
#     SNOWC.attrs['units'] = ""
#     SNOWC.attrs['description'] = "FLAG INDICATING SNOW COVERAGE (1 FOR SNOW COVER)"

#     SNOWHi           = np.array(getvar(wrf_file, "SNOWH")) *1.0
#     SNOWH            = xr.DataArray(SNOWHi, name='SNOWH', dims=('south_north', 'west_east'))
#     SNOWH.attrs      = Ti.attrs
#     SNOWH.attrs['units'] = "m"
#     SNOWH.attrs['description'] = "PHYSICAL SNOW DEPTH"

#     # # Extract the pressure, geopotential height, and wind variables
#     # p = getvar(wrf_file, "pressure")
#     # z = getvar(wrf_file, "z", units="dm")
#     # ua = getvar(wrf_file, "ua", units="m s-1")
#     # va = getvar(wrf_file, "va", units="m s-1")
#     # wspd = getvar(wrf_file, "wspd_wdir", units="m s-1")[0,:]

#     # # Interpolate geopotential height, u, and v winds to 500 hPa
#     # ht_500i = interplevel(z, p, 500)
#     # u_500i = interplevel(ua, p, 500)
#     # v_500i = interplevel(va, p, 500)
#     # wspd_500i = interplevel(wspd, p, 500)

#     # ht_500i           = np.array(ht_500i) *1.0
#     # HT500            = xr.DataArray(ht_500i, name='HT500', dims=('south_north', 'west_east'))
#     # HT500.attrs      = Ti.attrs
#     # HT500.attrs['units'] = "m"
#     # HT500.attrs['description'] = "500 hPa geopotential height"

#     # u_500i           = np.array(u_500i) *1.0
#     # U500            = xr.DataArray(u_500i, name='U500', dims=('south_north', 'west_east'))
#     # U500.attrs      = Ti.attrs
#     # U500.attrs['units'] = "m s-1"
#     # U500.attrs['description'] = "500 hPa U winds"

#     # v_500i           = np.array(v_500i) *1.0
#     # V500            = xr.DataArray(v_500i, name='V500', dims=('south_north', 'west_east'))
#     # V500.attrs      = Ti.attrs
#     # V500.attrs['units'] = "m s-1"
#     # V500.attrs['description'] = "500 hPa U winds"

#     # wspd_500i           = np.array(wspd_500i) *1.0
#     # WSP500            = xr.DataArray(wspd_500i, name='WSP500', dims=('south_north', 'west_east'))
#     # WSP500.attrs      = Ti.attrs
#     # WSP500.attrs['units'] = "m s-1"
#     # WSP500.attrs['description'] = "500 hPa wind speeds"


#     var_list = [H,T,W,WD,r_o, SNW, SNOWC, SNOWH, U10, V10]
#     ds = xr.merge(var_list)
#     ds_list.append(ds)
#     time_list.append(time)
#     attributes.append(path_in_str)

# ### Combine xarrays and rename to match van wangers defs 
# wrf_ds = xr.combine_nested(ds_list, 'time')
# wrf_ds = wrf_ds.rename_vars({"T2":"T"})

# wrf_file = Dataset(attributes[0],'r')
# nc_attrs = wrf_file.ncattrs()
# for nc_attr in nc_attrs:
#     # print('\t%s:' % nc_attr, repr(wrf_file.getncattr(nc_attr)))
#     wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

# if args:
#     xy_np    = np.array(ll_to_xy(wrf_file, float(args[0]), float(args[1])))
# else:
#     xy_np    = None

# print('End reeadwrf')
# return wrf_ds, xy_np