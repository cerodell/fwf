import context
import io
import json
import requests

import numpy as np
import pandas as pd
import xarray as xr
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.make_intercomp import daily_merge_ds

from context import data_dir, root_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

wrf_model = "wrf4"
## make dir for that intercomp files if it doest not all ready exist
make_dir = Path(str(data_dir) + "/intercomp/")
make_dir.mkdir(parents=True, exist_ok=True)

### Open nested grid json
with open(str(root_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)

### Open color map json
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Get All Stations CSV
url = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv"
stations_df_og = pd.read_csv(url, sep=",")
stations_df_og = stations_df_og.drop_duplicates(subset="wmo", keep="last")
stations_df_og = stations_df_og.drop(
    columns=["tmm", "ua", "the_geom", "h_bul", "s_bul", "hly", "syn"]
)

date_range = pd.date_range("2021-12-01", "2021-12-31")
domains = ["d03"]
# """######### get directory to yesterdays hourly/daily .zarr files.  #############"""
def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


for date in date_range:
    stations_df = stations_df_og
    day1_obs_date = date.strftime("%Y%m%d06")
    day2_obs_date = date - np.timedelta64(1, "D")
    day2_obs_date = day2_obs_date.strftime("%Y%m%d06")

    for domain in domains:
        stations_df = stations_df_og

        day1_ds = daily_merge_ds(day1_obs_date, domain, wrf_model)
        # day1_ds = daily_merge_ds(day2_obs_date, domain, wrf_model)

        day2_ds = daily_merge_ds(day2_obs_date, domain, wrf_model)

        ### Get a wrf file
        wrf_filein = "/wrf/"
        wrf_file_dir = str(data_dir) + wrf_filein
        wrf_file_dir = sorted(Path(wrf_file_dir).glob(f"wrfout_{domain}_*"))
        wrf_file = Dataset(wrf_file_dir[0], "r")

        ### Get Daily observations CSV
        url2 = f"https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{day1_obs_date[:-2]}.csv"
        headers = list(pd.read_csv(url2, nrows=0))
        obs_df = pd.read_csv(url2, sep=",", names=headers)
        obs_df = obs_df.drop_duplicates()
        obs_df = obs_df.drop(obs_df.index[[0]])
        obs_df["wmo"] = obs_df["WMO"].astype(str).astype(int)
        del obs_df["WMO"]

        ## get index to remove boundary conditions
        n, y1, y2, x1, x2 = (
            nested_index["n"],
            nested_index["y1_" + domain],
            nested_index["y2_" + domain],
            nested_index["x1_" + domain],
            nested_index["x2_" + domain],
        )

        ### Drop stations out sie of model domain
        xy_np = ll_to_xy(wrf_file, stations_df["lat"], stations_df["lon"])
        stations_df["x"] = xy_np[0]
        stations_df["y"] = xy_np[1]
        shape = np.shape(day1_ds.XLAT)
        stations_df = stations_df.drop(
            stations_df.index[np.where(stations_df["x"] > (shape[1] - x2 - 1))]
        )
        stations_df = stations_df.drop(
            stations_df.index[np.where(stations_df["y"] > (shape[0] - y2 - 1))]
        )
        stations_df = stations_df.drop(
            stations_df.index[np.where(stations_df["x"] < x1 - 1)]
        )
        stations_df = stations_df.drop(
            stations_df.index[np.where(stations_df["y"] < y1 - 1)]
        )

        wmo_df = stations_df
        final_df = wmo_df.merge(obs_df, on="wmo", how="left")
        final_df = final_df.replace("NULL", np.nan)
        final_df = final_df.replace(" NULL", np.nan)
        final_df = final_df.replace("  NULL", np.nan)
        final_df = final_df.drop_duplicates(subset=["wmo"], keep="last")
        final_df = final_df.astype(
            {
                "TEMP": "float32",
                "TD": "float32",
                "RH": "float32",
                "WS": "float32",
                "WDIR": "float32",
                "PRECIP": "float32",
                "FFMC": "float32",
                "DMC": "float32",
                "DC": "float32",
                "BUI": "float32",
                "ISI": "float32",
                "FWI": "float32",
                "DSR": "float32",
            }
        )

        south_north, west_east = final_df["y"].values, final_df["x"].values
        var_list = list(day1_ds)
        remove = ["r_o_tomorrow", "SNOWC"]
        var_list = list(set(var_list) - set(remove))
        final_var_list = []
        for var in var_list:
            name_lower = cmaps[var]["name"].lower()
            var_columns = day1_ds[var].values[:, south_north, west_east]
            var_columns = np.array(var_columns, dtype="float32")
            final_df[name_lower + "_day1"] = var_columns[0, :]
            # final_df[name_lower + "_day1"] = var_columns[1, :]

            if day2_ds is None:
                # print('day2_ds is none')
                a = np.empty(len(south_north))
                a[:] = np.nan
                a = np.array(a, dtype="float32")
                final_df[name_lower + "_day2"] = a
            else:
                # print('day2_ds is a ds')
                var_columns = day2_ds[var].values[:, south_north, west_east]
                var_columns = np.array(var_columns, dtype="float32")
                try:
                    final_df[name_lower + "_day2"] = var_columns[1, :]
                except:
                    a = np.empty(len(south_north))
                    a[:] = np.nan
                    a = np.array(a, dtype="float32")
                    final_df[name_lower + "_day2"] = a

            final_var_list.append(name_lower)
            final_var_list.append(name_lower + "_day1")
            final_var_list.append(name_lower + "_day2")

        wmos = final_df["wmo"].values
        _, index, count = np.unique(wmos, return_index=True, return_counts=True)
        ids = final_df["id"].values.astype(str)
        names = final_df["name"].values.astype(str)
        provs = final_df["prov"].values.astype(str)
        lons = final_df["lon"].values.astype("float32")
        lats = final_df["lat"].values.astype("float32")
        elevs = final_df["elev"].values.astype("float32")
        tz_correct = final_df["tz_correct"].values.astype(int)
        try:
            day = np.array(day1_ds.Time[0], dtype="datetime64[D]")
            # day = np.array(day1_ds.Time[1], dtype="datetime64[D]")
        except:
            day = np.array(day1_ds.Time, dtype="datetime64[D]")

        xr_list = []
        final_df.columns = [x.lower() for x in final_df.columns]
        for var in final_var_list:
            var_array = np.array(final_df[var], dtype="float32")
            x = np.stack((final_df[var].values, final_df[var].values))
            xr_var = xr.DataArray(
                x,
                name=f"{var}",
                coords={
                    "wmo": wmos,
                    "time": [day, day],
                    "lats": ("wmo", lats),
                    "lons": ("wmo", lons),
                    "elev": ("wmo", elevs),
                    "name": ("wmo", names),
                    "prov": ("wmo", provs),
                    "id": ("wmo", ids),
                    "tz_correct": ("wmo", tz_correct),
                },
                dims=("time", "wmo"),
            )

            xr_list.append(xr_var)

        intercomp_today_ds = xr.merge(xr_list)
        intercomp_today_ds = intercomp_today_ds.isel(time=0)

        intercomp_today_ds.attrs["TITLE"] = str(
            "wrfout/fwf model versus wmo weather station observations"
        ).upper()
        for var in var_list:
            name_lower = cmaps[var]["name"].lower()
            attrs = day1_ds[var].attrs
            intercomp_today_ds[name_lower].attrs["description"] = attrs
            intercomp_today_ds[name_lower].attrs["description"] = (
                "OBSERVED " + attrs["description"]
            )
            intercomp_today_ds[name_lower + "_day1"].attrs["description"] = attrs
            intercomp_today_ds[name_lower + "_day1"].attrs["description"] = (
                "ONE DAY FORECASTED " + attrs["description"]
            )
            intercomp_today_ds[name_lower + "_day2"].attrs["description"] = attrs
            intercomp_today_ds[name_lower + "_day2"].attrs["description"] = (
                "TWO DAY FORECASTED " + attrs["description"]
            )

        intercomp_today_dir = day1_obs_date[:-2]
        intercomp_yesterday_dir = day2_obs_date[:-2]

        my_dir = Path(
            str(data_dir)
            + "/intercomp/"
            + f"intercomp-{domain}-{intercomp_yesterday_dir}.zarr"
        )
        if my_dir.is_dir():
            intercomp_yesterday_ds = xr.open_zarr(
                str(data_dir)
                + "/intercomp/"
                + f"intercomp-{domain}-{intercomp_yesterday_dir}.zarr"
            )
            final_ds = xr.combine_nested(
                [intercomp_yesterday_ds, intercomp_today_ds], "time"
            )

            final_ds = rechunk(final_ds)
            final_ds.to_zarr(
                str(data_dir)
                + "/intercomp/"
                + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
                mode="w",
            )
            print(
                "Wrote:   "
                + str(data_dir)
                + "/intercomp/"
                + f"intercomp-{domain}-{intercomp_today_dir}.zarr"
            )
        else:
            final_ds = intercomp_today_ds
            final_ds = rechunk(final_ds)
            final_ds.to_zarr(
                str(data_dir)
                + "/intercomp/"
                + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
                mode="w",
            )
            print(
                "Wrote:   "
                + str(data_dir)
                + "/intercomp/"
                + f"intercomp-{domain}-{intercomp_today_dir}.zarr"
            )

### Timer
print("Total Run Time: ", datetime.now() - startTime)
