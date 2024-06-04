#!/bluesky/fireweather/miniconda3/envs/fwx/bin/python

"""
Creates geojson files for each fwf forecast prodcut. Used as intermediate step for dispaly on leaflet map.
NOTE: The geojson file get post processed to topojson for use on leaflet.
      The node_module geo2topo in topojson-server handles convertion

"""
import context
import sys
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr
import geojsoncontour
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from utils.geoutils import mask, mycontourf_to_geojson
from datetime import datetime, date, timedelta

startTime = datetime.now()

from context import data_dir, root_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


import warnings

warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")


### make folder for json files on webapge
# forecast_date = pd.Timestamp("today").strftime("%Y%m%d")
forecast_date = pd.Timestamp(2024, 6, 3).strftime("%Y%m%d")
make_dir = Path(f"/bluesky/archive/fireweather/forecasts/{forecast_date}00/data/map")
make_dir.mkdir(parents=True, exist_ok=True)

## redefine forecast ate to get file with spin up
forecast_date = forecast_date + "06"
# forecast_date = pd.Timestamp(2023, 7, 18).strftime("%Y%m%d06")

### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

### Open nested index json
with open(str(root_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    return ds

ny = (417 * 3) - 12
nx = (627 * 3) - 12
target_grid = salem.Grid(
    nxny=(nx, ny),
    dxdy=(4000.0, 4000.0),
    x0y0=(-3593999.2734108134, -6343328.220350546),
    # proj=hourly_d02.attrs["pyproj_srs"],
    proj= '+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs'
).to_dataset()

def open_fwf(domain, target_grid):
    loopTime = datetime.now()
    hourly_file_dir = str(data_dir) + str(f"/fwf-data/fwf-hourly-{domain}-{forecast_date}.nc")
    daily_file_dir = str(data_dir) + str(f"/fwf-data/fwf-daily-{domain}-{forecast_date}.nc")

    hourly_ds = salem.open_xr_dataset(hourly_file_dir)[["FRP", "F", "R", "S", "HFI", "ROS", "CFB", "SFC", "TFC", "W", "T", "H", "r_o", "SNW"]]
    daily_ds = salem.open_xr_dataset(daily_file_dir)[["D", "P", "U"]]
    hourly_ds = hourly_ds.load()
    daily_ds = daily_ds.load()
    if domain == 'd03':
        daily_ds = daily_ds.isel(west_east=slice(30, 610), south_north=slice(30, 810))
        hourly_ds = hourly_ds.isel(west_east=slice(30, 610), south_north=slice(30, 810))
    # y1, y2, x1, x2 = (
    #     nested_index["y1_" + domain],
    #     nested_index["y2_" + domain],
    #     nested_index["x1_" + domain],
    #     nested_index["x2_" + domain],
    # )
    # shape = daily_ds.XLAT.shape
    # I = np.arange(y1, shape[0] - y2)
    # J = np.arange(x1, shape[1] - x2)
    # hourly_ds, daily_ds  = hourly_ds.isel(south_north=I, west_east=J), daily_ds.isel(south_north=I, west_east=J)
    hourly_ds, daily_ds  = target_grid.salem.transform(hourly_ds,interp="nearest"), target_grid.salem.transform(daily_ds, interp="nearest")
    print('Time to tranform datasets: ', datetime.now() - loopTime )
    return hourly_ds, daily_ds


hourly_d02, daily_d02 = open_fwf('d02', target_grid)
hourly_d03, daily_d03 = open_fwf('d03', target_grid)


hourly_ds = xr.where(~np.isnan(hourly_d03), hourly_d03, hourly_d02)
daily_ds = xr.where(~np.isnan(daily_d03), daily_d03, daily_d02)


fwf_hourly_d02["R"] = xr.where(
    ~np.isnan(fwf_hourly_d03["R"]), fwf_hourly_d03["R"], fwf_hourly_d02["R"]
)
# shape_d02 = hourly_d02['XLONG'].shape
# ny = (shape_d02[0] * 3) - 12
# nx = (shape_d02[1] * 3) - 12
ny = (408 * 3) - 12
nx = (624 * 3) - 12
target_grid = salem.Grid(
    nxny=(nx, ny),
    dxdy=(4000.0, 4000.0),
    x0y0=(-3593999.2734108134, -6343328.220350546),
    proj=hourly_d02.attrs["pyproj_srs"],
).to_dataset()

r_hourly_list = []
for i in range(len(hourly_ds.Time)):
    r_hour = hourly_ds.r_o_hourly[i : i + 3].sum(dim="time")
    r_hourly_list.append(r_hour)
r_hourly = np.stack(r_hourly_list)
r_hourly = xr.DataArray(
    r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
)
hourly_ds["r_o_3hour"] = r_hourly

hourly_vars = [
    "F",
    "R",
    "S",
    "HFI",
    "ROS",
    "CFB",
    "SFC",
    "TFC",
    "W",
    "T",
    "H",
    "r_o",
    "r_o_3hour",
    "SNW",
]
for var in hourly_vars:
    hourly_ds[var] = xr.where(
        hourly_ds[var] < cmaps[var]["vmax"],
        hourly_ds[var],
        int(cmaps[var]["vmax"] + 1),
    )
    if var == "CFB":
        hourly_ds[var] = hourly_ds[var].round(0) * 100
    else:
        hourly_ds[var] = hourly_ds[var].round(0)

daily_vars = ["D", "P", "U"]
for var in daily_vars:
    daily_ds[var] = xr.where(
        daily_ds[var] < cmaps[var]["vmax"],
        daily_ds[var],
        int(cmaps[var]["vmax"] + 1),
    )
    daily_ds[var] = daily_ds[var].round(0)

# ## Get first timestamp of forecast and make dir to store files
timestamp = np.array(hourly_ds.Time.dt.strftime("%Y%m%d%H"))
folderdate = timestamp[0]

### make dir for that days forecast files
forecast_dir = Path(
    "/bluesky/archive/fireweather/forecasts/" + str(folderdate) + "/data/plot"
)
forecast_dir = Path("/bluesky/fireweather/fwf/web_dev/data/")
forecast_dir.mkdir(parents=True, exist_ok=True)

make_dir = Path("/bluesky/fireweather/fwf/data/geojson/" + str(folderdate))
make_dir.mkdir(parents=True, exist_ok=True)

# ## Make geojson of dmc, dc, bui at noon local for the two day forecast period
print(
    f"{str(datetime.now())} ---> start loop of daily fwf products for domain {domain}"
)
try:
    for i in range(len(daily_ds.Time)):
        ds = daily_ds.isel(time=i)
        timestamp = np.array(ds.Time.dt.strftime("%Y%m%d%H")).tolist()
        timestamp = timestamp[:-2]
        for var in daily_vars:
            mycontourf_to_geojson(
                cmaps, var, ds[var], folderdate, domain, timestamp
            )
except:
    ds = daily_ds.isel(time=0)
    timestamp = np.array(ds.Time.dt.strftime("%Y%m%d%H")).tolist()
    timestamp = timestamp[:-2]
    for var in daily_vars:
        mycontourf_to_geojson(cmaps, var, ds[var], folderdate, domain, timestamp)

print(
    f"{str(datetime.now())} ---> end loop of daily fwf products for domain {domain}"
)

# Make geojson of ffmc, isi, fwf every 3 hours
print(
    f"{str(datetime.now())} ---> start loop of hourly fwf products for domain {domain}"
)

lenght = len(hourly_ds.F)
index = np.arange(0, lenght, 3, dtype=int)
for i in index:
    ds = hourly_ds.isel(time=i)
    timestamp = np.array(ds.Time.dt.strftime("%Y%m%d%H")).tolist()
    for var in hourly_vars:
        mycontourf_to_geojson(cmaps, var, ds[var], folderdate, domain, timestamp)
print(
    f"{str(datetime.now())} ---> end loop of hourly fwf products for domain {domain}"
)


# ### Timer
print("Run Time: ", datetime.now() - startTime)
