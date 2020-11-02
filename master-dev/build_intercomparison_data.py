#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
startTime = datetime.now()

from utils.make_csv import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir
from wrf import ll_to_xy, xy_to_ll

import warnings

warnings.filterwarnings("ignore", message="elementwise comparison failed")



"""######### get today/yesterday dates.  #############"""

current = date.today()
today = current - timedelta(days=1)
yesterday = today - timedelta(days=1)

##  Our machine is on an odd timezone so todays is yesterdays and yesterdays is two days ago....
### example curent = 20200725, today = 20200724, yesterday = 20200723
### Its confusing im sorry feel free to rename the varibles just know the date will all match up with the correct data.
todays_date = today.strftime('%Y%m%d')
yesterdays_date = yesterday.strftime('%Y%m%d')

todays_date = today.strftime('%Y%m%d')
yesterdays_date = yesterday.strftime('%Y%m%d')

intercomparison_make_csv(None, todays_date, yesterdays_date)