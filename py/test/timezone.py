import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from fwi.utils.wrf.read_wrfout import readwrf
from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir
import timezonefinder, pytz
from datetime import datetime
from pathlib import Path


filein = "/2019-08-19T00_ds_wrf.zarr"
ds_wrf_file = str(data_dir) + filein
ds_wrf = xr.open_zarr(ds_wrf_file)

filein = "/ds_tzone.zarr"
ds_tzone_file = str(tzone_dir) + filein
ds_tzone = xr.open_zarr(ds_tzone_file)

shape = ds_wrf.T.shape
shape = shape[1:]
print(shape, "SHAPE")

zero_full = np.zeros(shape, dtype=float)
i = 0
hour = np.datetime_as_string(ds_wrf.Time[18+i:20+i], unit='h')
print(hour)

def zone_means(ds_wrf):

    tzdict     = {"PDT": {'zone_id':7, 'noon':19 , 'plus': 20, 'minus':18},
                  "MDT": {'zone_id':6, 'noon':18 , 'plus': 19, 'minus':17},
                  "CDT": {'zone_id':5, 'noon':17 , 'plus': 18, 'minus':16},
                  "EDT": {'zone_id':4, 'noon':16 , 'plus': 17, 'minus':15},
                  "ADT": {'zone_id':3, 'noon':15 , 'plus': 16, 'minus':14}}
    
    
    # zone_id, noon, plus, minus = tzdict[tzone]['zone_id'], tzdict[tzone]['noon'], tzdict[tzone]['plus'], tzdict[tzone]['minus']

    ds_files = []
    for i in range(0,48,24):

        ds_list_sum = []
        for key in tzdict.keys():
            zone_id, noon, plus, minus = tzdict[key]['zone_id'], tzdict[key]['noon'], tzdict[key]['plus'], tzdict[key]['minus']

            da_mean = []
            for var in ds_wrf.data_vars:
                # print(ds_wrf[var])
                var_mean = ds_wrf[var][minus+i:plus+i].mean(axis=0)
                da_var = xr.where(ds_tzone != zone_id, zero_full, ds_wrf[var][minus+i:plus+i].mean(axis=0))
                da_var = np.array(da_var.Zone)
                time = ds_wrf.Time[noon+i]
                da_var = xr.DataArray(da_var, name=var, 
                        dims=('south_north', 'west_east'),coords={'noon':time})
                da_mean.append(da_var)

            
            ds_mean = xr.merge(da_mean)
            ds_list_sum.append(ds_mean)
        ds_sum = sum(ds_list_sum)
        ds_files.append(ds_sum)
    



        ds = xr.combine_nested(ds_files, 'noon')
    
    return ds

ds = zone_means(ds_wrf)












# shape = ds_wrf.T.shape
# shape = shape[1:]
# print(shape, "SHAPE")
# # i,j = 0, -1
# # Lat = float(ds_wrf.XLAT[i,j])
# # print(Lat, "lat")
# # Long = float(ds_wrf.XLONG[i,j])
# # print(Long, "long")

# tf = timezonefinder.TimezoneFinder()


# def mytimezone(Lat,Long):
#     timezone_str = tf.closest_timezone_at(lat=Lat, lng=Long, delta_degree=5)
#     common_name = pytz.timezone(timezone_str)
#     abbr = common_name.localize(datetime.now(), is_dst=None)
#     zone_abbr = abbr.tzname()
#     if zone_abbr is None:
#         zone_abbr = np.NaN
#         print ("Could not determine the time zone")
#     elif zone_abbr == "AKDT":
#         zone_abbr = 8
#     elif zone_abbr == "AKST":
#         zone_abbr = 8
#     elif zone_abbr == "PDT":
#         zone_abbr = 7
#     elif zone_abbr == "PST":
#         zone_abbr = 7
#     elif zone_abbr == "MDT":
#         zone_abbr = 6
#     elif zone_abbr == "MST":
#         zone_abbr = 6
#     elif zone_abbr == "CDT":
#         zone_abbr = 5
#     elif zone_abbr == "CST":
#         zone_abbr = 5
#     elif zone_abbr == "EDT":
#         zone_abbr = 4
#     elif zone_abbr == "EST":
#         zone_abbr = 4
#     elif zone_abbr == "ADT":
#         zone_abbr = 3
#     elif zone_abbr == "AST":
#         zone_abbr = 3
#     elif zone_abbr == "NDT":
#         zone_abbr = 3
#     elif zone_abbr == "NST":
#         zone_abbr = 3
#     else:
#         pass
#     return zone_abbr


# i_list = []
# for i in range(shape[0]):
#     print(f"{i} I of shape {shape[0]}" )
#     j_list = []
#     for j in range(shape[1]):
#         Lat = float(ds_wrf.XLAT[i,j])
#         Long = float(ds_wrf.XLONG[i,j])
#         # print(f"{Lat},{Long}")
#         timezone_str = mytimezone(Lat,Long)
#         j_list.append(timezone_str)
#     i_list.append(j_list)

# timezone_array = np.stack(i_list)


# make_dir = Path(str(xr_dir) + str('/') +  str(f"ds_zone.zarr"))

# da_zone = xr.DataArray(timezone_array, name='Zone', dims=('south_north', 'west_east'))
# ds_zone = xr.Dataset()

# # ds = xr.Dataset({})
# ds_zone['Zone'] = (('south_north', 'west_east'), da_zone)
# make_dir.mkdir(parents=True, exist_ok=True)

# ds_zone.compute()
# ds_zone.to_zarr(make_dir, "w")


# # print(ds_zone)

