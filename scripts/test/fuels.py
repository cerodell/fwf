""""
This script take of fuels data for the US and Canada and converst them to CFFDRS fuel types.

Also, transform the fuels data to the same domain as the met wrf domains the
masks and replace (mosacis) into one simple gridded array.

"""


import context
import json
import salem
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from affine import Affine
from pathlib import Path
from netCDF4 import Dataset
from osgeo import osr, gdal, ogr

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

## Choose wrf domain
domain = "d02"

save_zarr = str(data_dir) + f"/fbp/fuels-wrf4-{domain}.zarr"
## Path to Fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"
## Path to any wrf file used in transformation
# wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18093000/wrfout_{domain}_2018-10-02_11:00:00"
wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"

## Path to 2014 nrcan fuels data tif
fbp2014_filein = (
    str(data_dir) + "/fbp/National_FBP_Fueltypes_version2014b/nat_fbpfuels_2014b.tif"
)


## Path to 2016 land fire US fuels data tif
us_filein = str(data_dir) + "/fbp/LF2020_FBFM13_200_CONUS/Tif/LC20_F13_200.tif"

## Open all files mentioned above
fc_df = pd.read_csv(fuel_converter)
wrf_ds = salem.open_xr_dataset(wrf_filein)
fbp2014_tiff = salem.open_xr_dataset(fbp2014_filein)
us_tiff = salem.open_xr_dataset(us_filein)


## Using nearest neighbor transformation tif to wrf domain
fbp2014_ds = wrf_ds.salem.transform(fbp2014_tiff.data)
us_ds = wrf_ds.salem.transform(us_tiff.data)


## take US Anderson 13 fuel valsue and convert to CFFDRS fuel types
us_array = us_ds.values


def getunique(array):
    unique, count = np.unique(array[~np.isnan(array)], return_counts=True)
    unique = np.unique(array[~np.isnan(array)]).astype(int)
    return unique, count


us_unique, us_count = getunique(us_array)


for i in range(len(fc_df.LF_16.values)):
    if fc_df.LF_16[i] == -99:
        pass
    else:
        us_array[us_array == fc_df.LF_16[i]] = fc_df.National_FBP_Fueltypes_2014[i]
us_unique_new, us_count_new = getunique(us_array)

## with converter US fuels in CFFDRS mask and replace location of missing data that use array can fill
fbp2014 = np.array(fbp2014_ds.data)
fbp2014[fbp2014 == 0] = np.nan
ind = np.isnan(fbp2014)
fbp2014[ind] = us_array[ind]
fbp_unique, fbp_count = getunique(fbp2014)

## loop all tiffs of AK to gridded adn mask fuels type tag to be the same as CFFDRS
folders = ["%.2d" % i for i in range(1, 21)]
print(folders)
for folder in folders:
    ak_filein = (
        str(data_dir) + f"/fbp/{folder}_AK_140CFFDRS/AK_140CFFDRS\AK_140CFFDRS.tif"
    )
    ak_tiff = salem.open_xr_dataset(ak_filein)
    ak_ds = wrf_ds.salem.transform(ak_tiff.data)
    ak_array = ak_ds.values
    for i in range(len(fc_df.AK_Fuels.values)):
        if fc_df.AK_Fuels[i] == -99:
            pass
        else:
            ak_array[ak_array == fc_df.AK_Fuels[i]] = fc_df.National_FBP_Fueltypes_2014[
                i
            ]

    ind = np.isnan(fbp2014)
    fbp2014[ind] = ak_array[ind]

fbp_unique, fbp_count = getunique(fbp2014)

## concidered remianing missing data to be water
ind = np.isnan(fbp2014)
fbp2014[np.isnan(fbp2014)] = 118

## make dataset add coordinates and write to zarr file
fuels_ds = xr.DataArray(fbp2014, name="fuels", dims=("south_north", "west_east"))
T2 = wrf_ds.T2
fuels_ds = xr.merge([fuels_ds, T2])
fuels_ds = fuels_ds.drop_vars("T2")
fuels_final = fuels_ds.isel(Time=0)
fuels_final.to_zarr(save_zarr, mode="w")

### Timer
print("Total Run Time: ", datetime.now() - startTime)
