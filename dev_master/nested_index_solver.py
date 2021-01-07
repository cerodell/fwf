#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import json
import numpy as np
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from dev_utils.geoutils import jsonmask
from dev_utils.make_intercomp import daily_merge_ds
from wrf import ll_to_xy, xy_to_ll, geo_bounds, get_cartopy, getvar, cartopy_xlim, cartopy_ylim

import string

from context import data_dir, xr_dir, wrf_dir, root_dir, tzone_dir, wrf_dir_new
from datetime import datetime, date, timedelta
startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
import salem




## define the number of grids you want in each file for the point click forecasts
## for now it must be under 26 as files as deind by alphabet ie: file-ab.josn
n = 24 

## define any date of the fwf datasets for d02 and d03
forecast_day = datetime.today().strftime('%Y%m%d')
forecast_day = '20201224'
print(forecast_day)

### Get Path to most recent FWI forecast and open 
hourly_file_dir_d02 = str(data_dir) + str(f"/test/fwf-hourly-{forecast_day}00-d02.zarr") 
hourly_file_dir_d03 = str(data_dir) + str(f"/test/fwf-hourly-{forecast_day}00-d03.zarr") 

### Open datasets
hourly_ds_d02 = xr.open_zarr(hourly_file_dir_d02)
hourly_ds_d03 = xr.open_zarr(hourly_file_dir_d03)

### open wrf file
wrf_filein = "/wrf/"
wrf_file_dir = str(data_dir) + wrf_filein
wrf_file_dir = sorted(Path(wrf_file_dir).glob(f'wrfout_d02_*'))
wrf_file = Dataset(wrf_file_dir[0],'r')


def mask_nested(array, mask):
    i, j = np.indices(array.shape)
    j_true = np.isin(j, unique_x)
    i_true = np.isin(i, unique_y)
    nested_mask = np.where((j_true == True) & (i_true == True), array, mask)
    return nested_mask


def new_domain(ds, n):
    """
    Calculates the Fine Fuel Moisture Code at a one-hour interval writes/outputs as an xarray
    
    Parameters
    ----------

    ds: dataset of wrf domains 
    n : number of grids in kdtree grid for point click forecasts

    Returns
    -------
    
    hourly_ds: DataSet
        - Adds FFMC and m_o dataset
        """
    xlats = ds.XLAT.values
    xlons = ds.XLONG.values
    shape = xlats.shape

    value_list = []
    for i in range(200,shape[0]):
        if i % n == 0:
            value_list.append(i)
    shape_diff_0 = shape[0] - value_list[-1] 
    print(f"shape 0 differential {shape_diff_0}")
    if shape_diff_0 % 2 == 0:
        y1, y2 = int(shape_diff_0/2), int(shape_diff_0/2)
    else:
        y1 = int(np.floor(shape_diff_0/2))
        y2 = int(y1 + 1)

    value_list = []
    for i in range(200,shape[1]):
        if i % n == 0:
            value_list.append(i)
    shape_diff_1 = shape[1] - value_list[-1] 
    print(f"shape 1 differential {shape_diff_1}")
    if shape_diff_1 % 2 == 0:
        x1, x2 = int(shape_diff_1/2), int(shape_diff_1/2)
    else:
        x1 = int(np.floor(shape_diff_1/2))
        x2 = int(x1 + 1)
    if (x2+x1) == shape_diff_1 and (y2+y1) == shape_diff_0:
        pass
    else:
        print('Error: New domain shape wont work')
        exit

    xlats = xlats[y1:,x1:]
    xlats = xlats[:-y2,:-x2]

    xlons = xlons[y1:,x1:]
    xlons = xlons[:-y2,:-x2]

    return xlats, xlons, x1, x2, y1, y2

if n > 26:
    print("Error: needs to be 26 or smaller for indexing method to work")
else:
    pass

## get new domains sized for n number of grids in each file for webpage
xlats_d02, xlons_d02, x1_d02, x2_d02, y1_d02, y2_d02 = new_domain(hourly_ds_d02, n)
xlats_d03, xlons_d03, x1_d03, x2_d03, y1_d03, y2_d03 = new_domain(hourly_ds_d03, n)

## flatten d03 lat/lon grids to find associated index d02
lats = xlats_d03.flatten()
lons = xlons_d03.flatten()
xy_np  = ll_to_xy(wrf_file, lats, lons)

## get x index and find unique values
x = xy_np[0]
unique_x, index_x, counts_x = np.unique(x, return_index = True, return_counts = True)
## get y index and find unique values
y = xy_np[1]
unique_y, index_y, counts_y = np.unique(y, return_index = True, return_counts = True)


## TODO should wirte conditional statement to verify equal size near realiteve bounds
## For now just print and confirm 

## create new lat array of d02 with grids that define d03
## and print related details of grid dimentions size and bonds
# xlats_d02_nested = 
xlats_d02_nested = xlats_d02[:, unique_x]
xlats_d02_nested = xlats_d02_nested[unique_y, :]
d02_shape_lats = xlats_d02_nested.shape
dx_d02 = float(hourly_ds_d02.DX)/1000 ## grid size in km 
dy_d02 = float(hourly_ds_d02.DY)/1000 ## grid size in km 
print(f"d02 shape {d02_shape_lats}")
print(f"d02 km {d02_shape_lats[0]*dy_d02}")
print(f"d02 km {d02_shape_lats[1]*dx_d02}")
print(f"d02 min {xlats_d02_nested.min()}")
print(f"d02 max {xlats_d02_nested.max()}")

## and print related details of grid dimentions size and bonds of d03 to compare
d03_shape = xlats_d03.shape
dx_d03 = float(hourly_ds_d03.DX)/1000 ## grid size in km 
dy_d03 = float(hourly_ds_d03.DY)/1000 ## grid size in km 
print(f"d03 shape {d03_shape}")
print(f"d03 km {d03_shape[0]*dy_d03}")
print(f"d03 km {d03_shape[1]*dx_d03}")
print(f"d03 min {xlats_d03.min()}")
print(f"d03 max {xlats_d03.max()}")

## create new lon array of d02 with grids that define d03
xlons_d02_nested = xlons_d02[:, unique_x]
xlons_d02_nested = xlons_d02_nested[unique_y, :]
d02_shape_lons = xlons_d02_nested.shape
print(f"d02 shape {d02_shape_lons}")
print(f"d02 km {d02_shape_lons[0]*dy_d02}")
print(f"d02 km {d02_shape_lons[1]*dx_d02}")
print(f"d02 min {xlons_d02_nested.min()}")
print(f"d02 max {xlons_d02_nested.max()}")

## and print related details of grid dimentions size and bonds of d03 to compare
d03_shape_lons = xlons_d03.shape
print(f"d03 shape {d03_shape_lons}")
print(f"d03 km {d03_shape_lons[0]*dy_d03}")
print(f"d03 km {d03_shape_lons[1]*dx_d03}")
print(f"d03 min {xlons_d03.min()}")
print(f"d03 max {xlons_d03.max()}")


## write json file of useful index information to be used in other scripts 
nest_index = {'n': n,
              'x1_d02': x1_d02,
              'x2_d02': x2_d02,
              'y1_d02': y1_d02, 
              'y2_d02': y2_d02,
              'x1_d03': x1_d03,
              'x2_d03': x2_d03,
              'y1_d03': y1_d03, 
              'y2_d03': y2_d03,
              'unique_x': unique_x.tolist(),
              'unique_y': unique_y.tolist(),   
}

ones = np.ones_like(xlats_d02)
i, j = np.indices(ones.shape)
j_true = np.isin(j, unique_x)
i_true = np.isin(i, unique_y)
nested_mask = np.where((j_true== True) & (i_true== True), ones, 0)
unique, index, counts = np.unique(nested_mask, return_index = True, return_counts = True)
cs = plt.contourf(nested_mask)
cbar = plt.colorbar(cs)

# xlats_d02.shape
# hourly_ds_d02.F.shape
# ## Write json file to defind dir
# make_dir = Path(str(root_dir) + "/json/" )
# make_dir.mkdir(parents=True, exist_ok=True) 
# with open(str(make_dir) + f"/nested-index.json","w") as f:
#     json.dump(nest_index,f)

# print(f"{str(datetime.now())} ---> wrote json nested index to:  " + str(make_dir) + f"/nested-index.json.json")

# ### Timer
print("Run Time: ", datetime.now() - startTime)





