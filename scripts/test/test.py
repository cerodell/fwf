import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
import string

from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

fwf_dir = '/Volumes/Scratch/FWF-WAN00CG/d02/202101/'

wrf_model = "wrf4"
domain = 'd02'
forecast_date = '2021010106'

loopTime = datetime.now()
hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-{domain}-{forecast_date}.nc")
hourly_ds = xr.open_dataset(hourly_file_dir)
