import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from fwi.utils.wrf.read_wrfout import readwrf
from fwi.utils.ubc_fwi.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir
import timezonefinder, pytz
from datetime import datetime
from pathlib import Path

filein = "/2019-08-19T00_ds_wrf.zarr"
ds_wrf_file = str(data_dir) + filein
ds_wrf = xr.open_zarr(ds_wrf_file)
#  ds_wrf.Time.astype('datetime64[D]')

test = ds_wrf.Time[15]

day_time    = np.datetime_as_string(ds_wrf.Time, unit='h')
day         = day_time.astype('datetime64[s]').tolist()
day_of_year = np.array([int(day[i].strftime('%j')) for i in range(len(day))])

hour = np.array([int(day_time[i][-2:]) for i in range(len(day_time))])

y = (2 * np.pi / 365) * (day_of_year - 1 + ((hour - 12)/24))

eqtime = 229.18 * (0.000075 + 0.001868 * np.cos(y) 
        - 0.032077*np.sin(y) - 0.0114615 * np.cos(2 * y) - 0.040849 * np.sin(2 * y))

snoon = [720 - 4* np.array(ds_wrf.XLONG) - eqtime[i] for i in range(len(eqtime))]

noon = snoon[0]