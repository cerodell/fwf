#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import context
import salem
import dask
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
from context import data_dir


class VIIRS:
    def __init__(self, config):
        self.file_list = self.file_finder(
            config
        )  # Initializes the file list based on the configuration
        return

    def file_finder(self, config):
        self.date_range = pd.date_range(
            config["date_range"][0], config["date_range"][-1], freq="h"
        )
        return (
            f'/Volumes/WFRT-Ext23/satilite/viirs/{self.date_range[0].strftime("%Y")}/'
        )

    def open_ndvi(self):
        return self.mod_ds(
            salem.open_xr_dataset(str(self.file_list) + "VNP13A2.001_1km_aid0001.nc")
        ).rename({"_1_km_16_days_NDVI": "NDVI"})

    def open_lai(self):
        return self.mod_ds(
            salem.open_xr_dataset(str(self.file_list) + "VNP15A2H.001_500m_aid0001.nc")
        ).rename({"Lai": "LAI"})

    def mod_ds(self, ds):
        timestamps_series = pd.Series(
            [
                pd.Timestamp(
                    datetime(
                        cftime_obj.year,
                        cftime_obj.month,
                        cftime_obj.day,
                        cftime_obj.hour,
                        cftime_obj.minute,
                        cftime_obj.second,
                        int(cftime_obj.microsecond),
                    )
                )
                for cftime_obj in ds.time.values
            ]
        )
        ds.coords["time"] = timestamps_series

        # Find the nearest time in the past
        start_nearest = timestamps_series[
            timestamps_series <= pd.Timestamp(self.date_range[0])
        ].max()
        stop_nearest = timestamps_series[
            timestamps_series >= pd.Timestamp(self.date_range[-1])
        ].min()
        return ds.sel(
            time=slice(
                start_nearest.strftime("%Y-%m-%d"), stop_nearest.strftime("%Y-%m-%d")
            )
        )
