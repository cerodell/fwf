import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


from context import data_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

wrf_model = "wrf3"
domain = "d02"
filein = f"/Volumes/cer/fireweather/data/fwf-hourly-d02-2018040106-2018100106.zarr"
saveout = "/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/ZARR_Data/fwf-hourly-d02-2018040106-2018100106.nc"

ds = xr.open_zarr(filein)
ds.to_netcdf(saveout)


# static_in = str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
# static_out = f'/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/ZARR_Data/static-vars-{wrf_model}-{domain}.nc'
# static_ds = xr.open_zarr(static_in)

# static_ds = rechunk(static_ds)
# static_ds.to_netcdf(static_out)


ds = xr.open_zarr(filein)

var_list = ["XLAT", "XLONG", "ROS", "TFC", "HFI"]
ds_short = ds.drop_vars([i for i in list(ds) if i not in var_list])


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


ds_short = rechunk(ds_short)

ds_short.to_netcdf(saveout)


### Timer
print("Total Run Time: ", datetime.now() - startTime)
