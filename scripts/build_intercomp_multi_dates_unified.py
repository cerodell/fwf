import context
import io
import json
import requests
import salem

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.make_intercomp import daily_merge_ds

from context import data_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

wrf_model = "wrf4"
domain = "d02"
date_range = pd.date_range("2022-06-24", "2022-08-01")

nc_filein = "/Volumes/WFRT-Data02/FWF-WAN00CG/d02/"
## make dir for that intercomp files if it doest not all ready exist
make_dir = Path(str(data_dir) + "/intercomp/")
make_dir.mkdir(parents=True, exist_ok=True)

### Open nested grid json
with open(str(data_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)

### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Get All Stations CSV
url = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv"
stations_df_og = pd.read_csv(url, sep=",")
stations_df_og = stations_df_og.drop_duplicates(subset="wmo", keep="last")
stations_df = stations_df_og.drop(
    columns=["tmm", "ua", "the_geom", "h_bul", "s_bul", "hly", "syn"]
)


wrf_filein = "/wrf/"
wrf_file_dir = str(data_dir) + wrf_filein
wrf_file_dir = sorted(Path(wrf_file_dir).glob(f"wrfout_{domain}_*"))
wrf_file = Dataset(wrf_file_dir[0], "r")
shape = np.shape(xr.open_dataset(wrf_file_dir[0]).XLAT[0, :, :])


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
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["x"] > (shape[1] - x2 - 1))]
)
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["y"] > (shape[0] - y2 - 1))]
)
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["x"] < x1 - 1)])
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["y"] < y1 - 1)])

# filein_obs = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_fwi2020sopEC.csv"
# obs_df = pd.read_csv(filein_obs, sep=",", skiprows=0)


# """######### get directory to yesterdays hourly/daily .zarr files.  #############"""
def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


for date in date_range:
    day1_obs_date = date.strftime("%Y%m%d06")
    day2_obs_date = date - np.timedelta64(1, "D")
    day2_obs_date = day2_obs_date.strftime("%Y%m%d06")

    era5_ds = salem.open_xr_dataset(
        nc_filein + f"/era5/fwf-daily-{domain}-{day1_obs_date}.nc"
    )

    day1_ds = salem.open_xr_dataset(
        nc_filein + f"/forecast/fwf-daily-{domain}-{day1_obs_date}.nc"
    )
    try:
        day2_ds = salem.open_xr_dataset(
            nc_filein + f"/forecast/fwf-daily-{domain}-{day2_obs_date}.nc"
        )
    except:
        day2_ds = None

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
    del obs_df["NAME"]
    obs_df["wmo"] = obs_df["WMO"].astype(str).astype(int)
    del obs_df["WMO"]
    obs_df.columns = obs_df.columns.str.lower()

    # index obs dateframe to get date of interest
    # obs_df_on_date = obs_df[
    #     obs_df["rep_date"] == date.strftime("%Y-%m-%d 12:00:00")
    # ]
    wmo_df = stations_df
    final_df = wmo_df.merge(obs_df, on="wmo", how="left")
    # merge with stations data information
    # final_df = wmo_df.merge(obs_df_on_date, on="wmo", how="left")
    final_df = final_df.replace("NULL", np.nan)
    final_df = final_df.replace(" NULL", np.nan)
    final_df = final_df.replace("  NULL", np.nan)
    final_df = final_df.drop_duplicates(subset=["wmo"], keep="last")
    ## convert to float 32 for smaller storage
    final_df = final_df.astype(
        {
            "temp": "float32",
            "td": "float32",
            "rh": "float32",
            "ws": "float32",
            "wdir": "float32",
            "precip": "float32",
            "ffmc": "float32",
            "dmc": "float32",
            "dc": "float32",
            "bui": "float32",
            "isi": "float32",
            "fwi": "float32",
            "dsr": "float32",
        }
    )
    gpm25 = gpd.GeoDataFrame(
        final_df,
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(final_df["lon"], final_df["lat"]),
    ).to_crs(
        "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
    )
    # gpm25["west_east"], gpm25["south_north"] = gpm25.geometry.x, gpm25.geometry.y
    # gpm25.head()
    x = xr.DataArray(
        np.array(gpm25.geometry.x),
        dims="wmo",
        coords=dict(wmo=gpm25.wmo.values),
    )
    y = xr.DataArray(
        np.array(gpm25.geometry.y),
        dims="wmo",
        coords=dict(wmo=gpm25.wmo.values),
    )
    south_north, west_east = final_df["y"].values, final_df["x"].values
    var_list = list(day1_ds)
    remove = ["r_o_tomorrow", "SNOWC", "r_o_hourly"]
    var_list = list(set(var_list) - set(remove))
    final_var_list = []
    for var in var_list:
        name_lower = cmaps[var]["name"].lower()

        ## get era5 models values at wxstation locations
        var_columns_interp = era5_ds[var].interp(west_east=x, south_north=y).values
        var_columns_interp = np.array(var_columns_interp, dtype="float32")
        final_df[name_lower + "_era5_interp"] = var_columns_interp[0, :]

        var_columns = era5_ds[var].values[:, south_north, west_east]
        var_columns = np.array(var_columns, dtype="float32")
        final_df[name_lower + "_era5_nearest"] = var_columns[0, :]

        ## get fwf models values at wxstation locations for day 1 forecast
        var_columns_interp = day1_ds[var].interp(west_east=x, south_north=y).values
        var_columns_interp = np.array(var_columns_interp, dtype="float32")
        final_df[name_lower + "_day1_interp"] = var_columns_interp[0, :]

        var_columns = day1_ds[var].values[:, south_north, west_east]
        var_columns = np.array(var_columns, dtype="float32")
        final_df[name_lower + "_day1_nearest"] = var_columns[0, :]

        if day2_ds is None:
            # print('day2_ds is none')
            a = np.empty(len(south_north))
            a[:] = np.nan
            a = np.array(a, dtype="float32")
            final_df[name_lower + "_day2_interp"] = a
            final_df[name_lower + "_day2_nearest"] = a

        else:
            ## get fwf models values at wxstation locations for day 2 forecast
            var_columns_interp = day2_ds[var].interp(west_east=x, south_north=y).values
            var_columns_interp = np.array(var_columns_interp, dtype="float32")

            var_columns = day2_ds[var].values[:, south_north, west_east]
            var_columns = np.array(var_columns, dtype="float32")
            try:
                final_df[name_lower + "_day2_interp"] = var_columns_interp[1, :]
                final_df[name_lower + "_day2_nearest"] = var_columns[1, :]
            except:
                a = np.empty(len(south_north))
                a[:] = np.nan
                a = np.array(a, dtype="float32")
                final_df[name_lower + "_day2_interp"] = a
                final_df[name_lower + "_day2_nearest"] = a
        ## append varible names to list
        final_var_list.append(name_lower)
        final_var_list.append(name_lower + "_era5_interp")
        final_var_list.append(name_lower + "_era5_nearest")
        final_var_list.append(name_lower + "_day1_interp")
        final_var_list.append(name_lower + "_day1_nearest")
        final_var_list.append(name_lower + "_day2_interp")
        final_var_list.append(name_lower + "_day2_nearest")

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
    for var in final_var_list:
        var = var.lower()
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
        "wrfout/fwf/era5 model versus wmo weather station observations"
    ).upper()
    for var in var_list:
        name_lower = cmaps[var]["name"].lower()
        attrs = day1_ds[var].attrs
        intercomp_today_ds[name_lower].attrs["description"] = attrs
        intercomp_today_ds[name_lower].attrs["description"] = (
            "OBSERVED " + attrs["description"]
        )

        intercomp_today_ds[name_lower + "_era5_interp"].attrs["description"] = attrs
        intercomp_today_ds[name_lower + "_era5_interp"].attrs["description"] = (
            "ERA5 INTERPOLATED " + attrs["description"]
        )

        intercomp_today_ds[name_lower + "_era5_nearest"].attrs["description"] = attrs
        intercomp_today_ds[name_lower + "_era5_nearest"].attrs["description"] = (
            "ERA5 NEAREST NEIGHBOR " + attrs["description"]
        )

        intercomp_today_ds[name_lower + "_day1_interp"].attrs["description"] = attrs
        intercomp_today_ds[name_lower + "_day1_interp"].attrs["description"] = (
            "ONE DAY INTERPOLATED FORECASTED " + attrs["description"]
        )

        intercomp_today_ds[name_lower + "_day1_nearest"].attrs["description"] = attrs
        intercomp_today_ds[name_lower + "_day1_nearest"].attrs["description"] = (
            "ONE DAY NEAREST NEIGHBOR FORECASTED " + attrs["description"]
        )

        intercomp_today_ds[name_lower + "_day2_interp"].attrs["description"] = attrs
        intercomp_today_ds[name_lower + "_day2_interp"].attrs["description"] = (
            "TWO DAY INTERPOLATED FORECASTED " + attrs["description"]
        )

        intercomp_today_ds[name_lower + "_day2_nearest"].attrs["description"] = attrs
        intercomp_today_ds[name_lower + "_day2_nearest"].attrs["description"] = (
            "TWO DAY NEAREST NEIGHBOR FORECASTED " + attrs["description"]
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
        print(final_ds)
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
        print(final_ds)

### Timer
print("Total Run Time: ", datetime.now() - startTime)
