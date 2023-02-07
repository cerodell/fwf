#!/Users/crodell/miniconda3/envs/fwf/bin/python

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

from datetime import datetime, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF
from context import wrf_dir
import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

wrf_model = "wrf4"
date_range = pd.date_range("2022-02-16", "2022-11-01")
# date_range = pd.date_range("2021-01-01", "2021-01-10")
# date_range = pd.date_range("2021-01-01", "2021-01-01")

# date_range = pd.date_range("2020-01-10", "2022-10-31")
# date_range = pd.date_range("2020-01-02", "2020-01-10")
# date_range = pd.date_range("2020-01-01", "2020-01-01")


# """######### get directory to yesterdays hourly/daily .nc files.  #############"""
for date in date_range:

    domains = ["d02"]
    for domain in domains:
        domain_startTime = datetime.now()
        print(f"start of domain {domain}: ", str(domain_startTime))
        # """######### run era5  #############"""
        # print("######### run fwf era5  #############")
        # era_filein = f'/Volumes/WFRT-Data02/era5/era5-{date.strftime("%Y%m%d%H")}.nc'
        # era_filein = f'/Volumes/WFRT-Data02/era5/fwf/fwf-hourly-d02-{date.strftime("%Y%m%d%H")}.nc'

        # coeff = FWF(
        #     era_filein,
        #     domain,
        #     iterator="era5",
        #     fbp_mode=False,
        #     overwinter=True,
        #     initialize=False,
        #     correctbias=False,
        #     forecast=False,
        #     config="ERA505",
        # )
        # coeff.daily()
        # coeff.hourly()

        """######### run fwf day0  #############"""
        print("######### run fwf wrf  #############")
        fwf0_filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/{date.strftime("%Y%m")}/fwf-hourly-d02-{date.strftime("%Y%m%d06")}.nc'
        coeff = FWF(
            fwf0_filein,
            domain,
            iterator="fwf",
            fbp_mode=False,
            overwinter=True,
            initialize=False,
            correctbias=True,
            forecast=False,
            config="WRF08",
        )
        coeff.daily()
        # coeff.hourly()

        print(f"Domain {domain} run time: ", datetime.now() - domain_startTime)


### Timer
print("Total Run Time: ", datetime.now() - startTime)
