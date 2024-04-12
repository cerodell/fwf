#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from context import data_dir


class FWX:
    """
    A class to handle FWX (Fire Weather Index) data processing.

    This class includes methods for finding relevant files within a specified date range and model configuration,
    extracting data, and modifying datasets for analysis.

    Attributes
    ----------
    file_list : list
        A list of file paths for FWX datasets that fall within the specified date range.

    Methods
    -------
    __init__(config)
        Constructor for the FWX class that initializes file list based on the configuration.
    get_timestamp_vars(file_name)
        Extracts timestamp variables from the file name.
    file_finder(config)
        Finds and returns a list of FWX dataset files based on the provided configuration.
    get_ds(filein)
        Opens a dataset file and selects the first 24 time steps.
    mod_ds(filein, var_list)
        Opens a dataset file, selects specified variables, and restricts to the first 24 time steps.
    open_fwx(var_list=None)
        Combines multiple FWX datasets into a single dataset, optionally filtering by variables.
    """

    def __init__(self, config):
        """
        Initializes the FWX object with file paths based on the configuration.

        Parameters
        ----------
        config : dict
            Configuration dictionary specifying the date range, model, domain, trail name, and method.
        """
        self.file_list = self.file_finder(
            config
        )  # Initializes the file list based on the configuration

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
        return str(file_name).split("/")[-1].split("-")[-1][:-5]

    def file_finder(self, config):
        """
        Finds and returns a list of FWX dataset files based on the provided configuration.

        Parameters
        ----------
        config : dict
            Configuration dictionary specifying the date range, model, domain, trail name, and method.

        Returns
        -------
        list
            A list of sorted file paths that fall within the specified date range.
        """
        self.date_range = pd.date_range(
            config["date_range"][0], config["date_range"][-1], freq="h"
        )
        years = self.date_range.strftime("%Y").unique().tolist()
        months = self.date_range.strftime("%m").unique().tolist()
        model = config["model"]
        try:
            domain = config["domain"]
        except:
            domain = self.within_domain(config["fire_i"])
        trail_name = config["trail_name"]
        method = config["method"]
        file_list = sorted(
            Path(f"/Volumes/WFRT-Ext24/fwf-data/{model}/{domain}/{trail_name}/").glob(
                f"fwf-{method}*"
            ),
            key=self.get_timestamp_vars,
        )

        toi = pd.to_datetime(
            [self.get_timestamp_vars(file_list[i]) for i in range(len(file_list))]
        )
        return file_list[
            np.where(toi == self.date_range[0] - pd.Timedelta(days=1))[0][0] : np.where(
                toi == self.date_range[-1]
            )[0][0]
            + 1
        ]

    def within_domain(self, fire_i):
        static_d02 = salem.open_xr_dataset(
            str(data_dir) + "/static/static-vars-wrf-d02.nc"
        )
        static_d03 = salem.open_xr_dataset(
            str(data_dir) + "/static/static-vars-wrf-d03.nc"
        )
        try:
            static_d03["HGT"].salem.subset(shape=fire_i, margin=20, all_touched=True)
            domain = "d03"
        except:
            try:
                static_d02["HGT"].salem.subset(
                    shape=fire_i, margin=20, all_touched=True
                )
                domain = "d02"
            except:
                pass
        print(domain)
        return domain

    def get_ds(self, filein):
        """
        Opens a dataset file and selects the first 24 time steps.

        Parameters
        ----------
        filein : str
            Path to the FWX dataset file to be opened.

        Returns
        -------
        xarray.Dataset
            The dataset with only the first 24 time steps selected.
        """
        ds = xr.open_dataset(filein, chunks="auto").isel(time=slice(0, 24))
        return ds

    def mod_ds(self, filein, var_list):
        """
        Opens a dataset file, selects specified variables, and restricts to the first 24 time steps.

        Parameters
        ----------
        filein : str
            Path to the FWX dataset file to be opened.
        var_list : list of str
            List of variable names to be selected from the dataset.

        Returns
        -------
        xarray.Dataset
            The dataset with specified variables and only the first 24 time steps selected.
        """
        ds = xr.open_dataset(filein, chunks="auto")[var_list].isel(time=slice(0, 24))
        return ds

    def open_fwx(self, var_list=None):
        """
        Combines multiple FWX datasets into a single dataset, optionally filtering by variables.

        Parameters
        ----------
        var_list : list of str, optional
            List of variable names to filter the datasets by. If None, all variables are included.

        Returns
        -------
        xarray.Dataset
            A single dataset combined from multiple FWX datasets, with variables optionally filtered.
        """
        if var_list is None:
            ds = xr.combine_nested(
                [self.get_ds(filein) for filein in self.file_list],
                concat_dim="time",
                combine_attrs="drop_conflicts",
            )
            # Copying projection information to all variables after combining
            for var in list(ds):
                ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
        else:
            # Combining datasets after selecting specified variables and copying projection information
            ds = xr.combine_nested(
                [self.mod_ds(filein, var_list) for filein in self.file_list],
                concat_dim="time",
                combine_attrs="drop_conflicts",
            )
            for var in list(ds):
                ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]
        return ds.sel(
            time=slice(self.date_range[0], self.date_range[-1] + pd.Timedelta(hours=23))
        )
