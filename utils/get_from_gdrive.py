#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python
import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


wrf_model = "WAN00CP-04"

zarr_dir = f"/Users/rodell/Google Drive/My Drive/{wrf_model}/"
save_dir = f"/Volumes/cer/fireweather/data/{wrf_model}/"


date_range = pd.date_range("2018-08-06", "2018-08-15")


for domain in ["d03"]:
    for date in date_range:
        startTime = datetime.now()
        zarr_date = date.strftime("%Y%m%d06")
        zarr_file = f"wrfout-{domain}-{zarr_date}.zarr"
        print(zarr_file)
        zarr_file_dir = str(zarr_dir) + zarr_file
        ds = xr.open_zarr(zarr_file_dir)
        ds.to_zarr(save_dir + zarr_file, mode="w")
        print("File Run Time: ", datetime.now() - startTime)
