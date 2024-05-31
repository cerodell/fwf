#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import os
import json
import joblib
import logging
import simplekml
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon

import matplotlib.pyplot as plt
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from datetime import datetime
from utils.ml_data import MLDATA
from utils.firep import FIREP

from context import data_dir
import warnings

warnings.simplefilter(action="ignore", category=UserWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


# # Function to reduce precision of coordinates
# def reduce_precision(coords, precision=2):
#     return [(round(x, precision), round(y, precision)) for x, y in coords]


sum_list = []
avg_list = []
save_dir = "/Users/crodell/fwf/scripts/test/frp-paper/fire-cases/web/data"
# Initialize MLP model and load dataset
mlD = MLDATA(config={"method": "averaged-v2-nans"})
cases_df = mlD.open_ml_ds()
for year in ["2021", "2022", "2023"]:
    firep = FIREP(config={"year": year})
    firep_df = firep.open_firep()

    for ID, group in cases_df.groupby("id"):
        ID = int(ID)
        id_df = firep_df.loc[firep_df["id"] == int(ID)]
        if len(id_df) == 0:
            print("No ID")
        else:
            if os.path.exists(f"/Volumes/ThunderBay/CRodell/fires/v2/{year}-{ID}.nc"):
                ds = xr.open_dataset(
                    f"/Volumes/ThunderBay/CRodell/fires/v2/{year}-{ID}.nc"
                )
                MAX_MODELED_FRP = float(ds["MODELED_FRP"].max())
                MAX_FRP = float(ds["FRP"].max())
                print(MAX_MODELED_FRP)
                ds_nan = xr.open_zarr(
                    f"/Volumes/WFRT-Ext23/fire/full/{year}-{ID}.zarr"
                )["FRP"].to_dataset()
                ds = xr.where(np.isnan(ds_nan["FRP"].values) == True, np.nan, ds)
                ds = ds.salem.roi(shape=id_df, all_touched=True)
                ds_space_avg = ds.mean(dim=("x", "y"))
                ds_space_sum = ds.sum(dim=("x", "y"))
                ds_space_sum = xr.where(
                    np.isnan(ds_space_avg["FRP"].values) == True, np.nan, ds_space_sum
                )

                df_space_avg = ds_space_avg.to_dataframe()
                df_space_avg["id"] = np.full_like(df_space_avg["FRP"], ID)
                df_space_avg["area_ha"] = np.full_like(
                    df_space_avg["FRP"], id_df["area_ha"]
                )
                df_space_avg["finaldate"] = np.full_like(
                    df_space_avg["FRP"], id_df["finaldate"], dtype=str
                )
                df_space_avg["initialdat"] = np.full_like(
                    df_space_avg["FRP"], id_df["initialdat"], dtype=str
                )
                df_space_avg["lat"] = np.full_like(
                    df_space_avg["FRP"],
                    np.round(np.mean([id_df["min_y"], id_df["max_y"]]), 2),
                )
                df_space_avg["lon"] = np.full_like(
                    df_space_avg["FRP"],
                    np.round(np.mean([id_df["min_x"], id_df["max_x"]]), 2),
                )
                df_space_avg["MAX_MODELED_FRP"] = np.full_like(
                    df_space_avg["FRP"], MAX_MODELED_FRP
                )
                df_space_avg["MAX_MODELED_FRP"] = np.full_like(
                    df_space_avg["FRP"], MAX_FRP
                )

                avg_list.append(df_space_avg)

                df_space_sum = ds_space_sum.to_dataframe()
                df_space_sum["id"] = np.full_like(df_space_sum["FRP"], ID)
                df_space_sum["area_ha"] = np.full_like(
                    df_space_sum["FRP"], id_df["area_ha"]
                )
                df_space_sum["finaldate"] = np.full_like(
                    df_space_sum["FRP"], id_df["finaldate"], dtype=str
                )
                df_space_sum["initialdat"] = np.full_like(
                    df_space_sum["FRP"], id_df["initialdat"], dtype=str
                )
                df_space_sum["lat"] = np.full_like(
                    df_space_sum["FRP"],
                    np.round(np.mean([id_df["min_y"], id_df["max_y"]]), 2),
                )
                df_space_sum["lon"] = np.full_like(
                    df_space_sum["FRP"],
                    np.round(np.mean([id_df["min_x"], id_df["max_x"]]), 2),
                )
                df_space_sum["MAX_MODELED_FRP"] = np.full_like(
                    df_space_sum["FRP"], MAX_MODELED_FRP
                )
                df_space_avg["MAX_FRP"] = np.full_like(df_space_avg["FRP"], MAX_FRP)
                sum_list.append(df_space_sum)


sum_df = pd.concat(sum_list, ignore_index=True)
sum_df.to_csv(
    "/Users/crodell/fwf/data/ml-data/test-data/sum-averaged-v2.csv", index=False
)


avg_df = pd.concat(avg_list, ignore_index=True)
avg_df.to_csv(
    "/Users/crodell/fwf/data/ml-data/test-data/avg-averaged-v2.csv", index=False
)
