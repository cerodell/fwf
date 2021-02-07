import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from context import data_dir, xr_dir, wrf_dir, root_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


wrf_in = "/Users/rodell/Google Drive/My Drive/WAN00CG-01/wrfout-d03-2021020206.zarr"

wrf_ds = xr.open_zarr(wrf_in)
domain = "d03"
int_time = wrf_ds.Time.values
for i in range(1, 2):
    print(i)
retrive_time = pd.to_datetime(str(int_time[0] - np.timedelta64(1, "D")))
retrive_time = retrive_time.strftime("%Y%m%d%H")
hourly_file_dir = str(fwf_zarr_dir) + f"/fwf-hourly-{retrive_time}-{domain}.zarr"


retrive_time = pd.to_datetime(str(int_time[0] - np.timedelta64(1, "D"))).strftime(
    "%Y%m%d%H"
)


# finished = False
# while not finished:
#   for i in range(1,3):
#     retrive_time =  pd.to_datetime(str(int_time[0] - np.timedelta64(i,'D'))).strftime("%Y%m%d%H")
#     hourly_file_dir = str(fwf_zarr_dir) + f'/fwf-hourly-{retrive_time}-{domain}.zarr'
#     finished = Path(hourly_file_dir).exists()
#     print(i)


# retrive_time =  pd.to_datetime(str(int_time[0] - np.timedelta64(i,'D'))).strftime("%Y%m%d%H")
# hourly_file_dir = str(fwf_zarr_dir) + f'/fwf-hourly-{retrive_time}-{domain}.zarr'
# finished = Path(hourly_file_dir).exists()
# if finished == False:
#   try:
#     retrive_time =  pd.to_datetime(str(int_time[0] - np.timedelta64(i,'D'))).strftime("%Y%m%d%H")
#     hourly_file_dir = str(fwf_zarr_dir) + f'/fwf-hourly-{retrive_time}-{domain}.zarr'
