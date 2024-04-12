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
import plotly.express as px

from context import root_dir, data_dir


class FIREP:
    def __init__(self, config):
        # Read in the shapefile for fire data and process it

        self.gdf_all = salem.read_shapefile(
            str(data_dir)
            + f'/fires/North_America/North_America_vs2_{config["year"]}.shp'
        )

        return

    def open_firep(self):
        gdf_all = self.gdf_all
        gdf_all["datetime"] = pd.to_datetime(
            gdf_all["initialdat"]
        )  # Convert initialdat to datetime format
        # Filter the dataframe for dates starting in April and area greater than 200 hectares
        gdf_all = gdf_all[
            (gdf_all["datetime"].dt.month >= 4) & (gdf_all["area_ha"] >= 200)
        ]
        # gdf_all = gdf_all[gdf_all['area_ha'] >= 200]
        del gdf_all["datetime"]  # Remove the temporary datetime column
        gdf_all = gdf_all.reset_index(
            drop=True
        )  # Reset the index and remove the old index column
        return gdf_all
