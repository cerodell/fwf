#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import os
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF
from utils.read_wrfout import readwrf

from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir, wrf_dir_new, nc_dir
import warnings

from netCDF4 import Dataset
from wrf import getvar, omp_set_num_threads, omp_get_max_threads, ALL_TIMES


wrf_dir = "/Volumes/cer/fireweather/data/FWF-WAN00CG-01/fwf-daily-2021020106-d03.zarr/"

ds = xr.open_zarr(wrf_dir)


# ar = np.random.rand(1200,20000)
# shape = ar.shape
# e_full    = np.full(shape,math.e, dtype=float)

# startTime = datetime.now()
# arr=np.exp(ar)
# print("exp: ", datetime.now() - startTime)

# startTime = datetime.now()
# test = np.power(e_full, ar)
# print("power: ", datetime.now() - startTime)

wrf_model = "WAN00CP-04"

zarr_dir = f"/Users/rodell/Google Drive/My Drive/{wrf_model}/"
save_dir = f"/Volumes/cer/fireweather/data/{wrf_model}/"


date_range = pd.date_range("2018-05-20", "2018-05-31")


for domain in ["d02", "d03"]:
    for date in date_range:
        startTime = datetime.now()
        zarr_date = date.strftime("%Y%m%d06")
        zarr_file = f"wrfout-{domain}-{zarr_date}.zarr"
        print(zarr_file)
        zarr_file_dir = str(zarr_dir) + zarr_file
        ds = xr.open_zarr(zarr_file_dir)
        ds.to_zarr(save_dir + zarr_file)
        print("File Run Time: ", datetime.now() - startTime)


# for path in pathlist:
#   startTime = datetime.now()
#   ds = xr.open_zarr(path)
#   save_ds = str(path).rsplit('/',1)[1]
#   print(save_dir + save_ds)
#   ds.to_zarr(save_dir + save_ds)
#   print("File RUn Time: ", datetime.now() - startTime)
#         ## Open time zones dataset...each grids offset from utc time

# # yesterdays_date, domain = '2021011606', 'd02'
# # # hourly_file_dir = str(data_dir) + str(f"/FWF-WAN00CG-01/fwf-hourly-{yesterdays_date}-{domain}.zarr")

# # hourly_file_dir =  str(f"/Users/rodell/Desktop/WAN00CG-01/wrfout-{domain}-{yesterdays_date}.zarr")

# # wrf_ds = xr.open_zarr(hourly_file_dir)
# # tzone_ds = xr.open_dataset(str(tzone_dir) + f"/tzone_wrf_{domain}.nc")

# # yesterdays_date, domain = '2021011906', 'd02'
# # hourly_file_dir = str(data_dir) + str(f"/FWF-WAN00CG-01/fwf-daily-{yesterdays_date}-{domain}.zarr")
# # previous_daily_ds = xr.open_zarr(hourly_file_dir)


# # print("Create Daily ds")

# ### Call on variables
# tzone = tzone_ds.Zone.values
# shape = np.shape(wrf_ds.T[0,:,:])

# ## create I, J for quick indexing
# I,J = np.ogrid[:shape[0],:shape[1]]

# ## determine index for looping based on length of time array and initial time
# time_array = wrf_ds.Time.values
# int_time = int(pd.Timestamp(time_array[0]).hour)
# length = len(time_array)
# num_days = [i-12 for i in range(1, length) if i%24 == 0]
# index    = [i-int_time if 12-int_time >= 0 else i+24-int_time for i in num_days]
# print(f'index of times {index} with initial time {int_time}Z')
# ## loop every 24 hours at noon local
# files_ds = []
# for i in index:
#     # print(i)
#     ## loop each variable
#     mean_da = []
#     for var in wrf_ds.data_vars:
#         if var == 'SNOWC':
#             var_array = wrf_ds[var].values
#             noon = var_array[(i + tzone), I, J]
#             day = np.array(wrf_ds.Time[i+1], dtype ='datetime64[D]')
#             var_da = xr.DataArray(noon, name=var,
#             dims=('south_north', 'west_east'), coords= wrf_ds.isel(time = i).coords)
#             var_da["Time"] = day
#             mean_da.append(var_da)
#         else:
#             var_array = wrf_ds[var].values
#             noon_minus = var_array[(i + tzone - 1), I, J]
#             noon = var_array[(i + tzone), I, J]
#             noon_pluse = var_array[(i + tzone + 1), I, J]
#             noon_mean = (noon_minus + noon + noon_pluse) / 3
#             day = np.array(wrf_ds.Time[i+1], dtype ='datetime64[D]')
#             var_da = xr.DataArray(noon_mean, name=var,
#                     dims=('south_north', 'west_east'), coords= wrf_ds.isel(time = i).coords)
#             var_da["Time"] = day
#             mean_da.append(var_da)

#     mean_ds = xr.merge(mean_da)
#     files_ds.append(mean_ds)

# daily_ds = xr.combine_nested(files_ds, 'time')


# x_prev = 0
# for i, x_val in enumerate(daily_ds['r_o']):
#     daily_ds['r_o'][i] -= x_prev
#     x_prev = x_val

# # print(daily_ds['r_o'])
# length = 35
# test = [i for i in range(1, length) if i%24 == 0]
# len(test)

# length = len([i for i in range(1, 55) if i%24 == 0])

# a = []
# if not a:
#   print("List is empty")
# else:
#     print(a)

# ## create datarray for carry over rain, this will be added to the next days rain totals
# ## NOTE: this is rain that fell from noon local until 00Z.
# r_o_tomorrow_i = wrf_ds.r_o.values[index[0]+24] - daily_ds.r_o.values[0]
# r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
# r_o_tomorrow = np.stack(r_o_tomorrow)
# r_o_tomorrow_da = xr.DataArray(r_o_tomorrow, name="r_o_tomorrow",
#                 dims=('time','south_north', 'west_east'), coords= daily_ds.coords)

# daily_ds["r_o_tomorrow"] = r_o_tomorrow_da

# print("Daily ds done")
# try:
#     current_time = np.datetime_as_string(daily_ds.Time[0], unit='D')
# except:
#     current_time = np.datetime_as_string(daily_ds.Time, unit='D')

# previous_time = np.array(previous_daily_ds.Time.dt.strftime('%Y-%m-%dT%H'))
# try:
#     previous_time = datetime.strptime(str(previous_time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')
# except:
#     previous_time = datetime.strptime(str(previous_time), '%Y-%m-%dT%H').strftime('%Y%m%d%H')


# # daily_ds.T[0]
# previous_times = np.datetime_as_string(previous_daily_ds.Time, unit='D')
# index, = np.where(previous_times == current_time)
# index = int(index[0])

# previous_daily_ds['r_o']


# daily_ds['r_o'][0] = daily_ds['r_o'][0]

# # wrf_file_dir = str(data_dir) + "/test_wrf/wrfout-d02-2021011306.zarr"
# # wrf_file_dir = '/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18043000/wrfout_d03_2018-04-30_06:00:00'
# # wrf_file = Dataset(wrf_file_dir,'r')

# # ds = xr.open_dataset(wrf_file_dir)
# # test_ds, xx = readwrf(wrf_file_dir,domain)


# # current_time = np.datetime_as_string(ds.Time[-1], unit='h')

# # i = int(current_time[-2:])


# previous_time ="2222"

# if Path(wrf_file_dir).exists() == False:
#     print(f"{Path(wrf_file_dir).exists()}: No prior FFMC on date {previous_time}, will initialize with 85s")
# elif Path(wrf_file_dir).exists() == True:
#     print(f"{Path(wrf_file_dir).exists()}: Found previous FFMC on date {previous_time}, will merge with hourly_ds")
#     wrf_ds = xr.open_dataset(wrf_file_dir)

# else:
#     raise SyntaxError('ERROR: Can initialize fwf model')

# wrf_ds.T2.values
# wrf_ds.Times
# # time= wrf_ds.T.values

# # current_time = np.datetime_as_string(time, unit='h')
# tzone_ds = xr.open_dataset(str(tzone_dir) + f"/tzone_wrf_{domain}.nc")


# ### Read then open WRF dataset
# if wrf_file_dir.endswith('.zarr'):
#     print('zarr file')
#     wrf_ds = xr.open_zarr(wrf_file_dir)
# else:
#     print('nc file, use readwrf')
#     wrf_ds, xy_np = readwrf(wrf_file_dir, domain)
# attrs    = wrf_ds.attrs

# ds = xr.open_dataset(filein)


# var_list = ['T', 'U', 'V']

# for var in list(ds):
#     if var in var_list:
#         pass
#     else:
#         del ds[var]
# ds_object = ds._file_obj.ds


# slp = getvar(ds_object, "slp", timeidx  = ALL_TIMES)


# timefile = ds.Times.values[0].decode('UTF-8')
# timefile = timefile[:-9].replace('-', '')
# #path to save data
# save_dir = str(data_dir) + '/test_wrf/'

# date_range = pd.date_range('2021-01-22', '2021-01-22')

# ######## get variable attributes ##################
# filein = str(wrf_dir) + '21010900/'
# pathlist = sorted(Path(filein).glob(f'wrfout_{domain}_*00'))
# wrf_file = Dataset(str(pathlist[0]),'r')
# Ti                  = getvar(wrf_file, "T2")
# attrs               = Ti.attrs
# attrs['projection'] = str(attrs['projection'])

# ######## loop and add variable attributes ##################
# for domain in ['d03']:
#   for date in date_range:
#     wrf_filein = date.strftime('%Y%m%d06')
#     print(wrf_filein)
#     wrf_dir = f"/Users/rodell/Google Drive File Stream/My Drive/wrfout/wrfout-{domain}-{wrf_filein}.zarr"

#     wrf_ds = xr.open_zarr(wrf_dir)
#     wrf_ds = wrf_ds.compute()


#     print(list(wrf_ds))

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

#     for key in wrf_vars:
#         wrf_ds[wrf_vars[key]['name']].attrs = attrs
#         wrf_ds[wrf_vars[key]['name']].attrs['units'] = wrf_vars[key]['units']
#         wrf_ds[wrf_vars[key]['name']].attrs['description'] = wrf_vars[key]['description']

#     for key in div_vars:
#         wrf_ds[div_vars[key]['name']].attrs = attrs
#         wrf_ds[div_vars[key]['name']].attrs['units'] = div_vars[key]['units']
#         wrf_ds[div_vars[key]['name']].attrs['description'] = div_vars[key]['description']

#     for var in wrf_ds.data_vars:
#         wrf_ds[var] = wrf_ds[var].astype(dtype= 'float32')

#     time = np.array(wrf_ds.Time.dt.strftime('%Y-%m-%dT%H'))
#     timestamp = datetime.strptime(str(time[0]), '%Y-%m-%dT%H').strftime('%Y%m%d%H')

#     print(wrf_ds.r_o.attrs['description'])
#     wrf_ds_dir = str(save_dir) + str(f'wrfout-{domain}-{timestamp}.zarr')
#     wrf_ds = wrf_ds.compute()
#     wrf_ds.to_zarr(wrf_ds_dir)
#     print(f"wrote {wrf_ds_dir}")
#     print("readwrf run time: ", datetime.now() - startTime)


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
