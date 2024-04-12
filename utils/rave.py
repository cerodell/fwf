#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from sklearn.neighbors import KDTree

from context import data_dir


class RAVE:
    """
    A class to represent a RAVE analysis tool.

    This class provides methods to preprocess and analyze RAVE dataset
    including reading data, generating grids, and manipulating datasets.

    Attributes
    ----------
    file_list : list
        A list of file paths for RAVE datasets within the specified date range.
    grid_ds : xarray.Dataset
        The static grid dataset used for RAVE data alignment and analysis.

    Methods
    -------
    __init__(config)
        Initializes the RAVE object with a configuration for date range and data processing.
    get_timestamp_vars(file_name)
        Extracts timestamp variables from the file name.
    rave_grid(ds)
        Generates a grid dataset based on the RAVE dataset spatial characteristics.
    mod_ds(filein)
        Modifies the dataset for analysis, applying spatial and temporal selections.
    open_rave()
        Opens multiple RAVE datasets and combines them into a single dataset.
    make_KDtree()
        Builds a KDTree for efficient spatial queries.
    """

    def __init__(self, config):
        """
        Initialize the RAVE object with specified configurations.

        Parameters
        ----------
        config : dict
            A dictionary with configuration settings, including the date range for data analysis.
        """
        # Creating a date range from configuration settings
        date_range = pd.date_range(
            config["date_range"][0], config["date_range"][-1], freq="h"
        )
        years = date_range.strftime("%Y").unique().tolist()
        months = date_range.strftime("%m").unique().tolist()

        file_list = []
        # Generating file list within the date range from the specified directory
        for year in years:
            for month in months:
                int_list = sorted(
                    Path(f"/Volumes/WFRT-Ext24/rave/{year}/{month}/").glob(
                        f"RAVE-HrlyEmiss*"
                    ),
                    key=self.get_timestamp_vars,
                )
                file_list.append([str(filein) for filein in int_list])

        file_list = [item for sublist in file_list for item in sublist]

        # Extracting times of interest based on the file list and the specified date range
        toi = pd.to_datetime(
            [self.get_timestamp_vars(file_list[i])[:8] for i in range(len(file_list))]
        )
        self.file_list = file_list[
            np.where(toi == date_range[0])[0][0] : np.where(toi == date_range[-1])[0][0]
            + 1
        ]

        # Try to open a static grid dataset, or generating one if it fails
        try:
            self.grid_ds = salem.open_xr_dataset(
                str(data_dir) + "/static/static-rave-3km-grid.nc"
            )
        except:
            self.grid_ds = self.rave_grid(xr.open_dataset(self.file_list[0]))

    def get_timestamp_vars(self, file_name):
        """
        Extracts timestamp variables from the file name.

        Parameters
        ----------
        file_name : str
            The name of the file from which to extract timestamp variables.

        Returns
        -------
        str
            A string containing the extracted timestamp variables.
        """
        return str(file_name).split("/")[-1].split("_s")[-1].split("_")[0]

    def rave_grid(self, ds):
        """
        Generates a grid dataset based on the RAVE dataset spatial characteristics.

        Parameters
        ----------
        ds : xarray.Dataset
            The RAVE dataset from which to derive spatial characteristics.

        Returns
        -------
        xarray.Dataset
            A grid dataset matching the RAVE dataset's spatial configuration.
        """
        grid_ds = salem.Grid(
            nxny=(len(ds["grid_xt"]), len(ds["grid_yt"])),
            dxdy=(
                ds.attrs["geospatial_lon_resolution"],
                ds.attrs["geospatial_lat_resolution"],
            ),
            x0y0=(
                ds.attrs["geospatial_lon_min"] - 360,
                ds.attrs["geospatial_lat_min"],
            ),
            proj=salem.wgs84,
        ).to_dataset()

        grid_ds.to_netcdf(str(data_dir) + "/static/static-rave-3km.nc")

        return grid_ds

    def get_ds(self, filein):
        """
        Modifies the dataset for analysis, applying spatial and temporal selections.

        Parameters
        ----------
        filein : str
            Path to the RAVE dataset file to be opened and modified.

        Returns
        -------
        xarray.Dataset
            The modified dataset, ready for further analysis.
        """
        rave_ds = xr.open_dataset(
            filein, chunks="auto"
        )  # Open the dataset with automatic chunking for dask
        ds = self.grid_ds.assign_coords(
            {"time": rave_ds.time.values}
        )  # Assign time coordinates from the RAVE dataset to the grid
        # Apply spatial selections and calculations to the dataset
        rave_ds = xr.where(rave_ds["QA"] != 3, rave_ds, np.nan)
        for var in list(ds):
            ds[var] = (
                ("time", "y", "x"),
                dask.array.nan_to_num(rave_ds[var].data[:, ::-1]),
            )  # Invert and fill NaN values
            ds[var].attrs = ds.attrs  # Copy attributes
        ds = ds.sel(
            x=slice(-180, -27), y=slice(20, 75)
        )  # Select a specific spatial region
        return ds

    def mod_ds(self, filein, var_list):
        """
        Modifies the dataset for analysis, applying spatial and temporal selections.

        Parameters
        ----------
        filein : str
            Path to the RAVE dataset file to be opened and modified.

        Returns
        -------
        xarray.Dataset
            The modified dataset, ready for further analysis.
        """
        rave_ds = xr.open_dataset(
            filein, chunks="auto"
        )  # Open the dataset with automatic chunking for dask
        ds = self.grid_ds.assign_coords(
            {"time": rave_ds.time.values}
        )  # Assign time coordinates from the RAVE dataset to the grid
        # Apply spatial selections and calculations to the dataset
        ds_vars = xr.where(rave_ds["QA"] != 3, rave_ds, np.nan)
        ds_vars = ds_vars[var_list]
        for var in var_list:
            ds[var] = (
                ("time", "y", "x"),
                dask.array.nan_to_num(ds_vars[var].data[:, ::-1]),
            )  # Invert and fill NaN values
            ds[var].attrs = ds.attrs  # Copy attributes
        ds.attrs = ds.attrs  # Copy attributes
        ds = ds.sel(
            x=slice(-180, -27), y=slice(20, 75)
        )  # Select a specific spatial region
        return ds

    def open_rave(self, var_list=None):
        """
        Opens multiple RAVE datasets and combines them into a single dataset.

        Returns
        -------
        xarray.Dataset
            A single dataset combined from multiple RAVE datasets.
        """
        # Combine datasets along the time dimension, dropping conflicting attributes
        if var_list is None:
            ds = xr.combine_nested(
                [self.get_ds(filein) for filein in self.file_list],
                concat_dim="time",
                combine_attrs="drop_conflicts",
            )
        else:
            ds = xr.combine_nested(
                [self.mod_ds(filein, var_list) for filein in self.file_list],
                concat_dim="time",
                combine_attrs="drop_conflicts",
            )
        return ds

    def make_KDtree(self):
        """
        Builds a KDTree for efficient spatial queries.

        Returns
        -------
        tuple of ndarray
            The 2D array indices for spatial queries.
        """
        # Get longitude and latitude coordinates from the grid dataset
        XLONG, XLAT = self.grid_ds.salem.grid.ll_coordinates
        shape = XLAT.shape
        # Flatten the coordinates for KDTree construction
        locs = pd.DataFrame({"lats": XLAT.values.ravel(), "lons": XLONG.values.ravel()})
        # Build the KDTree
        fwf_tree = KDTree(locs)
        print("Fire KDTree built")
        yy, xx = [], []  # Initialize lists for indices

        # Define search area
        df = pd.DataFrame(
            {"lat": [self.min_lat, self.max_lat], "lon": [self.min_lon, self.max_lon]}
        )
        for index, row in df.iterrows():
            single_loc = np.array([row.lat, row.lon]).reshape(
                1, -1
            )  # Format location for KDTree query
            dist, ind = fwf_tree.query(single_loc, k=1)  # Perform query
            if dist > 0.1:
                pass  # Ignore if the nearest point is more than 0.1 degrees away
            else:
                ind_2d = np.unravel_index(int(ind), shape)  # Convert 1D index to 2D
                yy.append(ind_2d[0])  # Append row index
                xx.append(ind_2d[1])  # Append column index
        yy, xx = np.array(yy), np.array(xx)  # Convert lists to arrays

        return yy, xx
