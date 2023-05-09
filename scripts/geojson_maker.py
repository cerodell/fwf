#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
/bluesky/bsf-ops/modules/HYSPLIT/v7/
Creates geojson files for each fwf forecast prodcut. Used as intermediate step for dispaly on leaflet map.
NOTE: The geojson file get post processed to topojson for use on leaflet.
      The node_module geo2topo in topojson-server handles convertion

"""
import context
import sys
import json
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

from context import data_dir, xr_dir, wrf_dir, root_dir, fwf_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


import warnings

warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")


### make folder for json files on webapge
forecast_date = pd.Timestamp("today").strftime("%Y%m%d")
make_dir = Path(f"/bluesky/archive/fireweather/forecasts/{forecast_date}00/data/map")
# make_dir.mkdir(parents=True, exist_ok=True)

## redefine forecast ate to get file with spin up
forecast_date = forecast_date + "06"
# forecast_date = pd.Timestamp(2021, 2, 9).strftime("%Y%m%d06")

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


for domain in ["d02", "d03"]:
    hourly_file_dir = str(fwf_dir) + str(f"/fwf-hourly-{domain}-{forecast_date}.nc")
    daily_file_dir = str(fwf_dir) + str(f"/fwf-daily-{domain}-{forecast_date}.nc")

    hourly_ds = xr.open_dataset(hourly_file_dir)
    daily_ds = xr.open_dataset(daily_file_dir)
    hourly_ds = hourly_ds.load()
    daily_ds = daily_ds.load()
    y1, y2, x1, x2 = (
        nested_index["y1_" + domain],
        nested_index["y2_" + domain],
        nested_index["x1_" + domain],
        nested_index["x2_" + domain],
    )

    shape = daily_ds.XLAT.shape
    I = np.arange(y1, shape[0] - y2)
    J = np.arange(x1, shape[1] - x2)
    hourly_ds = hourly_ds.isel(south_north=I, west_east=J)
    daily_ds = daily_ds.isel(south_north=I, west_east=J)

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
