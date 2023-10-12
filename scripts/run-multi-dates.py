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
from utils.wrf_ import read_wrf
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
warnings.filterwarnings("ignore", category=UserWarning)
date_range = pd.date_range("2019-12-26", "2023-01-01")

config = dict(
    model="ecmwf",
    domain="era5",
    trail_name="02",
    initialize=False,
    initialize_hffmc=False,
    overwinter=False,
    fbp_mode=False,
    correctbias=False,
)

if config["model"] == "eccc":
    config["root_dir"] = "/Volumes/WFRT-Ext23/fwf-data"
elif config["model"] == "ecmwf":
    config["root_dir"] = "/Volumes/ThunderBay/CRodell/ecmwf/era5/"
elif config["model"] == "wrf":
    if int(date_range[0].strftime("%Y")) >= 2023:
        config["root_dir"] = "/Volumes/WFRT-Ext24/fwf-data"
    else:
        config["root_dir"] = "/Volumes/Scratch/fwf-data"
else:
    raise ValueError("YIKES! Sorry check your paths")


for date in date_range:
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
