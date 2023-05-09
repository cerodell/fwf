import context
import json
import bson
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
import string

from context import data_dir, xr_dir, wrf_dir, fwf_dir, tzone_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()


filein_obs = "/bluesky/fireweather/fwf/data/obs/cwfis_canusfwi2020s.csv"
obs_df = pd.read_csv(filein_obs, sep=",", skiprows=0)

test = obs_df.copy()

filein_obs = "/bluesky/fireweather/fwf/data/obs/cwfis_fwi2020sopEC.csv"
obs_df2 = pd.read_csv(filein_obs, sep=",", skiprows=0)

wrf_model = "wrf4"
domain = "d02"
### make folder for json files on webapge
forecast_date = pd.Timestamp("today").strftime("%Y%m%d")
make_dir = Path(f"/bluesky/archive/fireweather/forecasts/{forecast_date}00/data/plot")
make_dir.mkdir(parents=True, exist_ok=True)

## redefine forecast ate to get file with spin up
forecast_date = forecast_date + "06"


## Get Path to most recent FWI forecast and open
print(f"Starting to make jsons for {domain}")
loopTime = datetime.now()
hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-{domain}-{forecast_date}.nc")
hourly_ds = xr.open_dataset(hourly_file_dir)
