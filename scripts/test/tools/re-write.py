#!/Users/crodell/miniconda3/envs/fwf/bin/python


import context
import numpy as np
import pandas as pd
import xarray as xr

from datetime import datetime, timedelta
from utils.era5 import rewrite_era5

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


#
date_range = pd.date_range("2019-12-27", "2019-12-27")

for date in date_range:
    ds = rewrite_era5(date, "ecmwf", "era5")
