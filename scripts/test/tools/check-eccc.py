#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import os
import sys
import time
import xarray as xr
import pandas as pd
from pathlib import Path
import wget
import gc


from context import data_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

model = "eccc"
domain = "hrdps"

date_range = pd.date_range(f"2021-01-01", f"2023-01-01")


save_dir = f"/Volumes/WFRT-Ext24/{model}/{domain}/"
bad_nc, good_nc = [], []

for date in date_range:
    for i in range(0, 49):
        date.strftime("%Y%m%d00")
        save_dir_i = f'{save_dir}{date.strftime("%Y%m")}/{date.strftime("%Y%m%d00")}_{str(i).zfill(2)}.nc'
        if os.path.isfile(save_dir_i) == True:
            try:
                ds = xr.open_dataset(save_dir_i)
                var_list = list(ds)
                if len(var_list) <= 7:
                    bad_nc.append(f'{date.strftime("%Y%m%d00")}_{str(i).zfill(2)}')
                    good_nc.append(-99)
                elif 8 <= len(var_list) <= 11:
                    good_nc.append(f'{date.strftime("%Y%m%d00")}_{str(i).zfill(2)}')
                    bad_nc.append(-99)
                else:
                    raise ValueError(f"Unknown variable list length {list(ds)}")
                del ds
                gc.collect()
            except:
                print(
                    f'Data Failed to open: {date.strftime("%Y%m%d00")}_{str(i).zfill(2)}'
                )
                raise ValueError(f"Unknown variable list length {list(ds)}")
            # print('File Exists')
        else:
            bad_nc.append(f'{date.strftime("%Y%m%d00")}_{str(i).zfill(2)}')
            good_nc.append(-99)
            print(f'Data Does not Exist: {date.strftime("%Y%m%d00")}')

d = {"bad_nc": bad_nc, "good_nc": good_nc}
df = pd.DataFrame(data=d)
df.to_csv(str(data_dir) + f"/{model}/{domain}/check.csv")
