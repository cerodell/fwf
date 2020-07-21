import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, date, timedelta
startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))
from dev_fwf import FWF
from context import data_dir, wrf_dir, tzone_dir, root_dir


"""######### get directory to yesterdays hourly/daily .zarr files.  #############"""
re_run = '/Volumes/cer/fireweather/data/'

start = datetime.strptime("2020053000", "%Y%m%d00")
end = datetime.strptime("2020072000", "%Y%m%d00")
solve_forecast_range = [start + timedelta(days=x) for x in range(0, (end-start).days)]

start = datetime.strptime("2020052900", "%Y%m%d00")
end = datetime.strptime("2020071900", "%Y%m%d00")
yesterdays_forecast_range = [start + timedelta(days=x) for x in range(0, (end-start).days)]

for i in range(len(solve_forecast_range)):
    solve_forecast = solve_forecast_range[i].strftime("%Y%m%d00")

    yesterdays_forecast = yesterdays_forecast_range[i].strftime("%Y%m%d00")
    if int(solve_forecast) > 2020071800:
        exit
    else:
        print(solve_forecast, "today")
        print(yesterdays_forecast, "yesterday")

        wrf_file_dir = str(re_run) + str(f"xr/fwf-hourly-{solve_forecast}.zarr") 
        hourly_file_dir = str(re_run) + str(f"new_xr/fwf-hourly-{yesterdays_forecast}.zarr")   #### SHOULD BE THE DAY BEFORE THE OTHERS!!!
        daily_file_dir = str(re_run) + str(f"xr/fwf-daily-{solve_forecast}.zarr") 
        print(wrf_file_dir)
        print(hourly_file_dir)

        coeff = FWF(wrf_file_dir, hourly_file_dir, daily_file_dir) 
        hourly_file_dir  = coeff.hourly()



"""######### Open wrf_out.nc and write  new hourly/daily .zarr files #############"""
# coeff = FWF(wrf_file_dir, None, daily_file_dir) 

# hourly_file_dir  = coeff.hourly()




### Timer
# print("Run Time: ", datetime.now() - startTime)

# testdate = '2020052900'
# wrf_file_dir = str(re_run) + str(f"xr/fwf-hourly-{testdate}.zarr") 
# hourly_file_dir = str(re_run) + str(f"new_xr/fwf-hourly-{testdate}.zarr")


# old_hourly_ds = xr.open_zarr(wrf_file_dir)
# new_hourly_ds = xr.open_zarr(hourly_file_dir)

# print(np.array(old_hourly_ds.Time[0], dtype ='datetime64[h]'), 'old time')
# print(np.array(new_hourly_ds.Time[0], dtype ='datetime64[h]'), 'new time')

# print(np.nanmax(old_hourly_ds.F[0]), 'old ffmc max')
# print(np.nanmax(new_hourly_ds.F[0]), 'new ffmc max ')

# print(np.nanmean(old_hourly_ds.F[0]), 'old ffmc mean')
# print(np.nanmean(new_hourly_ds.F[0]), 'new ffmc mean ')

# print(np.nanmin(old_hourly_ds.F[0]), 'old ffmc min')
# print(np.nanmin(new_hourly_ds.F[0]), 'new ffmc min ')


# print(np.nanmean(old_hourly_ds.T[10]), 'old temp mean')
# print(np.nanmean(new_hourly_ds.T[10]), 'new temp mean ')


