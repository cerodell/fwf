#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))


from make_csv_dev import intercomparison_make_csv
from context import data_dir, xr_dir, wrf_dir, root_dir
from wrf import ll_to_xy, xy_to_ll

import warnings

warnings.filterwarnings("ignore", message="elementwise comparison failed")



"""######### get today/yesterday dates.  #############"""
"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
start = datetime.strptime("20200831", "%Y%m%d")
end = datetime.strptime("20200919", "%Y%m%d")
todays_date_range = [start + timedelta(days=x) for x in range(0, (end-start).days)]

start = datetime.strptime("20200830", "%Y%m%d")
end = datetime.strptime("20200918", "%Y%m%d")
yesterdays_range = [start + timedelta(days=x) for x in range(0, (end-start).days)]

# df_list = []
for i in range(len(todays_date_range)):
    todays_date = todays_date_range[i].strftime("%Y%m%d")
    yesterdays_date = yesterdays_range[i].strftime("%Y%m%d")

    if int(todays_date) > 20200919:
        exit
    else:
        print(todays_date, "today")
        print(yesterdays_date, "yesterday")


    intercomparison_make_csv(None, todays_date, yesterdays_date)
    print("Run Time: ", datetime.now() - startTime)


# final_inter_df = pd.concat(df_list)
# final_inter_df.drop(final_inter_df.columns[-1],axis=1,inplace=True) 

# final_inter_df.to_csv(csv_dir_today, sep=',', encoding='utf-8', index=False)
# print(f"{str(datetime.now())} ---> wrote {csv_dir_today}" )


print("Total Run Time: ", datetime.now() - startTime)
