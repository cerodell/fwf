import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import scipy.stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter
from pylab import *
import salem

from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText
import matplotlib
from pathlib import Path
from utils.fwi import (
    solve_ffmc,
    solve_dmc,
    solve_dc,
    solve_isi,
    solve_bui,
    solve_fwi,
)

matplotlib.rcParams.update({"font.size": 14})

import warnings

warnings.filterwarnings("ignore")

warnings.filterwarnings("ignore", category=FutureWarning)


"""

BAD KRIGED TEMP file on 2021-02-24, fix and rerun all of WRF07

"""

wrf_model = "wrf4"
domain = "d02"
# time_slice = slice("2021-02-26", "2021-10-31")

model_config = ["_wrf05", "_wrf06", "_wrf07"]
trail_name = "WRF050607"
nc_file = "20210101-20221031.nc"


with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)


ds = xr.open_dataset(str(data_dir) + f"/intercomp/d02/{trail_name}/{nc_file}")

try:
    ds = ds.sel(time=time_slice)
except:
    pass

ds = ds.load()


# ds['dc_wrf07'].mean(dim = 'wmo').plot()

doi = ds["temp_wrf07"].mean(dim="wmo").idxmin().values

doi_krig = pd.to_datetime(str(doi - np.timedelta64(1, "D"))).strftime("%Y%m%d")
doi = pd.to_datetime(str(doi)).strftime("%Y%m%d")

ds_krig = salem.open_xr_dataset(
    f"/Volumes/WFRT-Data02/FWF-WAN00CG/d02/krig-bias/fwf-krig-d02-{doi_krig}.nc"
)

ds_krig.T_bias.salem.quick_map()


ds_fwf = salem.open_xr_dataset(
    f"/Volumes/WFRT-Data02/FWF-WAN00CG/d02/WRF07/fwf/fwf-daily-d02-{doi}06.nc"
)


# ds_fwf['T'] = ds_fwf['T'] + ds_krig.T_bias.values
# ds_fwf['T'].attrs['pyproj_srs'] = ds_fwf['TD'].attrs['pyproj_srs']

ds_fwf.isel(time=0).T.salem.quick_map()


if (np.max(ds_fwf.T) > 100) | (np.min(ds_fwf.T) < -100):
    raise ValueError("ERROR: nonphysical T values")


# filein = "/Volumes/Scratch/FWF-WAN00CG/d02/202205/fwf-hourly-d02-2022051006.nc"
# # filein = "/Users/crodell/fwf/fwf-hourly-d02-2022051706.nc"
# ds = xr.open_dataset(filein)
# ds.Time.values[0]
# int_ds = ds.isel(time = slice(24,50))
# int_ds["Time"] = int_ds.Time + np.timedelta64(1, "D")
# print(int_ds.Time.values[0])

# int_ds.to_netcdf("/Volumes/Scratch/FWF-WAN00CG/d02/202205/fwf-hourly-d02-2022051006.nc", mode="w")

# cp -r /Users/crodell/fwf/fwf-hourly-d02-2022051806.nc /Volumes/Scratch/FWF-WAN00CG/d02/202205/

# date_range = pd.date_range("2021-01-01", "2022-08-01")
# """######### get directory to yesterdays hourly/daily .nc files.  #############"""
# for date in date_range:
#     #     filein = f'/Volumes/Scratch/FWF-WAN00CG/{domain}/'
#     #     file_doi = filein + f'{date.strftime("%Y%m")}/fwf-hourly-d02-{date.strftime("%Y%m%d06")}.nc'
#     file_doi = f'/Volumes/WFRT-Data02/FWF-WAN00CG/d02/forecast/fwf-daily-d02-{date.strftime("%Y%m%d06")}.nc'

#     my_file = Path(file_doi)
#     if my_file.is_file():
#         pass
#     else:
#         pass
#         day1 = pd.to_datetime(str(date - np.timedelta64(1, "D")))
#         print(f'No file on {date.strftime("%Y%m%d06")}')
#       file_doi_y = filein + f'{day1.strftime("%Y%m")}/fwf-daily-d02-{day1.strftime("%Y%m%d06")}.nc'
#       command = f'cp -r {file_doi_y}  {file_doi}'
#       os.system(command)


# # loopTime = datetime.now()
# hourly_file_dir = str(fwf_dir) + str(f"/fwf-daily-{domain}-{forecast_date}.nc")
# ds = xr.open_dataset(hourly_file_dir)

# print(np.unique(ds.isel(time = 0).F.isnull(), return_counts = True))
# print(np.unique(ds.isel(time = 0).P.isnull(), return_counts = True))
# print(np.unique(ds.isel(time = 0).D.isnull(), return_counts = True))
# print(np.unique(ds.isel(time = 0).R.isnull(), return_counts = True))
# print(np.unique(ds.isel(time = 0).U.isnull(), return_counts = True))
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
