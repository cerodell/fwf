import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from utils.make_intercomp import make_daily_noon

from context import data_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


domain = "d02"
wrf_model = "wrf3"

startdate = pd.Timestamp("2019-04-01")
enddate = pd.Timestamp("2019-10-01")


# date_range = pd.date_range("2019-04-01", "2019-10-01")
# index_start = np.where(date_range==startdate)
# index_end = np.where(date_range==enddate)

pathlist = sorted(Path(fwf_zarr_dir).glob(f"fwf-hourly-{domain}-*"))
# date_range = pd.date_range(str(pathlist[0])[-15:-7], str(pathlist[-1])[-15:-7])
# index_start = np.where(date_range==startdate)
# index_end = np.where(date_range==enddate)


# pathlist = pathlist[int(index_start[0]):int(index_end[0])+1]

pathlist = pathlist[185:]
startdate = startdate.strftime("%Y%m%d00")
enddate = enddate.strftime("%Y%m%d00")


def read_zarr(f):
    ds = xr.open_zarr(f)
    ds = ds.isel(time=slice(0, 24))
    return ds


ds = xr.concat([read_zarr(f) for f in pathlist], dim="time")
ds = ds.chunk(chunks="auto")
ds = ds.unify_chunks()
for var in list(ds):
    ds[var].encoding = {}

# var_list = ['CFB', 'FMC', 'HFI', 'ROS', 'SFC', 'TFC', 'ISI', 'R', 'F']
# ds_short = ds.drop_vars([i for i in list(ds) if i not in var_list])
ds_short = make_daily_noon(ds, domain, wrf_model)


save_file = (
    f"/Volumes/cer/fireweather/data/fwf-daily-{domain}-{startdate}-{enddate}.zarr"
)
ds_short.to_zarr(save_file, mode="w")

print("Total Run Time: ", datetime.now() - startTime)
