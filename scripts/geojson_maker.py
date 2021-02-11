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

from context import data_dir, xr_dir, wrf_dir, root_dir, fwf_zarr_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


import warnings

warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")


### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

### Open nested index json
with open(str(data_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)

### Get ForecastTime
forecast_date = pd.Timestamp("today").strftime("%Y%m%d06")
# forecast_date = pd.Timestamp(2021, 2, 9).strftime("%Y%m%d06")

for domain in ["d02", "d03"]:
    hourly_file_dir = str(fwf_zarr_dir) + str(
        f"/fwf-hourly-{domain}-{forecast_date}.zarr"
    )
    daily_file_dir = str(fwf_zarr_dir) + str(
        f"/fwf-daily-{domain}-{forecast_date}.zarr"
    )

    hourly_ds = xr.open_zarr(hourly_file_dir)
    daily_ds = xr.open_zarr(daily_file_dir)

    r_hourly_list = []
    for i in range(len(hourly_ds.Time)):
        r_hour = hourly_ds.r_o_hourly[i : i + 3].sum(dim="time")
        r_hourly_list.append(r_hour)
    r_hourly = np.stack(r_hourly_list)
    r_hourly = xr.DataArray(
        r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
    )
    hourly_ds["r_o_3hour"] = r_hourly

    hourly_vars = ["F", "R", "S", "DSR", "W", "T", "H", "r_o", "r_o_3hour", "SNW"]
    for var in hourly_vars:
        hourly_ds[var] = xr.where(
            hourly_ds[var] < cmaps[var]["vmax"],
            hourly_ds[var],
            int(cmaps[var]["vmax"] + 1),
        )

    daily_vars = ["D", "P", "U"]
    for var in daily_vars:
        daily_ds[var] = xr.where(
            daily_ds[var] < cmaps[var]["vmax"],
            daily_ds[var],
            int(cmaps[var]["vmax"] + 1),
        )

    # ## Get first timestamp of forecast and make dir to store files
    timestamp = np.array(hourly_ds.Time.dt.strftime("%Y%m%d%H"))
    folderdate = timestamp[0]
    # ### make dir for that days forecast files
    # forecast_dir = Path("/bluesky/archive/fireweather/forecasts/" + str(folderdate) + "/data/plot")
    # forecast_dir = Path("/bluesky/fireweather/fwf/web_dev/data/")
    # forecast_dir.mkdir(parents=True, exist_ok=True)

    make_dir = Path("/bluesky/fireweather/fwf/data/geojson/" + str(folderdate))
    make_dir.mkdir(parents=True, exist_ok=True)

    ## Make geojson of ffmc, isi, fwf every 6 hours
    print(f"{str(datetime.now())} ---> start loop of hourly fwf products")

    lenght = len(hourly_ds.F)
    index = np.arange(0, lenght, 3, dtype=int)
    for i in index:
        mycontourf_to_geojson(
            cmaps, "F", hourly_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "R", hourly_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "S", hourly_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "W", hourly_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "T", hourly_ds, i, folderdate, "colors47", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "H", hourly_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "r_o", hourly_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps,
            "r_o_3hour",
            hourly_ds,
            i,
            folderdate,
            "colors18",
            domain,
            nested_index,
        )
        mycontourf_to_geojson(
            cmaps, "SNW", hourly_ds, i, folderdate, "colors", domain, nested_index
        )

    print(f"{str(datetime.now())} ---> end loop of hourly fwf products")

    # ## Make geojson of dmc, dc, bui at noon local for the two day forecast period
    print(f"{str(datetime.now())} ---> start loop of daily fwf products")

    for i in range(len(daily_ds.Time)):
        mycontourf_to_geojson(
            cmaps, "P", daily_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "D", daily_ds, i, folderdate, "colors18", domain, nested_index
        )
        mycontourf_to_geojson(
            cmaps, "U", daily_ds, i, folderdate, "colors18", domain, nested_index
        )

    print(f"{str(datetime.now())} ---> end loop of daily fwf products")

# ### Timer
print("Run Time: ", datetime.now() - startTime)
