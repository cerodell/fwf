#!/Users/crodell/miniconda3/envs/fwx/bin/python

import os
import json
import context
import salem
import dask
import zarr
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import flox
import flox.xarray
from dask.distributed import LocalCluster, Client

from utils.compressor import compressor
from utils.climatology import get_daily_files, hour_qunt, concat_ds, slice_ds
from context import root_dir

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file


runAll = datetime.now()
print("Start running all: ", runAll)
### On workstation
### http://137.82.23.185:8787/status
### On personal
###  http://10.0.0.88:8787/status
cluster = LocalCluster(
    n_workers=2,
    #    threads_per_worker=,
    memory_limit="22GB",
    processes=False,
)
client = Client(cluster)
print(client)

save_dir = Path("/Volumes/WFRT-Ext22/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
var = "S"
fwf = True
method = "hourly"
start = "1991-01-01"
stop = "2020-12-31"

file_name = (
    str(save_dir)
    + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-std.zarr"
)

## get all files for era5-land of fwf
pathlist, x, y = get_daily_files(fwf, method, start, stop)


## open =, chunk and combine into single dask chunk dataset
openT = datetime.now()
print("Opening at: ", openT)
ds = concat_ds(pathlist, var, x, y)
print("Opening Time: ", datetime.now() - openT)

group = datetime.now()
print("Grouping at: ", group)
ds = ds.groupby("time.dayofyear").apply(hour_qunt)
print("Grouping Time: ", datetime.now() - group)

print(ds)
# dask.visualize(ds)
# Add some dataset attributes
ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
ds.attrs[
    "descriptionq"
] = f"30 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"
ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
# ds = ds.chunk("auto")


compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
write = datetime.now()
print("Writing at: ", write)
ds.to_zarr(
    file_name,
    mode="w",
    encoding={x: {"compressor": compressor} for x in ds},
)
print("Write Time: ", datetime.now() - write)

print("Run Time: ", datetime.now() - runAll)
