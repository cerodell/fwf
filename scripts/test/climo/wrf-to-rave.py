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
var = "R"
save_name = f"rave-3km-climatology-20210101-20231031"
quant = "max"

target_ds = salem.open_xr_dataset(str(data_dir) + f"/static/static-rave-3km-grid.nc")

wrf_d02 = xr.open_zarr(
    str(data_dir)
    + f"/wrf/climo/m{var}-daily-d02-climatology-20210101-20231031-{quant}.zarr"
).rename({f"m{var}": var})

wrf_d03 = (
    xr.open_zarr(
        str(data_dir)
        + f"/wrf/climo/m{var}-daily-d03-climatology-20210101-20231031-{quant}.zarr"
    )
    .isel(south_north=slice(20, -20), west_east=slice(20, -20))
    .rename({f"m{var}": var})
)


wrf_d02 = target_ds.salem.transform(wrf_d02, interp="linear")
wrf_d03 = target_ds.salem.transform(wrf_d03, interp="linear")
ds_final = xr.where(~np.isnan(wrf_d03), wrf_d03, wrf_d02)
ds_final = xr.where(np.isnan(ds_final), 0, ds_final)


compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
write = datetime.now()
print("Writing at: ", write)
file_name = f"/Volumes/ThunderBay/CRodell/climo/{var}{quant.upper()}-{save_name}.zarr"
ds_final.to_zarr(
    file_name,
    mode="w",
    encoding={x: {"compressor": compressor} for x in ds_final},
)
print("Write Time: ", datetime.now() - write)
