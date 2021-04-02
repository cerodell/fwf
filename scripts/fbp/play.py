import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


from context import data_dir, vol_dir, gog_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d02"
wrf_model = "wrf3"

hourly_ds = xr.open_zarr(
    Path(str(fwf_zarr_dir) + str("/fwf-hourly-") + domain + str(f"-2019040106.zarr"))
)
hourly_ds = hourly_ds.drop_vars("RH")
hourly_ds.to_zarr(
    str(fwf_zarr_dir) + str("/fwf-hourly-") + domain + str(f"-2019040106.zarr"),
    mode="w",
)


# daily_ds = xr.open_zarr(Path(
#     str(fwf_zarr_dir)
#     + str("/fwf-daily-")
#     + domain
#     + str(f"-2018040106.zarr")
# ))

# test = daily_ds.isel(time = 0)
# test.D.plot()
