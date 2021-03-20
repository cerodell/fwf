import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


from context import data_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


domain = "d02"
wrf_model = "wrf3"

pathlist = sorted(Path(fwf_zarr_dir).glob(f"fwf-hourly-{domain}-*"))
# pathlist = pathlist[:4]
startdate = str(pathlist[0])[-15:-5]
enddate = str(pathlist[-1])[-15:-5]


def read_zarr(f):
    ds = xr.open_zarr(f)
    ds = ds.isel(time=slice(0, 24))
    return ds


ds = xr.concat([read_zarr(f) for f in pathlist], dim="time")
ds = ds.chunk(chunks="auto")
ds = ds.unify_chunks()
for var in list(ds):
    ds[var].encoding = {}


save_file = (
    f"/Volumes/cer/fireweather/data/fwf-hourly-{domain}-{startdate}-{enddate}.zarr"
)
ds.to_zarr(save_file, mode="w")

print("Total Run Time: ", datetime.now() - startTime)
