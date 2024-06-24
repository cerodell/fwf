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
# date_range = pd.date_range("2023-05-13", "2023-05-18")
# date_range = pd.date_range("2023-05-15", "2023-05-15")
date_range = pd.date_range("2006-01-06", "2007-01-01")
# date_range = pd.date_range("2018-01-02", "2019-07-01")

config = dict(
    model="adda",
    domain="d01",
    trail_name="01",
    initialize=False,
    initialize_hffmc=True,
    overwinter=False,
    # fbp_mode=True,
    # frp_mode=True,
    correctbias=False,
    reanalysis_mode=False,
    parallel=False,
    file_formate="zarr",
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
elif config["model"] == "adda":
    config["root_dir"] = "/Volumes/WFRT-Ext20/ADDA_V2/"
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
