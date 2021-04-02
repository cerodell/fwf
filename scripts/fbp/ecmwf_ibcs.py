import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from wrf import ll_to_xy, xy_to_ll

from pylab import *
import matplotlib.pyplot as plt

from context import data_dir, vol_dir, gog_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


domain = "d02"
wrf_model = "wrf3"

### Get a wrf file
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"

wrf_ds = salem.open_xr_dataset(wrf_filein)

ds = xr.open_dataset(str(vol_dir) + f"/ecmwf/ffmc.nc")
ds.attrs["history"] = ""

date_of_int = "2019-03-31"


def getdate(var, date_of_int, int_value, new_var):
    ds = xr.open_dataset(str(vol_dir) + f"/ecmwf/{var}.nc")
    ds.attrs["history"] = ""
    ds_day = ds.sel(time=date_of_int)
    ds_day = wrf_ds.salem.transform(ds_day, interp="spline")
    ds_day = xr.where(np.isnan(ds_day[var]), int_value, ds_day[var])
    ds_day = ds_day.rename(new_var)
    # del ds_day[var]
    return ds_day


ffmc = getdate("ffmc", date_of_int, 85, "F")
m_o = (147.27723 * (101 - ffmc)) / (59.5 + ffmc)  ## Van 1985

ffmc = np.stack([ffmc, ffmc])
m_o = np.stack([m_o, m_o])

df = pd.DataFrame(
    {"Hours": pd.date_range("2019-04-01", "2019-04-02", freq="1H", closed="left")}
)
date_range = df.Hours.values[5:7]
ffmc = xr.DataArray(
    ffmc,
    name="F",
    coords={"time": date_range},
    dims=("time", "south_north", "west_east"),
)
m_o = xr.DataArray(
    m_o,
    name="m_o",
    coords={"time": date_range},
    dims=("time", "south_north", "west_east"),
)

hourly_ds = xr.merge([ffmc, m_o])
hourly_ds["Time"] = hourly_ds["time"]
dmc = getdate("dmc", date_of_int, 6, "P")
dc = getdate("dc", date_of_int, 15, "D")

hourly_ds.F.attrs["description"] = "FINE FUEL MOISTURE CODE"
hourly_ds.m_o.attrs["description"] = "FINE FUEL MOISTURE CONTENT"
make_dir = Path(
    str(fwf_zarr_dir) + str("/fwf-hourly-") + domain + str(f"-2019033106.zarr")
)
hourly_ds = hourly_ds.compute()
hourly_ds.to_zarr(make_dir, mode="w")


date_range = pd.date_range("2019-03-31", "2019-04-01")
dmc = getdate("dmc", date_of_int, 6, "P")
dmc = np.stack([dmc, dmc])
dmc = xr.DataArray(
    dmc,
    name="P",
    coords={"time": date_range},
    dims=("time", "south_north", "west_east"),
)

dc = getdate("dc", date_of_int, 15, "D")
dc = np.stack([dc, dc])
dc = xr.DataArray(
    dc, name="D", coords={"time": date_range}, dims=("time", "south_north", "west_east")
)


r_o_tomorrow = xr.DataArray(
    np.zeros(dmc.shape, dtype=float),
    name="r_o_tomorrow",
    dims=("time", "south_north", "west_east"),
)
daily_ds = xr.merge([dmc, dc, r_o_tomorrow])
daily_ds["Time"] = daily_ds["time"]
daily_ds.P.attrs["description"] = "DUFF MOISTURE CODE"
daily_ds.D.attrs["description"] = "DROUGHT CODE"
make_dir = Path(
    str(fwf_zarr_dir) + str("/fwf-daily-") + domain + str(f"-2019033106.zarr")
)
daily_ds = daily_ds.compute()
daily_ds.to_zarr(make_dir, mode="w")


# self.F_initial = 85.0
# self.P_initial = 6.0
# self.D_initial = 15.0
# self.snowfract = 0.5
