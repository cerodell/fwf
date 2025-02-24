#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from utils.ml_data import MLDATA


from datetime import datetime
from context import data_dir

from netCDF4 import Dataset
import plotly.express as px


# Mark the start time for the run
startTime = datetime.now()


all_fire = True
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v19"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
persist = True

df = pd.read_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/avg-averaged-{method[-3:]}-persist-{persist}.csv"
)


df["r2_sum_diff"] = df["r2_avg_mlp"] - df["r2_avg_pers"]

fig = px.scatter_mapbox(
    df,
    lat="lats",
    lon="lons",
    color="r2_sum_diff",
    # size=f"elev_bias_abs",
    color_continuous_scale="RdBu",
    hover_name="ids",
    center={"lat": 59.0, "lon": -120.0},
    hover_data=["r2_avg_mlp", "r2_avg_pers"],
    mapbox_style="carto-positron",
    range_color=[-1, 1],
    zoom=1,
    # labels={"colorbar": '2m Temperature Bias'}
)
fig.layout.coloraxis.colorbar.title = "Bias"

fig.show()
