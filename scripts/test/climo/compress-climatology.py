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

from context import root_dir

runTime = datetime.now()
print("Compression script started at: ", runTime)

from dask.distributed import LocalCluster, Client

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


ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext22/ecmwf/era5-land/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-quant-full.zarr"
)


def rechunk(ds):
    # ds = ds.load()
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    return ds


ds = rechunk(ds)

compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)

ds.to_zarr(
    str(save_dir)
    + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-compressed.zarr",
    mode="w",
    encoding={x: {"compressor": compressor} for x in ds},
)
print("Run Time: ", datetime.now() - runTime)
