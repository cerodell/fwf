#!/Users/crodell/miniconda3/envs/fwx/bin/python

import os
import json
import context
import salem
import zarr
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

import flox
import flox.xarray

from utils.compressor import compressor
from utils.climatology import get_daily_files
from context import root_dir

runTime = datetime.now()
print("Combine script started at: ", runTime)

from dask.distributed import LocalCluster, Client

cluster = LocalCluster(
    n_workers=1,
    #    threads_per_worker=,
    memory_limit="18GB",
    processes=False,
)
client = Client(cluster)
### # On workstation
### http://137.82.23.185:8787/status
### # On personal
###  http://10.0.0.88:8787/status
print(client)

save_dir = Path("/Volumes/WFRT-Ext22/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
var = "S"
fwf = True
method = "hourly"
start = "1991-01-01"
stop = "2020-12-31"


## get all files for era5-land of fwf
pathlist, x, y = get_daily_files(fwf, method, start, stop)

ds = (
    xr.open_dataset(str(pathlist[0]))["S"]
    .isel(time=0)
    .drop(["XLAT", "XLONG", "Time"])
    .chunk("auto")
)
ds_slice = xr.open_zarr(
    str(save_dir)
    + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i0j0-quant.zarr",
    chunks="auto",
)

dayofyear = ds_slice["dayofyear"].values
hour = ds_slice["hour"].values
quantile = ds_slice["quantile"].values
south_north = ds["south_north"].values
west_east = ds["west_east"].values

data = dask.array.full(
    (len(dayofyear), len(hour), len(quantile), len(south_north), len(west_east)),
    0,
    chunks=(4, 4, 8, 237, 517),
)
da = xr.DataArray(
    data=data,
    name=var,
    dims=["dayofyear", "hour", "quantile", "south_north", "west_east"],
    coords=dict(
        south_north=south_north,
        west_east=west_east,
        dayofyear=dayofyear,
        hour=hour,
        quantile=quantile,
    ),
)
# data=dask.array.full((len(dayofyear), len(hour), len(south_north), len(west_east)), 0, chunks=(4, 4, 237, 517))
# da = xr.DataArray(
#     data=data,
#     name = var,
#     dims=["dayofyear", "hour", "south_north", "west_east"],
#     coords=dict(
#         south_north = south_north,
#         west_east = west_east,
#         dayofyear = dayofyear,
#         hour=hour,
#     ),
# )
# (24, 711, 1551)
# (24, 711/3, 1551/3) = (24, 237, 517)
# (24, 711/9, 1551/11) = (24, 79, 141)
di, dj = 517, 237
for i in range(0, 3):
    ii = i + 1
    for j in range(0, 3):
        jj = j + 1
        ds_slice = xr.open_zarr(
            str(save_dir)
            + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}-quant.zarr",
            chunks="auto",
        )
        da[:, :, :, j * dj : jj * dj, i * di : ii * di] = ds_slice["S"]
        # da[:, :, j*dj: jj*dj, i*di: ii*di] = ds_slice['S']


ds_final = da.to_dataset()
ds_final = ds_final.chunk("auto")

compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)

ds_final.to_zarr(
    str(save_dir)
    + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-quant.zarr",
    mode="w",
    encoding={x: {"compressor": compressor} for x in ds_final},
)
print("Run Time: ", datetime.now() - runTime)
