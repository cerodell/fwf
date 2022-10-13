import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
import string
import salem
import os

from pathlib import Path


from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

fwf_dir = "/Volumes/WFRT-Data02/FWF-WAN00CG/d02/forecast"

wrf_model = "wrf4"
domain = "d02"
forecast_date = "2021010606"

date_range = pd.date_range("2021-04-25", "2022-06-01")

# """######### get directory to yesterdays hourly/daily .nc files.  #############"""
# for date in date_range:
#     filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/'
#     file_doi = filein + f'{date.strftime("%Y%m")}/fwf-hourly-d02-{date.strftime("%Y%m%d06")}.nc'

#     my_file = Path(file_doi)
#     if my_file.is_file():
#       pass
#     else:
#       day1 = pd.to_datetime(str(date - np.timedelta64(1, "D")))
#       print(f'No file on {date.strftime("%Y%m%d06")}')
#       file_doi_y = filein + f'{day1.strftime("%Y%m")}/fwf-hourly-d02-{day1.strftime("%Y%m%d06")}.nc'
#       command = f'cp -r {file_doi_y}  {file_doi}'
#       os.system(command)

#         # file exists


# loopTime = datetime.now()
# hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-{domain}-{forecast_date}.nc")
# ds = xr.open_dataset(hourly_file_dir)

# print(np.unique(ds.isel(time = 0).F.isnull(), return_counts = True))
# # print(np.unique(ds.isel(time = 0).P.isnull(), return_counts = True))
# # print(np.unique(ds.isel(time = 0).D.isnull(), return_counts = True))
# print(np.unique(ds.isel(time = 0).R.isnull(), return_counts = True))
# # print(np.unique(ds.isel(time = 0).U.isnull(), return_counts = True))
# print(np.unique(ds.isel(time = 0).S.isnull(), return_counts = True))


# era5_ds = salem.open_xr_dataset(f'/Volumes/WFRT-Data02/era5/era5-{forecast_date[:-2]}00.nc')
# era5_ds['T'] = era5_ds.t2m-273.15
# era5_ds['TD'] = era5_ds.d2m-273.15
# era5_ds['r_o_hourly'] = era5_ds.tp*1000
# # era5_ds['r_o_hourly'] = xr.where(era5_ds['r_o_hourly'] < 0, 0, era5_ds['r_o_hourly'])

# # era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["u10"], era5_ds["v10"]))
# era5_ds["SNOWH"] = era5_ds["sd"]
# era5_ds["U10"] = era5_ds["u10"]
# era5_ds["V10"] = era5_ds["v10"]

# keep_vars = [
#   "SNOWC",
#   "SNOWH",
#   "SNW",
#   "T",
#   "TD",
#   "U10",
#   "V10",
#   "W",
#   "WD",
#   "r_o",
#   "H",
# ]
# era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])
