#!/Users/crodell/miniconda3/envs/fwx/bin/python
import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from context import root_dir


def get_daily_files(fwf, method, start, stop):
    if fwf == True:
        ## get all fwf data derived from era5-land
        pathlist = sorted(
            Path("/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/").glob(
                f"fwf-{method}*"
            )
        )
        x, y = "west_east", "south_north"
    else:
        root = Path("/Volumes/WFRT-Ext25/ecmwf/era5-land/")
        # Get all monthly folders in the root path
        monthly_folders = [folder for folder in root.glob("*") if folder.is_dir()]

        # Iterate through each monthly folder
        daily_files = []
        for monthly_folder in monthly_folders:
            # Get all daily files in the current monthly folder
            daily_files.extend(
                list(monthly_folder.glob("**/*.nc"))
            )  # Change the pattern accordingly

        pathlist = sorted(daily_files)
        x, y = "longitude", "latitude"

    date_range = pd.date_range(str(pathlist[0])[-13:-5], str(pathlist[-1])[-13:-5])
    pathlist = pathlist[
        int(np.where(date_range == start)[0][0]) : int(
            np.where(date_range == stop)[0][0]
        )
        + 1
    ]

    return pathlist, x, y


# def hour_qunt(x):
#     """
#     function groups time to hourly and solves hourly mean

#     """
#     return x.groupby("time.hour").max(dim="time", engine='flox',method='cohorts', skipna = False)


def hour_qunt(x):
    """
    function groups time to hourly and solves hourly mean

    """
    # x = rechunk(x)
    x = x.chunk({"time": -1})
    return x.groupby("time.hour").quantile(
        [0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1],
        dim="time",
        skipna=False,
    )


def open_ds(path, var, x, y):
    ds = (
        xr.open_dataset(path)[var]
        .drop(["XLAT", "XLONG"])
        .chunk(chunks={y: 237, x: 517})
    )
    ds["time"] = ds["Time"]
    ds = ds.drop(["Time"])
    return ds


def concat_ds(pathlist, var, x, y):
    return (
        xr.concat(
            [open_ds(path, var, x, y) for path in pathlist],
            dim="time",
        )
        .to_dataset()
        .convert_calendar("noleap")
    )


def slice_ds(ds_full, i, j, di, dj):
    ii = i + 1
    jj = j + 1
    slicing = datetime.now()
    print("Start Slicing: ", slicing)
    try:
        ds = ds_full.isel(
            latitude=slice(j * dj, jj * dj), longitude=slice(i * di, ii * di)
        ).copy(deep=True)
    except:
        ds = ds_full.isel(
            south_north=slice(j * dj, jj * dj), west_east=slice(i * di, ii * di)
        ).copy(deep=True)
    print("Slicing Time: ", datetime.now() - slicing)
    return ds


# ds = xr.open_dataset(str(pathlist[0][0]))['S'].isel(time = 0).drop(['XLAT', 'XLONG', 'Time'])
# ds_slice = xr.open_zarr(str(save_dir) + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i0j0.zarr")
# dayofyear = ds_slice['dayofyear'].values
# hour = ds_slice['hour'].values
# south_north = ds['south_north'].values
# west_east = ds['west_east'].values
# da = xr.DataArray(
#     data=np.full((len(dayofyear), len(hour), len(south_north), len(west_east)), np.nan),
#     name = var,
#     dims=["dayofyear", "hour", "south_north", "west_east"],
#     coords=dict(
#         south_north = south_north,
#         west_east = west_east,
#         dayofyear = dayofyear,
#         hour=hour,
#     )
# )
# # (24, 711, 1551)
# # (24, 711/3, 1551/3) = (24, 237, 517)
# # (24, 711/9, 1551/11) = (24, 79, 141)
# file_names = []
# di, dj = 517, 237
# for i in range(0,3):
#     ii = i +1
#     for j in range(0,3):
#         jj = j+1
#         try:
#             ds_slice = xr.open_zarr(str(save_dir) + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.zarr")
#             da[:, :, j*dj: jj*dj, i*di: ii*di] = ds_slice['S']
#             file_names.append(str(save_dir) + f"/{var}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.zarr")
#         except:
#             pass

# da.isel(dayofyear=189, hour =0).plot()
