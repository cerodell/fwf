#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Test to run the FWF model
"""

import context
import os
import sys
import time
import pandas as pd
from pathlib import Path

from context import wrf_dir, root_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

domain = "d03"
avg_wrf = 61
min_wrf = 31
wait_max = 3  ## wait a max of hours then give up
wait_max = wait_max * 60  ## convert hours to mins


forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
filein = str(wrf_dir) + f"/{forecast_date}/"
lenght = len(sorted(Path(filein).glob(f"wrfout_{domain}_*00")))
command = f"{root_dir}/bin/all_fwf_run.sh"


if lenght >= avg_wrf:
    print(f"WRf Folder lenght of {lenght} mathces excepted lenght of {avg_wrf}")
    print(f"Running: {command}")
    os.system(command)
else:
    elapsed = 0
    while lenght < avg_wrf:
        print(f"slepping....WRf Folder lenght: {lenght}")
        time.sleep(60)
        elapsed += 1
        lenght = len(sorted(Path(filein).glob(f"wrfout_{domain}_*00")))
        if lenght >= avg_wrf:
            print(f"WRf Folder lenght of {lenght} mathces excepted lenght of {avg_wrf}")
            print(f"Running: {command}")
            os.system(command)
        elif elapsed >= wait_max:
            if lenght >= min_wrf:
                print(
                    f"WRf Folder lenght of {lenght} mathces minimum needed number of files to run FWF"
                )
                print(f"Running: {command}")
                os.system(command)
                sys.exit(0)
            else:
                print(
                    f"Quitting trying to run FWF...WRF folder lenght of {lenght} is not eneough"
                )
                sys.exit(0)
        else:
            pass
