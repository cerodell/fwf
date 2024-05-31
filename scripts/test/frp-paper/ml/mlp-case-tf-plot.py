#!/Users/crodell/miniconda3/envs/fwx/bin/python

import json
import os
import context
import salem
import dask
import joblib
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime


from utils.ml_data import MLDATA
from utils.firep import FIREP
from utils.plot_fire_case import plot_fire, drop_outside_std
from utils.solar_hour import get_solar_hours
from utils.compressor import compressor
import matplotlib.dates as mdates

from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from context import root_dir, data_dir

import warnings

# Suppress future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=RuntimeWarning)

import numpy as np


ID = 26415153  # 25407482 (2022) 25485086 (2022) 24448308 (2021) 24360611 (2021) 24450415 (2021) 26695902 (2023)
year = "2023"
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v2"
ml_pack = "tf"
plot_method = "mean"
persist = False
dt = 6

model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{mlp_test_case}/"
save_dir = model_dir
with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)

# fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
# ids = fire_cases[0].astype(int)
# years = fire_cases[1].astype(int)
config["year"] = year
firep = FIREP(config=config)
firep_df = firep.open_firep()
jj = firep_df[firep_df["id"] == ID].index[0]
fire_i = firep_df.iloc[jj : jj + 1]

# %%
ds = xr.open_dataset(f'/Volumes/ThunderBay/CRodell/fires/v2/{config["year"]}-{ID}.nc')


ds["MODELED_FRP"] = xr.where(ds["FRP"] == 0, 0, ds["MODELED_FRP"])

plot_fire(fire_i, ds, persist, dt, save_dir, "mean")
