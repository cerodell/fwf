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
# date_range = pd.date_range("2021-01-02", "2021-01-02")
date_range = pd.date_range("2021-01-01", "2021-01-01")

# """######### get directory to yesterdays hourly/daily .nc files.  #############"""
for date in date_range:
    # forecast_date = date.strftime("%Y%m%d")
    # era_day5 = pd.to_datetime(str(date - np.timedelta64(5, "D")))
    # fwf_day4 = pd.to_datetime(str(date - np.timedelta64(4, "D")))
    # fwf_day3 = pd.to_datetime(str(date - np.timedelta64(3, "D")))
    # fwf_day2 = pd.to_datetime(str(date - np.timedelta64(2, "D")))
    # fwf_day1 = pd.to_datetime(str(date - np.timedelta64(1, "D")))
    fwf_day0 = date
    # era_day5 = date

    domains = ["d02"]
    for domain in domains:
        domain_startTime = datetime.now()
        print(f"start of domain {domain}: ", str(domain_startTime))
        # """######### run era5  #############"""
        # print("######### run era5  #############")
        # era_filein = (
        #     f'/Volumes/WFRT-Data02/era5/era5-{era_day5.strftime("%Y%m%d%H")}.nc'
        # )
        # coeff = FWF(
        #     era_filein,
        #     domain,
        #     iterator="era5",
        #     fbp_mode=False,
        #     initialize=True,
        #     forecast=False,
        #     config='ERA502'
        # )
        # coeff.daily()
        # coeff.hourly()

        # # """######### run fwf day4  #############"""
        # print("######### run fwf day4  #############")
        # fwf4_filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/{fwf_day4.strftime("%Y%m")}/fwf-hourly-d02-{fwf_day4.strftime("%Y%m%d06")}.nc'
        # coeff = FWF(
        #     fwf4_filein,
        #     domain,
        #     iterator="era5",
        #     fbp_mode=False,
        #     initialize=False,
        #     forecast=False,
        #     config='ERA5WRF03'
        # )
        # coeff.daily()
        # # # coeff.hourly()

        # # # """######### run fwf day3  #############"""
        # print("######### run fwf day3  #############")
        # fwf3_filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/{fwf_day3.strftime("%Y%m")}/fwf-hourly-d02-{fwf_day3.strftime("%Y%m%d06")}.nc'
        # coeff = FWF(
        #     fwf3_filein,
        #     domain,
        #     iterator="fwf",
        #     fbp_mode=False,
        #     initialize=False,
        #     forecast=False,
        #     config='ERA5WRF03'
        # )
        # coeff.daily()
        # # # coeff.hourly()

        # # # """######### run fwf day2  #############"""
        # print("######### run fwf day2  #############")
        # fwf2_filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/{fwf_day2.strftime("%Y%m")}/fwf-hourly-d02-{fwf_day2.strftime("%Y%m%d06")}.nc'
        # coeff = FWF(
        #     fwf2_filein,
        #     domain,
        #     iterator="fwf",
        #     fbp_mode=False,
        #     initialize=False,
        #     forecast=False,
        #     config='ERA5WRF03'
        # )
        # coeff.daily()
        # # # # coeff.hourly()

        # # """######### run fwf day1  #############"""
        # print("######### run fwf day1  #############")
        # fwf1_filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/{fwf_day1.strftime("%Y%m")}/fwf-hourly-d02-{fwf_day1.strftime("%Y%m%d06")}.nc'
        # coeff = FWF(
        #     fwf1_filein,
        #     domain,
        #     iterator="fwf",
        #     fbp_mode=False,
        #     initialize=False,
        #     forecast=False,
        #     config='ERA5WRF03'
        # )
        # coeff.daily()
        # # # coeff.hourly()

        # """######### run fwf day0  #############"""
        print("######### run fwf day0  #############")
        fwf0_filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/{fwf_day0.strftime("%Y%m")}/fwf-hourly-d02-{fwf_day0.strftime("%Y%m%d06")}.nc'
        coeff = FWF(
            fwf0_filein,
            domain,
            iterator="fwf",
            fbp_mode=False,
            initialize=True,
            forecast=False,
            config="WRF05",
        )
        coeff.daily()
        # coeff.hourly()

        print(f"Domain {domain} run time: ", datetime.now() - domain_startTime)


### Timer
print("Total Run Time: ", datetime.now() - startTime)
