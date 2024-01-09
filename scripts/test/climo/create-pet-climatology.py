#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.compressor import compressor

from context import root_dir

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file


# f'/Volumes/WFRT-Ext23/pet/{year}_daily_pet.nc'


save_dir = Path(str(root_dir) + "/data/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
data_dir = "/Volumes/WFRT-Ext23/pet/"
var = "pet"
start = "1990-01-01"
stop = "2020-12-31"
nwse = [86, -180, 15, -25]


pathlist = sorted(Path(data_dir).glob("*.nc"))[:-2]

# test = salem.open_xr_dataset(str(save_dir) + f"/{var}-climatology-{start.replace('-','')}-{stop.replace('-','')}.nc")

# era5_land = salem.open_xr_dataset('/Volumes/WFRT-Ext25/ecmwf/era5-land/199101/era5-land-1991010100.nc').isel(time =0 )
# ds = salem.open_xr_dataset(pathlist[0]).sel(latitude = slice(86,15), longitude = slice(-180,-25))
# pet_tets = ds.isel(time = 0)
# pet_test = ds.isel(time = 0)
# era5_land['pet'] = pet_tets['pet']


open = datetime.now()
ds = xr.concat(
    [
        xr.open_dataset(path, chunks="auto").sel(
            latitude=slice(86, 15), longitude=slice(-180, -25)
        )
        for path in pathlist
    ],
    dim="time",
)
print("Opening Time: ", datetime.now() - open)


def hour_mean(x):
    """
    function groups time to hourly and solves hourly mean

    """
    return x.groupby("time.hour").mean("time")


def day_max(x):
    """
    function groups time to daily and take daily max

    """
    return x.groupby("time.day").max("time")


## group data into months and solve for monthly average over the 30 years
group = datetime.now()
ds = ds.groupby("time.month").mean("time")
print("Grouping Time: ", datetime.now() - group)

computeTime = datetime.now()
ds = ds.compute()
print("Compute Time: ", datetime.now() - computeTime)

ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
ds.attrs["description"] = "30 year (1990-2020) monthly averaged reanalysis"

# ds, encoding = compressor(ds)
write = datetime.now()
ds.to_netcdf(
    str(save_dir)
    + f"/{var}-climatology-{start.replace('-','')}-{stop.replace('-','')}.nc",
    mode="w",
    # encoding = encoding
)
print("Write Time: ", datetime.now() - write)
