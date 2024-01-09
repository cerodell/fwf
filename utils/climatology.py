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

    date_range = pd.date_range(str(pathlist[0])[-13:-5], str(pathlist[-1])[-13:-5])
    pathlist = pathlist[
        int(np.where(date_range == start)[0][0]) : int(
            np.where(date_range == stop)[0][0]
        )
        + 1
    ]

    return pathlist


def hour_qunt(x):
    """
    function groups time to hourly and solves hourly mean

    """
    x = x.chunk({"time": -1})
    # x = rechunk(x)
    return x.groupby("time.hour", allow_rechunk=True).quantile(
        [0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0], dim="time"
    )


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    return ds


def open_ds(path, var):
    ds = xr.open_dataset(path, chunks="auto")[var].drop(["XLAT", "XLONG"])
    ds["time"] = ds["Time"]
    ds = ds.drop(["Time"])
    return ds


# def concat_ds(pathlist, var):
#     return xr.concat([xr.open_dataset(path, chunks="auto")[var].drop(["XLAT", "XLONG"])for path in pathlist],dim="time",).to_dataset()


def concat_ds(pathlist, var):
    return xr.combine_nested(
        [open_ds(path, var) for path in pathlist],
        "time",
    ).to_dataset()
