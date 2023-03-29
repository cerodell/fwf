#!/Users/crodell/miniconda3/envs/fwf/bin/python

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
from utils.wrf import read_wrf
from utils.eccc import read_eccc
from utils.era5 import read_era5

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF


import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

date_range = pd.date_range("2021-01-02", "2021-01-10")
# date_range = pd.date_range("2021-01-01", "2021-01-01")
# date_range = pd.date_range("2020-01-01", "2020-01-01")

config = dict(
    model="eccc",
    domain="rdps",
    iterator="fwf",
    trail_name="04",
    fbp_mode=False,
    overwinter=True,
    initialize=False,
    correctbias=False,
    forecast=False,
    root_dir="/Volumes/WFRT-Ext23/fwf-data",
)


for date in date_range:
    date_startTime = datetime.now()
    coeff = FWF(
        # int_ds=read_wrf(f'{config["root_dir"]}/{config["model"]}/{config["domain"]}/{date.strftime("%Y%m")}/fwf-hourly-{config["domain"]}-{date.strftime("%Y%m%d06")}.nc',config["domain"]),
        int_ds=read_eccc(date, config["model"], config["domain"]),
        # int_ds=read_era5(date,config["model"],config["domain"]),
        config=config,
    )
    coeff.daily()
    # coeff.hourly()
    print(
        f'Domain {date.strftime("%Y%m%d0")} run time: ', datetime.now() - date_startTime
    )

### Timer
print("Total Run Time: ", datetime.now() - startTime)
