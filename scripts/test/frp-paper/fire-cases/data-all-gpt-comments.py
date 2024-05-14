#!/Users/crodell/miniconda3/envs/fwx/bin/python
"""
This script creates a Zarr file for each individual fire that occurred over North America on user-defined dates.
It extracts a subdomain around each fire, including various variables (features) to be used in training and testing
a machine learning model aimed at predicting fire radiative power.
"""

# Importing necessary libraries
import json
import context
import salem
import dask
import zarr
import os
import gc
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from context import root_dir, data_dir
from utils.rave import RAVE
from utils.fwx import FWX
from utils.viirs import VIIRS
from utils.firep import FIREP
from utils.frp import set_axis_postion
from scipy import stats
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.dates import DateFormatter
from matplotlib.colors import LinearSegmentedColormap

import matplotlib.dates as mdates
import cartopy.crs as ccrs

from dask.distributed import LocalCluster, Client

import warnings

# Suppress runtime warnings to clean up output
warnings.filterwarnings("ignore", category=RuntimeWarning)

years = ["2021", "2022"]


def tranform_ds(ds, rave_roi, fire_i, margin):
    """
    Apply spatial transformation and ROI subset to the dataset.

    Parameters:
        ds (xarray.Dataset): Dataset to transform.
        rave_roi (xarray.Dataset): RAVE dataset defining the region of interest.
        fire_i (xarray.DataArray): Data array for the specific fire instance.
        margin (int): Margin size for subset.

    Returns:
        xarray.Dataset: Transformed and subsetted dataset.
    """
    # Subset the dataset using Salem with a specified margin
    ds = ds.salem.subset(shape=fire_i, margin=margin, all_touched=True)
    # Apply a linear interpolation spatial transformation
    ds = rave_roi.salem.transform(ds, interp="linear")
    # Redefine the region of interest on the transformed dataset
    ds = ds.salem.roi(shape=fire_i, all_touched=True)
    # Try to drop the 'Time' variable if it exists
    try:
        ds = ds.drop_vars("Time")
    except:
        pass
    return ds


def re_index_ds(ds, rave_roi):
    """
    Re-index the dataset's time dimension to match the RAVE ROI dataset.

    Parameters:
        ds (xarray.Dataset): Dataset to re-index.
        rave_roi (xarray.Dataset): RAVE dataset with the correct time dimension.

    Returns:
        xarray.Dataset: Dataset with adjusted time dimension.
    """
    # Convert dataset time values to pandas Series
    ds_date_range = pd.Series(ds.time.values)
    date_range_list = []
    # Modify the date range to include an additional day for the last entry
    for doi in ds_date_range:
        if doi != ds_date_range.iloc[-1]:
            date_range_list.append(doi)
        else:
            date_range_list.append(doi + pd.Timedelta(days=1))
    # Update the 'time' coordinate with the new date range
    ds.coords["time"] = pd.Series(date_range_list)
    # Reindex the dataset's time dimension to match the RAVE ROI dataset, filling forward
    return ds.reindex(time=rave_roi.time, method="ffill")


def add_index(ds, rave_roi):
    """
    Add a new time dimension and reindex the dataset.

    Parameters:
        ds (xarray.Dataset): Dataset to modify.
        rave_roi (xarray.Dataset): RAVE dataset providing the new time dimension values.

    Returns:
        xarray.Dataset: Dataset with a new and aligned time dimension.
    """
    # Expand dataset dimensions to include 'time'
    ds = ds.expand_dims("time")
    # Set the 'time' coordinate using the first time value from the RAVE dataset
    ds.coords["time"] = pd.Series(rave_roi.time.values[0])
    # Reindex the dataset's time dimension to match the RAVE dataset, filling forward
    return ds.reindex(time=rave_roi.time, method="ffill")


def create_case_ds(config, fire_i, file_dir):
    """
    Creates and processes datasets for a specific fire case, then writes the result to a Zarr file.

    Parameters:
        config (dict): Configuration dictionary for setting up models and defining parameters.
        fire_i (DataFrame): Data for the specific fire instance being processed.
        file_dir (str): Directory path where the Zarr file will be saved.
    """
    # Record the start time of processing this specific fire case
    FIREloopTime = datetime.now()
    # Retrieve the fire ID from the fire instance data
    fire_ID = fire_i["id"].values[0]
    print(f"Start {fire_ID}")
    # Update the configuration with date range and fire instance data for processing
    config.update(
        date_range=[
            fire_i["initialdat"].to_list()[0],
            fire_i["finaldate"].to_list()[0],
        ],
        fire_i=fire_i,
    )
    # Logging to track progress within the batch process
    print(f"{i}/{file_len}")

    try:
        # Initialize models and open datasets
        rave = RAVE(config=config)
        rave_ds = rave.open_rave(var_list=["FRP_MEAN", "PM25"])
        fwx = FWX(config=config)
        fwx_ds = fwx.open_fwx()
        viirs = VIIRS(config=config)
        ndvi_ds = viirs.open_ndvi()
        lai_ds = viirs.open_lai()

        # Subset the datasets for the region of interest (ROI) and compute the result
        rave_roi = rave_ds.salem.subset(shape=fire_i, margin=1, all_touched=True)
        rave_roi = rave_roi.salem.roi(shape=fire_i, all_touched=True).compute()

        # Check if there are any valid FRP values
        if np.all(np.isnan(rave_roi["FRP_MEAN"].values)):
            print(f"NO FRP FOR: {fire_ID}")
        else:
            print(f"HAS FRP FOR: {fire_ID}")
            # Transform the datasets to align with the ROI and apply indices
            fwx_roi = tranform_ds(fwx_ds, rave_roi, fire_i, margin=2)
            ndvi_roi = re_index_ds(
                tranform_ds(ndvi_ds["NDVI"], rave_roi, fire_i, margin=10), rave_roi
            )
            lai_roi = re_index_ds(
                tranform_ds(lai_ds["LAI"], rave_roi, fire_i, margin=20), rave_roi
            )

            # Apply conditional transformations to ensure data values are within expected ranges
            lai_roi = xr.where(lai_roi < 0, 0, lai_roi)
            ndvi_roi = xr.where(ndvi_roi < -1, -1, ndvi_roi)
            ndvi_roi = xr.where(ndvi_roi > 1, 1, ndvi_roi)

            # Rename variables for clarity
            rave_roi = xr.where(rave_roi == 0, np.nan, rave_roi).rename(
                {"FRP_MEAN": "FRP"}
            )

            # Identify the first valid index for time slicing
            first_valid_index = (
                rave_roi["FRP"]
                .notnull()
                .any(dim=[dim for dim in rave_roi["FRP"].dims if dim != "time"])
                .argmax("time")
            )

            # Compile final dataset including all variables and conditions
            final_ds = fwx_roi
            final_ds["NDVI"] = ndvi_roi.rename("NDVI")
            final_ds["LAI"] = lai_roi.rename("LAI")
            for var in rave_roi:
                final_ds[var] = rave_roi[var]

            # Slice the dataset from the first valid index to ensure no leading empty slices
            final_ds = final_ds.isel(time=slice(first_valid_index.values, None))
            # Set attributes for metadata
            final_ds.attrs = {
                "area_ha": str(fire_i["area_ha"].values[0]),
                "initialdat": str(fire_i["initialdat"].values[0]),
                "finaldate": str(fire_i["finaldate"].values[0]),
                "id": str(fire_i["id"].values[0]),
                "min_x": str(fire_i["min_x"].values[0]),
                "min_y": str(fire_i["min_y"].values[0]),
                "max_x": str(fire_i["max_x"].values[0]),
                "max_y": str(fire_i["max_y"].values[0]),
            }
            # Clean up directory before writing new file
            bashComand = "rm -rf " + file_dir
            os.system(bashComand)
            bashComand = "rm -rf /Volumes/WFRT-Ext23/fire/all/._*"
            os.system(bashComand)
            # Define compressor for efficient storage
            zarr_compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
            encoding = {x: {"compressor": zarr_compressor} for x in final_ds}
            print(f"WRITING AT: {datetime.now()}")
            # Write processed data to Zarr file
            final_ds.to_zarr(file_dir, encoding=encoding, mode="w")
            print(f"Wrote: {file_dir}")

            # Cleanup to free memory
            del (
                rave,
                fwx,
                viirs,
                rave_ds,
                fwx_ds,
                ndvi_ds,
                lai_ds,
                rave_roi,
                fwx_roi,
                lai_roi,
                ndvi_roi,
                final_ds,
                fire_i,
            )
            gc.collect()
            print(f"FIRE {fire_ID} run time: {datetime.now() - FIREloopTime}")

    except Exception as e:
        # Handle exceptions and log errors
        raise ValueError("An error occurred: " + str(e))
    return


# Main script execution starts here
# Open static dataset
static_ds = salem.open_xr_dataset(str(data_dir) + "/static/static-rave-3km.nc")

# Loop through specified years
for year in years:
    # Configuration dictionary for the RAVE and FWX models
    config = dict(
        model="wrf",
        trail_name="01",
        method="hourly",
        year=year,
    )
    # Initialize FIREP data model with configuration
    firep = FIREP(config=config)
    # Open FIREP dataset
    firep_df = firep.open_firep()
    # Get length of the fire dataset
    file_len = len(firep_df)
    # Process each fire instance
    for i in range(file_len):
        fire_i = firep_df.iloc[i : i + 1]
        # Define file directory for the Zarr file
        file_dir = (
            "/Volumes/WFRT-Ext23/fire/all/"
            + year
            + "-"
            + str(fire_i["id"].values[0])
            + ".zarr"
        )
        # Check if the directory exists
        if os.path.isdir(file_dir) == True:
            print("TESTING FILE")
            try:
                ds = xr.open_zarr(file_dir)
                if (
                    (np.all(np.isnan(ds["NDVI"].values)) == False)
                    | (np.all(np.isnan(ds["LAI"].values)) == False)
                    | (np.all(np.isnan(ds["FRP"].values)) == False)
                ):
                    print(
                        year
                        + "-"
                        + str(fire_i["id"].values[0])
                        + ".zarr"
                        + " Is a valid file"
                    )
                else:
                    print("FAILED FILE TEST")
                    create_case_ds(config, fire_i, file_dir)
            except:
                print("FILE IS BAD CREATE IT")
                # Remove and recreate corrupted or incomplete Zarr file
                # bashComand = "rm -rf " + file_dir
                # os.system(bashComand)
                bashComand = "rm -rf /Volumes/WFRT-Ext23/fire/all/._*"
                os.system(bashComand)
                create_case_ds(config, fire_i, file_dir)
        else:
            print("NO FILE WILL CREATE IT")
            create_case_ds(config, fire_i, file_dir)
