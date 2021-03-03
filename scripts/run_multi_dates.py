#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Runs the FWF model for each model domain.
Saves dataset as zarr file contains all fwi and associated met products

"""
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF
from context import wrf_dir
import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore warnings by message
warnings.filterwarnings("ignore", message="invalid value encountered in power")
warnings.filterwarnings("ignore", message="invalid value encountered in log")
warnings.filterwarnings("ignore", message="divide by zero encountered in log")
wrf_model = "wrf3"
date_range = pd.date_range("2018-09-08", "2018-10-01")

# """######### get directory to yesterdays hourly/daily .zarr files.  #############"""
for date in date_range:
    forecast_date = date.strftime("%Y%m%d00")
    domains = ["d03"]
    for domain in domains:
        domain_startTime = datetime.now()
        print(f"start of domain {domain}: ", str(domain_startTime))
        # """######### get directory to todays wrf_out .nc files.  #############"""

        # wrf_file_dir = str(wrf_dir) + f"/{forecast_date}/"
        wrf_file_dir = str(wrf_dir) + f"/wrfout-{domain}-{forecast_date[:-2]}06.zarr"
        print(wrf_file_dir)

        # """######### Open wrf_out.nc and write  new hourly/daily .zarr files #############"""
        coeff = FWF(wrf_file_dir, domain, wrf_model, initialize=False)

        coeff.daily()
        coeff.hourly()

        print(f"Domain {domain} run time: ", datetime.now() - domain_startTime)

    ### Timer
    print("Total Run Time: ", datetime.now() - startTime)
