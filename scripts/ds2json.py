#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Creates json files with an alpabettic identifer for use on the website.
The json files are boxes (or subdomains) of grided fwf data for geocraphic locations in the model domain.

"""

import context
import json
import bson
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
import string

from context import data_dir, root_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()

from bson import json_util
import matplotlib as mpl
import matplotlib.colors
import cartopy.crs as crs
import matplotlib.pyplot as plt
from wrf import getvar, g_uvmet, geo_bounds


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

### make folder for json files on webapge
forecast_date = pd.Timestamp("today").strftime("%Y%m%d")
make_dir = Path(f"/bluesky/archive/fireweather/forecasts/{forecast_date}00/data/plot")
make_dir.mkdir(parents=True, exist_ok=True)

## redefine forecast ate to get file with spin up
forecast_date = forecast_date + "06"
# forecast_date = pd.Timestamp(2021, 2, 9).strftime("%Y%m%d06")

### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

### Open nested grid json
with open(str(root_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    # for var in list(ds):
    #     ds[var].encoding = {}
    return ds


## loop both domains
domains = ["d02"]
for domain in domains:
    ## Get Path to most recent FWI forecast and open
    print(f"Starting to make jsons for {domain}")
    loopTime = datetime.now()
    hourly_file_dir = str(data_dir) + str(f"/fwf-data/fwf-hourly-{domain}-{forecast_date}.nc")
    daily_file_dir = str(data_dir) + str(f"/fwf-data/fwf-daily-{domain}-{forecast_date}.nc")

    static_ds = xr.open_dataset(
        str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
    )

    ### Open datasets
    hourly_ds = xr.open_dataset(hourly_file_dir)
    daily_ds = xr.open_dataset(daily_file_dir)

    ## Round all var is the dataset
    hourly_ds = hourly_ds.round(2)
    daily_ds = daily_ds.round(2)
    # hourly_ds = rechunk(hourly_ds)
    # daily_ds = rechunk(daily_ds)

    ## get array of time and day
    time = np.array(hourly_ds.Time.dt.strftime("%Y-%m-%dT%H"), dtype="<U13")
    day = np.array(daily_ds.Time.dt.strftime("%Y-%m-%d"), dtype="<U10")

    ## Get first timestamp of forecast and make dir to store files
    timestamp = datetime.strptime(str(time[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

    ### Open web grid json
    with open(str(data_dir) + f"/json/fwf-zone-{domain}.json") as f:
        filezone = json.load(f)

    ## get index to remove boundary conditions
    n, y1, y2, x1, x2 = (
        nested_index["n"],
        nested_index["y1_" + domain],
        nested_index["y2_" + domain],
        nested_index["x1_" + domain],
        nested_index["x2_" + domain],
    )
    # unique_y, unique_x = nested_index['unique_y'], nested_index['unique_x']

    ## get unique time zone ids and remove nested d03 domain from d02.
    empty = np.array(filezone["ZONE"])
    unique_masked, index_masked, counts_masked = np.unique(
        empty, return_index=True, return_counts=True
    )
    unique_masked_list = unique_masked.tolist()
    if domain == "d02":
        unique_masked_list.remove("d3")
    else:
        pass

    ## remove some unwanted variables from dataset
    hourly_var_list = list(hourly_ds)
    remove = [
        "SNOWC",
        "SNOWH",
        "U10",
        "V10",
        "m_o",
        "r_o_hourly",
        "FMC",
        "ISI",
    ]
    hourly_var_list = list(set(hourly_var_list) - set(remove))

    ## remove some unwanted variables from dataset
    daily_var_list = list(daily_ds)
    remove = [
        "SNOWC",
        "F",
        "H",
        "T",
        "R",
        "W",
        "WD",
        "r_o",
        "r_o_hourly",
        "r_o_tomorrow",
    ]
    daily_var_list = list(set(daily_var_list) - set(remove))

    ## get array of lats and longs remove bad boundary conditions and flatten
    xlat = daily_ds.XLAT.values[y1:-y2, x1:-x2]
    xlon = daily_ds.XLONG.values[y1:-y2, x1:-x2]
    tzon = static_ds.ZoneDT.values[y1:-y2, x1:-x2]
    fuel = static_ds.FUELS_D.values[y1:-y2, x1:-x2]

    xlat = np.round(xlat.flatten(), 5)
    xlon = np.round(xlon.flatten(), 5)
    tzon = tzon.flatten()
    fuel = fuel.flatten()

    ## build dictionary with removed bad boundary conditions fro each variable in dataset
    ## also reshape into (time, (flatten XLAT/XLONG))
    dict_var = {}
    for var in hourly_var_list:
        var_name = cmaps[var]["name"].lower()
        var_array = hourly_ds[var].values
        var_array = var_array[:, y1:-y2, x1:-x2]
        time_shape = var_array.shape
        var_array = var_array.reshape(time_shape[0], (time_shape[1] * time_shape[2]))
        dict_var.update({var_name: var_array})

    ## build dictionary with removed bad boundary conditions fro each variable in dataset
    ## also reshape into (time, (flatten XLAT/XLONG))
    for var in daily_var_list:
        var_name = cmaps[var]["name"].lower()
        var_array = daily_ds[var].values
        var_array = var_array[:, y1:-y2, x1:-x2]
        time_shape = var_array.shape
        var_array = var_array.reshape(time_shape[0], (time_shape[1] * time_shape[2]))
        dict_var.update({var_name: var_array})

    ## flatten empty array
    empty = empty.flatten()
    # unique_masked_list = ['gk']
    ## added to dictionary all variables with in there unique group
    for filename in unique_masked_list:
        # print(filename)
        dict_file = {"Time": time.tolist(), "Day": day.tolist()}
        inds = np.where(empty == filename)
        for var in dict_var:
            var_name = var
            # print(var_name)
            var_array = dict_var[var]
            var_array = var_array[:, inds[0]]
            var_array = var_array.astype("float64")
            var_array = np.round(var_array, decimals=2)
            var_array = var_array.tolist()
            dict_file.update({var_name: str(var_array)})
            # Write json file to defind dir
        xlat_array = xlat[inds[0]]
        xlat_array = xlat_array.astype("<U8")
        xlon_array = xlon[inds[0]]
        xlon_array = xlon_array.astype("<U8")
        tzon_array = tzon[inds[0]]
        tzon_array = tzon_array.astype("<U2")
        fuel_array = fuel[inds[0]]
        fuel_array = fuel_array.astype("<U2")

        dict_file.update(
            {
                "XLAT": xlat_array.tolist(),
                "XLONG": xlon_array.tolist(),
                "TZONE": tzon_array.tolist(),
                "FUEL": fuel_array.tolist(),
            }
        )

        ## write json files :)
        with open(
            str(make_dir) + f"/fwf-{filename}-{timestamp}-{domain}.json", "w"
        ) as f:
            json.dump(
                dict_file,
                f,
                default=json_util.default,
                separators=(",", ":"),
                indent=None,
            )
        # print(
        #     f"{str(datetime.now())} ---> wrote json to:  "
        #     + str(make_dir)
        #     + f"/fwf-{filename}-{timestamp}-{domain}.json"
        # )
    print(f"Took {datetime.now() - loopTime} to make jsons for {domain}")


# ### Timer
print("Run Time: ", datetime.now() - startTime)
