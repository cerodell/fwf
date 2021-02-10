import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d03"

# file_dir = str(fwf_zarr_dir) + f"/fwf-daily-{domain}-2021020206.zarr"
# ds = xr.open_zarr(file_dir)

# # file_dir = str(wrf_dir) + f"/wrfout-{domain}-2021020206.zarr"
# # wrf_ds = xr.open_zarr(file_dir)


# for var in list(ds):
#     print(f"max of {var}: {ds[var].values.max()}")
#     print(f"min of {var}: {ds[var].values.min()}")
#     print(f"mean of {var}: {ds[var].values.mean()}")


ds = xr.open_zarr(str(data_dir) + "/intercomp/" + f"intercomp-{domain}-20210102.zarr")

for var in list(ds):
    print(f"max of {var}: {float(ds[var].max(skipna= True))}")
    print(f"min of {var}: {float(ds[var].min(skipna= True))}")
    print(f"mean of {var}: {float(ds[var].mean(skipna= True))}")
