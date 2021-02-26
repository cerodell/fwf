import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 8, 20)

domain = "d02"
terrain = str(data_dir) + f"/terrain/hgt_wrf_{domain}.nc"
ds_terrain = xr.open_dataset(terrain)

# terrain = str(fwf_zarr_dir) + f'/hgt_wrf_{domain}.nc'
# ds_terrain = xr.open_dataset(terrain)


## Foliar Moisture Content Determination


ELV, LAT, LON = (
    ds_terrain.HGT.values[0, :, :],
    ds_terrain.XLAT.values[0, :, :],
    ds_terrain.XLONG.values[0, :, :],
)

shape = LAT.shape
zero_full = np.zeros(shape, dtype=float)

###################    Foliar Moisture Content:  #######################
########################################################################
## Solve Normalized latitude (degrees) with no terrain data (1)
# LATN = 46 + 23.4 * np.exp(-0.0360 * (150 - ds_terrain.XLONG))

## Solve Julian date of minimum FMC with no terrain data (2)
# D_o = 151 * (ds_terrain.XLAT/LATN)

## Solve Normalized latitude (degrees) with terrain data (3)
LATN = 43 + 33.7 * np.exp(-0.0351 * (150 - LON))

## Solve Julian date of minimum FMC with no terrain data (4)
D_o = 142.1 * (LAT / LATN) + 0.0172 * ELV

## Get day of year or Julian date
D_j = int(date.strftime("%j"))

## Solve Number of days between the current date and D_o (5)

ND = abs(D_j - D_o)

## Solve Foliar moisture content(%) where ND < 30 (6)

FMC_low = xr.where(ND < 30.0, 85 + 0.0189 * ND ** 2, zero_full)

## Solve Foliar moisture content(%) where 30 <= ND < 50 (7)

FMC_mid = xr.where(
    (ND >= 30) & (ND < 50), 32.9 + 3.17 * ND - 0.0288 * ND ** 2, zero_full
)

## Solve Foliar moisture content(%) where ND >= 50 (8)

FMC_high = xr.where(ND >= 50, 120, zero_full)

## Combine all FMC over the domain

FMC = FMC_low + FMC_mid + FMC_high


###################    Surface Fuel Consumption  #######################
########################################################################
