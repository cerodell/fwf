#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from context import root_dir, data_dir


# viirs_ds = xr.open_dataset('/Volumes/WFRT-Ext23/satilite/viirs/VNP13A2.001_1km_aid0001.nc')

ndvi_ds = salem.open_xr_dataset(
    "/Volumes/WFRT-Ext23/satilite/viirs/2022/VNP13A2.001_1km_aid0001.nc"
)
lai_ds = salem.open_xr_dataset(
    "/Volumes/WFRT-Ext23/satilite/viirs/2022/VNP15A2H.001_500m_aid0001.nc"
)


ndvi_ds.isel(time=2)["_1_km_16_days_NDVI"].salem.quick_map()

lai_ds.isel(time=1)["Lai"].salem.quick_map()
