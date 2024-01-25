#!/Users/crodell/miniconda3/envs/fwx/bin/python

import os
import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import flox
import flox.xarray

from utils.compressor import compressor
from utils.climatology import get_daily_files, hour_qunt, concat_ds, slice_ds
from context import root_dir

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file


from dask.distributed import LocalCluster, Client

# cluster = LocalCluster(
#     n_workers=2,
#     #    threads_per_worker=,
#     memory_limit="7GB",
#     processes=False,
# )
# client = Client(cluster)
# client = Client(processes=False)
# print(client)
## On workstation
# http://137.82.23.185:8787/status
## On personal
#  http://10.0.0.88:8787/status

save_dir = Path("/Volumes/WFRT-Ext22/ecmwf/era5-land/")
save_dir.mkdir(parents=True, exist_ok=True)
var = "S"
fwf = True
method = "hourly"
start = "1991-01-01"
stop = "2020-12-31"

file_name = (
    str(save_dir)
    + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-quant.zarr"
)

## get all files for era5-land of fwf
pathlist, x, y = get_daily_files(fwf, method, start, stop)


## open =, chunk and combine into single dask chunk dataset
runAll = datetime.now()
print("Start running all: ", runAll)
openT = datetime.now()
print("Opening at: ", openT)
ds = concat_ds(pathlist, var, x, y)
print("Opening Time: ", datetime.now() - openT)

dss = ds
# for k, gg in ds.groupby('time.dayofyear'):
#     print(k)
#     print(gg)

group = datetime.now()
print("Grouping at: ", group)
ds = ds.groupby("time.dayofyear").apply(hour_qunt)
print("Grouping Time: ", datetime.now() - group)

# Add some dataset attributes
ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
ds.attrs[
    "descriptionq"
] = f"30 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"
ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"

ds = ds.chunk("auto")

write = datetime.now()
print("Writing at: ", write)
ds.to_zarr(
    file_name,
    mode="w",
)
print("Write Time: ", datetime.now() - write)

print("Run Time: ", datetime.now() - runAll)
