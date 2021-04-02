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

from context import data_dir, root_dir, tzone_dir, fwf_zarr_dir


def daily_merge_ds(date_to_merge, domain, wrf_model):

    hourly_file_dir = str(fwf_zarr_dir) + str(
        f"/fwf-hourly-{domain}-{date_to_merge}.zarr"
    )
    daily_file_dir = str(fwf_zarr_dir) + str(
        f"/fwf-daily-{domain}-{date_to_merge}.zarr"
    )

    # hourly_file_dir = str(data_dir) + str(
    #     f"/FWF-WAN00CP-04/fwf-hourly-{domain}-{date_to_merge}.zarr"
    # )
    # daily_file_dir = str(data_dir) + str(
    #     f"/FWF-WAN00CP-04/fwf-daily-{domain}-{date_to_merge}.zarr"
    # )
    ### Open datasets
    my_dir = Path(hourly_file_dir)
    if my_dir.is_dir():
        hourly_ds = xr.open_zarr(hourly_file_dir)

        daily_ds = xr.open_zarr(daily_file_dir)
        ### Call on variables
        tzone_ds = xr.open_zarr(
            str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
        )
        tzone = tzone_ds.ZoneDT.values
        shape = tzone.shape
        ## create I, J for quick indexing
        I, J = np.ogrid[: shape[0], : shape[1]]
        time_array = hourly_ds.Time.values
        try:
            int_time = int(pd.Timestamp(time_array[0]).hour)
        except:
            int_time = int(pd.Timestamp(time_array).hour)

        length = len(time_array) + 1
        num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
        index = [
            i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
        ]
        # print(f"index of times {index} with initial time {int_time}Z")

        ## loop every 24 hours
        files_ds = []
        for i in index:
            # print(i)

            ## loop each variable
            mean_da = []
            for var in ["DSR", "F", "R", "S"]:
                if var == "SNOWC":
                    var_array = hourly_ds[var].values
                    noon = var_array[(i + tzone), I, J]
                    day = np.array(hourly_ds.Time[i + 1], dtype="datetime64[D]")
                    # print(np.array(hourly_ds.Time[i]))
                    var_da = xr.DataArray(
                        noon,
                        name=var,
                        dims=("south_north", "west_east"),
                        coords=hourly_ds.isel(time=i).coords,
                    )
                    var_da["Time"] = day
                    mean_da.append(var_da)
                else:
                    # print(np.array(hourly_ds.Time[i]))
                    var_array = hourly_ds[var].values
                    noon_minus = var_array[(i + tzone - 1), I, J]
                    noon = var_array[(i + tzone), I, J]
                    noon_pluses = var_array[(i + tzone + 1), I, J]
                    noon_mean = (noon_minus + noon + noon_pluses) / 3
                    day = np.array(hourly_ds.Time[i + 1], dtype="datetime64[D]")
                    var_da = xr.DataArray(
                        noon_mean,
                        name=var,
                        dims=("south_north", "west_east"),
                        coords=hourly_ds.isel(time=i).coords,
                    )
                    var_da["Time"] = day
                    var_da.attrs = hourly_ds[var].attrs
                    mean_da.append(var_da)

            mean_ds = xr.merge(mean_da)
            files_ds.append(mean_ds)

        hourly_daily_ds = xr.combine_nested(files_ds, "time")
        final_ds = xr.merge([daily_ds, hourly_daily_ds], compat="override")
        final_ds.attrs = hourly_ds.attrs

    else:
        final_ds = None

    return final_ds


def make_daily_noon(ds, domain, wrf_model):

    ### Call on variables
    tzone_ds = xr.open_zarr(
        str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
    )
    tzone = tzone_ds.ZoneDT.values
    shape = tzone.shape
    ## create I, J for quick indexing
    I, J = np.ogrid[: shape[0], : shape[1]]
    time_array = ds.Time.values
    try:
        int_time = int(pd.Timestamp(time_array[0]).hour)
    except:
        int_time = int(pd.Timestamp(time_array).hour)

    length = len(time_array) + 1
    num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
    index = [
        i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
    ]
    print(f"index of times {index} with initial time {int_time}Z")
    ## loop every 24 hours
    list_ds = []
    ## loop each variable
    for var in list(ds):
        print(var)
        var_array = ds[var].values
        mean_da = []
        for i in index:
            noon_minus = var_array[(i + tzone - 1), I, J]
            noon = var_array[(i + tzone), I, J]
            noon_pluses = var_array[(i + tzone + 1), I, J]
            noon_mean = (noon_minus + noon + noon_pluses) / 3
            day = np.array(ds.Time[i + 1], dtype="datetime64[D]")
            var_da = xr.DataArray(
                noon_mean,
                name=var,
                dims=("south_north", "west_east"),
                coords=ds.isel(time=i).coords,
            )
            var_da["Time"] = day
            var_da.attrs = ds[var].attrs
            mean_da.append(var_da)

        var_ds = xr.combine_nested(mean_da, "time")
        list_ds.append(var_ds)

    final_ds = xr.merge(list_ds)
    final_ds.attrs = ds.attrs

    return final_ds
