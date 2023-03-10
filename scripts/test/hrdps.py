#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import os
import sys
import time
import xarray as xr
import pandas as pd
from pathlib import Path
import wget


from context import wrf_dir, root_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()


date_range = pd.date_range("2021-07-01", "2021-12-30")
# date_range = pd.date_range("2021-01-01", "2021-07-01")
# date_range = pd.date_range("2022-01-01", "2022-12-31")

url = "https://collaboration.cmc.ec.gc.ca/cmc/arqi/jac001/for_ChrisR_UBC/HRDPSforFWI/20210101-20210131/"
save_dir = "/Volumes/WFRT-Ext24/ECCC/HRDPS/"
for date in date_range:
    for i in range(0, 49):
        date.strftime("%Y%m%d00")
        url_i = f'{url}{date.strftime("%Y%m%d00")}_{str(i).zfill(3)}.nc'
        save_dir_i = f'{save_dir}{date.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
        if os.path.isfile(save_dir_i) == True:
            try:
                xr.open_dataset(save_dir_i)
            except:
                print(f'Failed to open: {date.strftime("%Y%m%d00")}')
            # print('File Exists')
        else:
            try:
                wget.download(url_i, out=save_dir_i)
                print(f' -----> Wrote: {date.strftime("%Y%m%d00")}_{str(i).zfill(2)}')
            except:
                print(f'File does not exists on FTP: {date.strftime("%Y%m%d00")}')
