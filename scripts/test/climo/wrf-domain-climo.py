#!/Users/crodell/miniconda3/envs/fwx/bin/python

"""
A script to create climatology for both the 12km/4km wrf domains.
The climatology will only span the years once the BSC domain was made operational from 1 Jan 2021 to present
"""
import context
import zarr
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import flox.xarray
from dask.distributed import LocalCluster, Client

from utils.compressor import compressor
from utils.climatology import get_daily_files, hour_qunt, concat_ds, slice_ds
from context import data_dir


runAll = datetime.now()
print("Start running all: ", runAll)
### On workstation
### http://137.82.23.185:8787/status
### On personal
###  http://10.0.0.8:8787/status
cluster = LocalCluster(
    n_workers=2,
    memory_limit="22GB",
    processes=False,
)
client = Client(cluster)
# print(client)

# ds = xr.open_zarr(file_name)

# for domain in ['d02', 'd03']:
#   for var in ['S', 'R', 'U']:
# for domain in ['d02']:
#   for var in ['S']:
var = "U"
domain = "d03"
save_dir = Path(str(data_dir) + "/wrf/climo/")
save_dir.mkdir(parents=True, exist_ok=True)
fwf = True
model = "wrf"
method = "daily"
# if var == 'U':
#     method = "daily"
# else:
#     method = 'hourly'
start = "2021-01-01"
stop = "2023-10-31"
quantile = 1

static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model}-{domain}.nc"
)
file_name = (
    str(save_dir)
    + f"/{var}-{method}-{domain}-climatology-{start.replace('-','')}-{stop.replace('-','')}-min.zarr"
)
print(file_name)
## get all files for era5-land of fwf
pathlist, x, y = get_daily_files(fwf, method, start, stop, domain, model)


## open =, chunk and combine into single dask chunk dataset
openT = datetime.now()
print("Opening at: ", openT)
ds = concat_ds(pathlist, var, x, y)
print("Opening Time: ", datetime.now() - openT)

# print(ds)

group = datetime.now()
print("Grouping at: ", group)
# ds1 = ds.groupby("time.dayofyear").apply(mod_group)
ds = (
    ds.chunk({"time": -1})
    .groupby("time.month")
    .min(dim="time", skipna=False, method="cohorts", engine="flox")
)
print("Grouping Time: ", datetime.now() - group)
# print(ds)

# dask.visualize(ds)
# Add some dataset attributes
ds.attrs["pyproj_srs"] = static_ds.attrs["pyproj_srs"]
ds.attrs[
    "descriptionq"
] = f"3 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"
ds[var].attrs["pyproj_srs"] = static_ds.attrs["pyproj_srs"]

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
