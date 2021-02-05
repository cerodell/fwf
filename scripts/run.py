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

from dev_utils.fwf import FWF
from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir, wrf_dir_new, nc_dir
import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore warnings by message
warnings.filterwarnings("ignore", message="invalid value encountered in power")
warnings.filterwarnings("ignore", message="invalid value encountered in log")

date_range = pd.date_range("2021-01-28", "2021-02-02")

"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
for date in date_range:
    yesterdays_date = date - np.timedelta64(1, "D")
    yesterdays_date = yesterdays_date.strftime("%Y%m%d06")
    forecast_date = date.strftime("%Y%m%d06")
    domains = ["d02", "d03"]
    for domain in domains:
        domain_startTime = datetime.now()
        print(f"start of domain {domain}: ", str(domain_startTime))

        hourly_file_dir = str(data_dir) + str(
            f"/FWF-WAN00CG-01/fwf-hourly-{yesterdays_date}-{domain}.zarr"
        )
        daily_file_dir = str(data_dir) + str(
            f"/FWF-WAN00CG-01/fwf-daily-{yesterdays_date}-{domain}.zarr"
        )

        """######### get directory to todays wrf_out .nc files.  #############"""
        # wrf_filein = date.today().strftime('/%y%m%d00/')
        # wrf_filein = f'/21010{i}00/'
        # print(wrf_filein)
        wrf_dir_new = "/Users/rodell/Desktop/WAN00CG-01"

        wrf_file_dir = str(wrf_dir_new) + f"/wrfout-{domain}-{forecast_date}.zarr"
        print(wrf_file_dir)

        """######### Open wrf_out.nc and write  new hourly/daily .zarr files #############"""
        coeff = FWF(wrf_file_dir, hourly_file_dir, daily_file_dir, domain)

        daily_file_dir = coeff.daily()
        hourly_file_dir = coeff.hourly()

        print(f"Domain {domain} run time: ", datetime.now() - domain_startTime)
        """######### Open daily_ds #############"""
        # daily_ds = xr.open_zarr(daily_file_dir)
        # print(daily_ds)
        # print(np.nanmin(np.array(daily_ds.D)), "D final min")
        # print(np.nanmax(np.array(daily_ds.D)), "D final max")

        """######### Open hourly_ds #############"""
        # hourly_ds = xr.open_zarr(hourly_file_dir)
        # print(hourly_ds)
        # print(hourly_ds.F)
        # print((hourly_ds.R))
        # print(np.nanmax(np.array(hourly_ds.S)))

    ### Timer
    print("Total Run Time: ", datetime.now() - startTime)
