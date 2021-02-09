#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from bson import json_util
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from datetime import datetime, date, timedelta
from scipy.stats.stats import pearsonr

startTime = datetime.now()
from matplotlib.dates import DateFormatter

import seaborn as sns
import scipy.stats as stats
from utils.make_csv import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir


### Pandas hates me and throws out so many warnings......turn on warnings to find out :) 
import warnings
warnings.filterwarnings("ignore")

"""######### get directory to hourly/daily .zarr files.  #############"""
start_date_prearsons = date.today() - timedelta(days=61)

start_date_bias = date.today() - timedelta(days=16)
stop_date = date.today() - timedelta(days=1)

file_date = stop_date.strftime("%Y%m%d")
todays_date = date.today() 
todays_date = todays_date.strftime("%Y%m%d")



# print(f"{str(datetime.now())} ---> write fwf wxstation dictonary to json" )

# ### Write json file to defind dir 
# make_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(todays_date) + "00/data")
# make_dir.mkdir(parents=True, exist_ok=True)

# with open(str(make_dir) + f"/fwf-wxstation-{file_date}00.json","w") as f:
#     json.dump(wmo_r_1day,f, default=json_util.default, separators=(',', ':'), indent=None)

# print(f"{str(datetime.now())} ---> wrote json fwf wxstation to:  " + str(make_dir) + f"/fwf-wxstation-{file_date}.json")
