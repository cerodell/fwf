#!/Users/crodell/miniconda3/envs/fwf/bin/python


import context
import gc
import numpy as np
import pandas as pd
import xarray as xr

from datetime import datetime, timedelta
from utils.eccc import read_eccc

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF


import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)
# date_range = pd.date_range("2021-04-20", "2022-11-01")
date_range = pd.date_range("2022-04-05", "2023-01-01")

# date_range = pd.date_range("2021-01-05", "2021-01-05")

config = dict(
    model="eccc",
    domain="hrdps",
    iterator="fwf",
    trail_name="04",
    fbp_mode=False,
    overwinter=True,
    initialize=True,
    correctbias=False,
    forecast=False,
    root_dir="/Volumes/Scratch/fwf-data/",
)


def compressor(ds):
    """
    this function compresses datasets
    """
    # ds = ds.load()
    for var in ds.data_vars:
        ds[var] = ds[var].astype(dtype="float32")
    comp = dict(zlib=True, complevel=2)
    encoding = {var: comp for var in ds.data_vars}
    # for var in ds.data_vars:
    #     ds[var].attrs = var_dict[var]

    return ds, encoding


for date in date_range:
    int_ds = read_eccc(date, config["model"], config["domain"])
    # int_ds=int_ds.chunks('auto')
    writeTime = datetime.now()
    # int_ds.to_netcdf(f'/Volumes/WFRT-Ext23/fwf-data/{config["model"]}/{config["domain"]}/fwf-hourly-{config["domain"]}-{date.strftime("%Y%m%d00")}.nc', mode ='w')
    int_ds, encoding = compressor(int_ds)
    int_ds.to_netcdf(
        f'/Volumes/WFRT-Ext23/fwf-data/{config["model"]}/{config["domain"]}/fwf-hourly-{config["domain"]}-{date.strftime("%Y%m%d00")}.nc',
        encoding=encoding,
        mode="w",
    )
    del int_ds
    gc.collect()
    print(
        f'Write Time for fwf-hourly-{config["domain"]}-{date.strftime("%Y%m%d00")}.nc: {datetime.now() - writeTime}'
    )
