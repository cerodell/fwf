#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import json
import salem
import os

import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from datetime import datetime, date, timedelta

from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


################## INPUTS ####################

domain = "d02"
temporal = "daily"
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"
date_range = pd.date_range("2021-01-01", "2023-08-15")
# date_range = pd.date_range('2023-05-09', '2023-05-12')

################## END INPUTS ####################

static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
if temporal == "daily":
    slicer = slice(0, 1)
else:
    slicer = slice(0, 24)
startTime = datetime.now()
for doi in date_range:
    fwi_i = xr.open_dataset(
        filein + f"fwf-{temporal}-{domain}-{doi.strftime('%Y%m%d06')}.nc"
    )[
        "S"
    ]  # .isel(time =slicer)
    fwi_i["south_north"] = static_ds["south_north"]
    fwi_i["west_east"] = static_ds["west_east"]
    fwi_max = fwi_i.max(dim="time").rename("S_max").expand_dims(dim={"t": [1]})
    fwi_min = fwi_i.min(dim="time").rename("S_min").expand_dims(dim={"t": [1]})
    # fwi_mean = xr.open_dataset(filein + f"fwf-hourly-{domain}-{doi.strftime('%Y%m%d06')}.nc")['S'].mean(dim = 'time').rename('S_mean').expand_dims(dim={"t": [1]})
    try:
        fwi_j_max = (
            xr.combine_nested([fwi_max, fwi_j_max], concat_dim="t")
            .max(dim="t")
            .expand_dims(dim={"t": [0]})
        )
        fwi_j_min = (
            xr.combine_nested([fwi_min, fwi_j_min], concat_dim="t")
            .min(dim="t")
            .expand_dims(dim={"t": [0]})
        )
    except:
        fwi_j_max = fwi_max.copy()
        fwi_j_max["t"] = [0]
        fwi_j_min = fwi_min.copy()
        fwi_j_min["t"] = [0]
    del fwi_max
    del fwi_min
    print(f"{doi.strftime('%Y%m%d06')}")


fwi = xr.merge([fwi_j_max, fwi_j_min]).isel(t=0)
fwi.attrs = static_ds.attrs
fwi["S_max"].attrs = static_ds.attrs
fwi["S_min"].attrs = static_ds.attrs

fwi.to_netcdf(str(data_dir) + f"/norm/fwi-{temporal}-{domain}.nc", mode="w")
print(f"Run time: ", datetime.now() - startTime)

daily_ds = salem.open_xr_dataset(str(data_dir) + f"/norm/fwi-{temporal}-{domain}.nc")
daily_ds["S_max"].salem.quick_map()
print(daily_ds)
