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

date_range = pd.date_range("2025-03-08", "2025-03-26")
# date_range = pd.date_range("2025-03-05", "2025-03-05")

config = dict(
    model="wrf",
    domain="d03",
    company = "fa",
    initialize=False,
    initialize_hffmc=False,
    overwinter=False,
    fbp_mode=False,
    file_formate="netcdf",
    nwp_dir = "/NASPANGEA/WRF/Fortis_Alberta_forecast/",       ## "/NASPANGEA/WRF/Fortis_Alberta_forecast/"  or "/NASPANGEA/WRF/BCWS_forecast/"
    # save_dir = "/path_to/save/fwf/" ## if not defined a folder is created nwp_dir/cffdrs
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
