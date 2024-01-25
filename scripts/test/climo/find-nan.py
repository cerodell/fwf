#!/Users/crodell/miniconda3/envs/fwx/bin/python

import os
import json
import context
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import flox
import flox.xarray

from utils.compressor import compressor
from utils.climatology import get_daily_files, hour_qunt, concat_ds, slice_ds
from context import root_dir


# from dask.distributed import LocalCluster, Client

# cluster = LocalCluster(
#     n_workers=2,
#     #    threads_per_worker=,
#     memory_limit="7GB",
#     processes=False,
# )
# client = Client(cluster)
# client = Client(processes=False)
## On workstation
# http://137.82.23.185:8787/status
## On personal
#  http://10.0.0.88:8787/status
# print(client)

date_range = pd.date_range("1990-01-01", "2021-01-01")

timeT = datetime.now()

list_statement = []
for date in date_range:
    print("-----------------------------------------------")
    doi = date.strftime("%Y%m%d%H")
    print(doi)
    # statment = np.any(np.isnan(xr.open_dataset(f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi}.nc")['S'].values))
    statment = np.any(
        xr.open_dataset(
            f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi}.nc"
        )["S"].values
        < 0
    )

    # print(statment) np.any(
    if statment == False:
        pass
    else:
        raise ValueError(date.strftime("%Y%m%d%H") + "has nan values for fwi")
    # print(np.any(np.isnan(xr.open_dataset(f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{date.strftime('%Y%m%d%H')}.nc")['S'])))
    # print(dask.array.unique(dask.array.isnan(xr.open_dataset(f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{date.strftime('%Y%m%d%H')}.nc")['S'].to_dask_array()), return_counts=True))

# np.savetxt('/Users/crodell/fwf/output.txt', list_statement)
print("Run time : ", datetime.now() - timeT)
