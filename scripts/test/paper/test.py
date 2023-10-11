import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy import stats
from pathlib import Path
import plotly.express as px
import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable


from context import data_dir, root_dir


previous_daily_ds = xr.open_dataset(
    "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-daily-d02-2021011006.nc"
)


daily_ds = xr.open_dataset(
    "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-daily-d02-2021011106.nc"
)

hourly_ds = xr.open_dataset(
    "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-hourly-d02-2021011106.nc"
)
hourly_ds_old = xr.open_dataset(
    "/Volumes/WFRT-Ext24/fwf-data/wrf/d02/02/fwf-hourly-d02-2021011106-copy.nc"
)

BUI = previous_daily_ds["U"].isel(time=0)
try:
    BUI = BUI.drop(["time"])
except:
    pass

daily_ds_i = daily_ds["U"]
daily_ds_i = daily_ds_i.drop(["XTIME"])
daily_ds_i = xr.combine_nested([BUI, daily_ds_i], "time")
daily_ds_i["time"] = daily_ds_i["Time"] + np.timedelta64(18, "h")

# Convert daily data to hourly intervals
hourly_dates = hourly_ds.Time.values
daily_dsH = daily_ds_i.resample(time="1H").interpolate("linear")

# Extrapolate forward in time
daily_dsH = daily_dsH.reindex(time=hourly_dates)
# Forward fill the extrapolated values
U = daily_dsH.ffill(dim="time")
U = U.transpose("time", "south_north", "west_east")

# U.isel(south_north = 50, west_east = 100).plot()

S_interp = hourly_ds_old["S"].mean(dim=("south_north", "west_east"))
S_old = hourly_ds["S"].mean(dim=("south_north", "west_east"))

(S_interp - S_old).plot()

S_interp.plot()
S_old.plot()


S_interp = hourly_ds_old["S"].mean(dim=("time"))
S_old = hourly_ds["S"].mean(dim=("time"))

(S_interp - S_old).plot()
S_old.plot()


# f_D = xr.where(
#     U > 80,
#     1000 / (25 + 108.64 * np.exp(-0.023 * U)),
#     (0.626 * np.power(U, 0.809)) + 2,
# )
# f_D.isel(south_north = 50, west_east = 100).plot()

# U.isel(south_north = 50, west_east = 100).plot()

# hourly_ds.isel(south_north = 50, west_east = 100)['S'].plot()
# hourly_ds.isel(south_north = 50, west_east = 100)['R'].plot()
