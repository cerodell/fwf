#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from dev_utils.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir, wrf_dir_new, nc_dir
import warnings

from netCDF4 import Dataset
from wrf import (getvar, omp_set_num_threads, omp_get_max_threads)


domain = 'd03'
wrf_dir = "/Users/rodell/Google Drive File Stream/Shared drives/FORECASTSset1/WAN00CG-01/"
#path to save data
save_dir = str(data_dir) + '/test_wrf/'

date_range = pd.date_range('2021-01-22', '2021-01-22')

######## get variable attributes ##################
filein = str(wrf_dir) + '21010900/'
pathlist = sorted(Path(filein).glob(f'wrfout_{domain}_*00'))
wrf_file = Dataset(str(pathlist[0]),'r')
Ti                  = getvar(wrf_file, "T2")
attrs               = Ti.attrs
attrs['projection'] = str(attrs['projection'])

######## loop and add variable attributes ##################
for domain in ['d03']:
  for date in date_range:
    wrf_filein = date.strftime('%Y%m%d06')
    print(wrf_filein)
    wrf_dir = f"/Users/rodell/Google Drive File Stream/My Drive/wrfout/wrfout-{domain}-{wrf_filein}.zarr"

    wrf_ds = xr.open_zarr(wrf_dir)
    wrf_ds = wrf_ds.compute()


    print(list(wrf_ds))

    wrf_vars = {'T2':{'name': 'T','description': "2m TEMP", 'units': 'C' },
                'SNOWNC':{'name': 'SNW','description': "ACCUMULATED TOTAL GRID SCALE SNOW AND ICE", 'units': 'cm' },
                'SNOWC':{'name': 'SNOWC','description': "FLAG INDICATING SNOW COVERAGE (1 FOR SNOW COVER)", 'units': '' },
                'SNOWH':{'name': 'SNOWH','description': "PHYSICAL SNOW DEPTH", 'units': 'm' },
                'U10':{'name': 'U10','description': "U at 10 M", 'units': 'm s-1' },
                'V10':{'name': 'V10','description': "V at 10 M", 'units': 'm s-1' }}

    div_vars  = {'rh2':{'name': 'H','description': "2m RELATIVE HUMIDITY", 'units': '(%)'},
                    'wsp':{'name': 'W','description': "10m WIND SPEED", 'units': 'km h-1'},
                    'wdir':{'name': 'WD','description': "10m WIND DIRECTION", 'units': 'degrees'},
                    'precip':{'name': 'r_o','description': "ACCUMULATED TOTAL PRECIPITATION", 'units': 'mm'}}

    for key in wrf_vars:
        wrf_ds[wrf_vars[key]['name']].attrs = attrs
        wrf_ds[wrf_vars[key]['name']].attrs['units'] = wrf_vars[key]['units']
        wrf_ds[wrf_vars[key]['name']].attrs['description'] = wrf_vars[key]['description']

    for key in div_vars:
        wrf_ds[div_vars[key]['name']].attrs = attrs
        wrf_ds[div_vars[key]['name']].attrs['units'] = div_vars[key]['units']
        wrf_ds[div_vars[key]['name']].attrs['description'] = div_vars[key]['description']

    for var in wrf_ds.data_vars:
        wrf_ds[var] = wrf_ds[var].astype(dtype= 'float32')

    time = np.array(wrf_ds.Time.dt.strftime('%Y-%m-%dT%H'))
    timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

    print(wrf_ds.r_o.attrs['description'])
    wrf_ds_dir = str(save_dir) + str(f'wrfout-{domain}-{timestamp}.zarr')
    wrf_ds = wrf_ds.compute()
    wrf_ds.to_zarr(wrf_ds_dir)
    print(f"wrote {wrf_ds_dir}")
    print("readwrf run time: ", datetime.now() - startTime)













# def readwrf(filein, domain, save_dir, *args):
#     """
#     This function reads wrfout files and grabs required met variables for fire weather index calculations.  Writes/outputs as a xarray    

#         - wind speed (km h-1)
#         - temp (degC)
#         - rh (%)
#         - qpf (mm)
#         - snw (mm)

#     Parameters
#     ----------

#     files: str
#         - File directory to NetCDF files

#     Returns
#     -------

#     ds_wrf: DataSet
#         xarray DataSet
#     """
#     omp_set_num_threads(8)
#     print(f"read files with {omp_get_max_threads()} threads")
#     startTime = datetime.now()
#     print("begin readwrf: ", str(startTime))
#     ds_list, time_list, attributes = [], [], []
#     pathlist = sorted(Path(filein).glob(f'wrfout_{domain}_*00'))
#     wrf_file = Dataset(str(pathlist[0]),'r')
#     lats                = getvar(wrf_file, "XLAT")
#     lngs                = getvar(wrf_file, "XLONG")
#     Ti                  = getvar(wrf_file, "T2")
#     shape               = lats.values.shape
#     attrs               = Ti.attrs
#     attrs['projection'] = str(attrs['projection'])
#     nc_attrs            = wrf_file.ncattrs()


#     ## van wangers nameing convention and description 
#     wrf_vars = {'T2':{'name': 'T','description': "2m TEMP", 'units': 'C' },
#                 'SNOWNC':{'name': 'SNW','description': "ACCUMULATED TOTAL GRID SCALE SNOW AND ICE", 'units': 'cm' },
#                 'SNOWC':{'name': 'SNOWC','description': "FLAG INDICATING SNOW COVERAGE (1 FOR SNOW COVER)", 'units': '' },
#                 'SNOWH':{'name': 'SNOWH','description': "PHYSICAL SNOW DEPTH", 'units': 'm' },
#                 'U10':{'name': 'U10','description': "U at 10 M", 'units': 'm s-1' },
#                 'V10':{'name': 'V10','description': "V at 10 M", 'units': 'm s-1' }}
    
#     div_vars  = {'rh2':{'name': 'H','description': "2m RELATIVE HUMIDITY", 'units': '(%)'},
#                     'wsp':{'name': 'W','description': "10m WIND SPEED", 'units': 'km h-1'},
#                     'wdir':{'name': 'WD','description': "10m WIND DIRECTION", 'units': 'degrees'},
#                     'precip':{'name': 'r_o','description': "ACCUMULATED TOTAL PRECIPITATION", 'units': 'mm'}}

#     if domain == 'd02':
#         pathlist = pathlist[6:61]
#     else:
#         pathlist = pathlist[6:]

#     tdim, ydim, xdim = int(len(pathlist)), int(shape[0]), int(shape[1])
#     date_range = pd.date_range(str(pathlist[0])[-19:-6].replace('_', ' '), str(pathlist[-1])[-19:-6].replace('_', ' '), freq='H')
#     ds_dict = {}
#     ds_dict.update({"coords":{'Time': {'dims': ('time'), 'data': date_range}}})
#     ds_dict.update({"coords":{'XLAT': {'dims': ('south_north','west_east'), 'data': lats}}})
#     ds_dict.update({"coords":{'XLONG': {'dims': ('south_north','west_east'), 'data': lngs}}})

#     ds_dict['XLAT'] = {'dims': ('south_north','west_east'), 'data': lats}
#     ds_dict['XLONG'] = {'dims': ('south_north','west_east'), 'data': lngs}

#     for key in wrf_vars:
#         ds_dict[wrf_vars[key]['name']] = {'dims': ('time','south_north','west_east'), 
#                                             'data': np.zeros((tdim,ydim,xdim)),
#                                             'description': wrf_vars[key]['description'], 
#                                             'units': wrf_vars[key]['units']}
#     for key in div_vars:
#         ds_dict[div_vars[key]['name']] = {'dims': ('time','south_north','west_east'),
#                                                 'data': np.zeros((tdim,ydim,xdim)),
#                                                 'description': div_vars[key]['description'], 
#                                                 'units': div_vars[key]['units']}

#     for i in range(len(pathlist)):
#         path_in_str = str(pathlist[i])
#         ds = xr.open_dataset(path_in_str) 

#         for key in wrf_vars:
#             ds_dict[wrf_vars[key]['name']]['data'][i,:,:] = ds[key]

#         wrf_file = Dataset(path_in_str,'r')

#         ds_dict[div_vars['rh2']['name']]['data'][i,:,:]    = getvar(wrf_file, "rh2", meta=False)
#         wsp_wdir                                           = getvar(wrf_file, "uvmet10_wspd_wdir",units='km h-1', meta=False)
#         ds_dict[div_vars['wsp']['name']]['data'][i,:,:]    = wsp_wdir[0]
#         ds_dict[div_vars['wdir']['name']]['data'][i,:,:]   = wsp_wdir[1]

#         ds_dict[div_vars['precip']['name']]['data'][i,:,:] = ds["RAINC"] + ds["RAINSH"] + ds["RAINNC"]


#     ### dictionary to xarrays with van wangers nameing convention   
#     wrf_ds = xr.Dataset.from_dict(ds_dict)

#     nc_attrs = wrf_file.ncattrs()
#     for nc_attr in nc_attrs:
#         # print('\t%s:' % nc_attr, repr(wrf_file.getncattr(nc_attr)))
#         wrf_ds.attrs[nc_attr] = repr(wrf_file.getncattr(nc_attr))

#     if args:
#         xy_np    = np.array(ll_to_xy(wrf_file, float(args[0]), float(args[1])))
#     else:
#         xy_np    = None

#     time = np.array(wrf_ds.Time.dt.strftime('%Y-%m-%dT%H'))
#     timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

#     print(wrf_ds)
#     wrf_ds_dir = str(save_dir) + str(f'wrfout-{domain}-{timestamp}.zarr')
#     wrf_ds.to_zarr(wrf_ds_dir, "w")
#     print(f"wrote {wrf_ds_dir}")
#     print("readwrf run time: ", datetime.now() - startTime)

#     return wrf_ds, xy_np



# for domain in ['d02', 'd03']:
#   for date in date_range:
#     wrf_filein = date.strftime('%y%m%d00/')
#     wrf_file_dir = str(wrf_dir) + wrf_filein
#     print(wrf_file_dir)
#     readwrf(wrf_file_dir, domain, save_dir)