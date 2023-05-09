#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.read_wrfout import readwrf

# from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

filein = "/bluesky/archive/fireweather/forecasts/current/data/plot/"

with open(str(filein) + "/wf-xr-2021110406-d03.json") as f:
    blah = json.load(f)
