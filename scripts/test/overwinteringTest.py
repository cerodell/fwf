import context
import os
import math
import json
import numpy as np
import pandas as pd
import xarray as xr


from pathlib import Path
from datetime import datetime
from utils.read_wrfout import readwrf
from utils.era5 import config_era5
from utils.compressor import compressor, file_size
from context import data_dir

# import h5py

doi = "2021011606"
timestep = "daily"
domain = "d02"
iterator_dir = "/Volumes/WFRT-Data02/FWF-WAN00CG/d02/WRF05/fwf"


ds = xr.open_dataset(str(iterator_dir) + f"/fwf-{timestep}-{domain}-{doi}.nc").chunk(
    "auto"
)


time_array = ds.Time.values
if timestep == "daily":
    tslice = 0
elif timestep == "hourly":
    tslice = slice(0, 24)
else:
    raise ValueError(
        f"Invalide timesept option of {timestep}, can only take daily or hourly"
    )

previous_dss, days_of_max = [], []
for i in range(4, -1, -1):
    retrieve_time_np = time_array[0] - np.timedelta64(i, "D")
    retrieve_time = pd.to_datetime(retrieve_time_np).strftime("%Y%m%d06")
    int_file_dir = str(iterator_dir) + f"/fwf-{timestep}-{domain}-{retrieve_time}.nc"
    try:
        # if i == 0:
        #     da = xr.open_dataset(int_file_dir).chunk("auto")
        # else:
        da = xr.open_dataset(int_file_dir).isel(time=tslice).chunk("auto")
        # da = xr.open_dataset(int_file_dir).isel(time = tslice).chunk('auto').SNOWC.mean(dim = 'time')
        previous_dss.append(da)
        days_of_max.append(retrieve_time_np.astype("datetime64[D]"))
    except:
        pass


cont_ds = xr.concat(previous_dss, dim="time").load()


cont_ds.isel(south_north=10, west_east=250).FS.plot()

cont_ds.isel(south_north=10, west_east=250).D.plot()

cont_ds.isel(south_north=250, west_east=200).FS.plot()

cont_ds.isel(south_north=250, west_east=200).D.plot()
