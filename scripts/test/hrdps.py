#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import os
import gc
import sys
import time
import xarray as xr
import pandas as pd
from pathlib import Path
import wget


from context import wrf_dir, root_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

model = "HRDPS"
date_range = pd.date_range("2021-01-01", "2021-04-01")
# start = date_range[0].strftime("%Y%m%d")
# stop = date_range[-1].strftime("%Y%m%d")

# url = f"https://collaboration.cmc.ec.gc.ca/cmc/arqi/jac001/for_ChrisR_UBC/{model}forFWI/{start}-{stop}/"
url = f"https://collaboration.cmc.ec.gc.ca/cmc/arqi/jac001/for_ChrisR_UBC/{model}forFWI/20211101-20211231/"
save_dir = f"/Volumes/WFRT-Ext24/ECCC/{model}/"
for date in date_range:
    for i in range(0, 49):
        date.strftime("%Y%m%d00")
        url_i = f'{url}{date.strftime("%Y%m%d00")}_{str(i).zfill(3)}.nc'
        save_dir_i = f'{save_dir}{date.strftime("%Y%m")}/{date.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
        if os.path.isfile(save_dir_i) == True:
            try:
                ds = xr.open_dataset(save_dir_i)
                del ds
                gc.collect()
            except:
                print(f'Failed to open: {date.strftime("%Y%m%d00")}')
            # print('File Exists')
        else:
            try:
                wget.download(url_i, out=save_dir_i)
                print(f' -----> Wrote: {date.strftime("%Y%m%d00")}_{str(i).zfill(2)}')
            except:
                print(f'File does not exists on FTP: {date.strftime("%Y%m%d00")}')

# rm -rf 202101*

# model = "HRDPS"
# date_range = pd.date_range("2019-04-04", "2019-10-01")

# url = f"https://collaboration.cmc.ec.gc.ca/cmc/arqi/jac001/for_ChrisR_UBC/HRDPS_FWI/2018season/"
# save_dir = f"/Volumes/WFRT-Ext24/ECCC/{model}/fwi/"
# init = ["00", "12"]
# valid = [["12","36"],["00", "24"]]

# for date in date_range:
#     for i in range(len(init)):
#         for j in valid[i]:
#             url_i = f'{url}{date.strftime("%Y%m%d")}{init[i]}_{str(j).zfill(3)}_lnoon_FWI.nc'
#             save_dir_i = f'{save_dir}{date.strftime("%Y%m%d")}{init[i]}_{str(j).zfill(3)}_lnoon_FWI.nc'
#             if os.path.isfile(save_dir_i) == True:
#                 try:
#                     xr.open_dataset(save_dir_i)
#                 except:
#                     print(f'Failed to open: {date.strftime("%Y%m%d00")}')
#                 # print('File Exists')
#             else:
#                 try:
#                     wget.download(url_i, out=save_dir_i)
#                     print(f' -----> Wrote: {date.strftime("%Y%m%d")}{init[i]}_{str(j).zfill(3)}')
#                 except:
#                     print(f'File does not exists on FTP: {date.strftime("%Y%m%d00")}')
