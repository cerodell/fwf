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
# date_range = pd.date_range("1990-01-01", "1990-01-01")
date_range = pd.date_range("2023-10-30", "2024-01-01")

config = dict(
    model="ecmwf",
    domain="era5-land",
    trail_name="04",
    initialize=False,
    initialize_hffmc=False,
    overwinter=False,
    fbp_mode=False,
    correctbias=False,
)

if config["model"] == "eccc":
    config["root_dir"] = "/Volumes/WFRT-Ext23/fwf-data"
elif config["model"] == "ecmwf":
    if config["domain"] == "era5":
        config["root_dir"] = "/Volumes/ThunderBay/CRodell/ecmwf/era5/"
    elif config["domain"] == "era5-land":
        config["root_dir"] = "/Volumes/WFRT-Ext25/ecmwf/era5-land/"
elif config["model"] == "wrf":
    if int(date_range[0].strftime("%Y")) >= 2023:
        config["root_dir"] = "/Volumes/WFRT-Ext23/fwf-data"
    else:
        config["root_dir"] = "/Volumes/Scratch/fwf-data"
else:
    raise ValueError(
        "YIKES! Sorry this model is not supported yet, you'll need to run /tools/build-static-ds.py"
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
