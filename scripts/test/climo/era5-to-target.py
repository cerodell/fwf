#!/Users/crodell/miniconda3/envs/fwx/bin/python
import context
import salem
import zarr
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime

from dask.distributed import LocalCluster, Client

from context import data_dir

# static-rave-3km.nc
save_name = "wrf-d03"
## Open gridded static

target_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d03.nc")
era5L_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-ecmwf-era5-land.nc"
)
climo_ds = xr.open_zarr(
    f"/Volumes/WFRT-Ext23/ecmwf/era5-land/S-hourly-climatology-19910101-20201231-compressed.zarr"
)

# ### On workstation
# ### http://137.82.23.185:8787/status
# ### On personal
# ###  http://10.0.0.88:8787/status
# cluster = LocalCluster(
#     n_workers=2,
#     #    threads_per_worker=,
#     memory_limit="16GB",
#     processes=False,
# )
# client = Client(cluster)
# print(client)

### get max values of S for everyday of year and transform to target grid and write to zarr
maxS = climo_ds.sel(quantile=1).max("hour").compute()
maxS.attrs = climo_ds.attrs
maxS["S"].attrs = climo_ds["S"].attrs
maxS = target_ds.salem.transform(maxS, interp="linear")
compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
write = datetime.now()
print("Writing at: ", write)
file_name = f"/Volumes/ThunderBay/CRodell/climo/SMAX-{save_name}-climatology-19910101-20201231.zarr"
maxS.to_zarr(
    file_name,
    mode="w",
    encoding={x: {"compressor": compressor} for x in maxS},
)
print("Write Time: ", datetime.now() - write)


### get min values of S for everyday of year and transform to target grid and write to zarr
minS = climo_ds.sel(quantile=0).min("hour").compute()
minS.attrs = climo_ds.attrs
minS["S"].attrs = climo_ds["S"].attrs
minS = target_ds.salem.transform(minS, interp="linear")
compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
write = datetime.now()
print("Writing at: ", write)
file_name = f"/Volumes/ThunderBay/CRodell/climo/SMIN-{save_name}-climatology-19910101-20201231.zarr"
minS.to_zarr(
    file_name,
    mode="w",
    encoding={x: {"compressor": compressor} for x in minS},
)
print("Write Time: ", datetime.now() - write)
