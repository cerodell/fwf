#!/Users/crodell/miniconda3/envs/fwx/bin/python

"""
Runs the FWF model for over user defined dates
"""

import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, timedelta


startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF


import warnings



__author__ = "Christopher Rodell"
__email__ = "crodell@tecnosylva.com"

# ignore RuntimeWarning
# warnings.filterwarnings("ignore", category=RuntimeWarning)
# warnings.filterwarnings("ignore", category=UserWarning)
# date_range = pd.date_range("2004-08-01", "2004-08-01")
# date_range = pd.date_range("2004-08-01", "2004-08-10")
# date_range = pd.date_range("2022-11-22", "2024-08-01")
date_range = pd.date_range("2022-11-15", "2024-08-01")

config = dict(
    model="wrf",
    domain="d03",
    company = "fa",
    initialize=False,
    initialize_hffmc=False,
    overwinter=False,
    # fbp_mode=True,
    # frp_mode=True,
    correctbias=False,
    reanalysis_mode=False,
    parallel=False,
    file_formate="netcdf",
    root_dir = "/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/"
)



for date in date_range:
    print("===================================================")
    date_startTime = datetime.now()
    config["doi"] = date
    coeff = FWF(
        config=config,
    )
    coeff.daily()
    coeff.hourly()
    print(f'{date.strftime("%Y%m%d")} run time: ', datetime.now() - date_startTime)

### Timer
print("Total Run Time: ", datetime.now() - startTime)
