#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import numpy as np
import xarray as xr
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from datetime import datetime
from utils.ml_data import MLDATA

from context import data_dir, root_dir

# Mark the start time for the run
startTime = datetime.now()

# Configuration parameters
keep_vars = ["FRP", "HFI", "S", "ISI", "W", "H", "T"]
scaler_type = "robust"  ##robust or standard or minmax


# Initialize MLP model and load dataset
mlD = MLDATA(config={"method": f"averaged"})
df = mlD.open_ml_ds()

X = df[keep_vars]
X = X.loc[X["HFI"] > 100]
X = X.loc[X["FRP"] < 4000]

# X_copy = X.copy()
sns.pairplot(X, diag_kind="kde")


X["HFI"] = np.log1p(X["HFI"])
X["FRP"] = np.log1p(X["FRP"])
X["S"] = np.log1p(X["S"])
X["ISI"] = np.log1p(X["ISI"])
X["W"] = np.log1p(X["W"])

sns.pairplot(X, diag_kind="kde")

# Scale features
if scaler_type == "standard":
    scaler = StandardScaler().fit(X)
elif scaler_type == "robust":
    scaler = RobustScaler().fit(X)
elif scaler_type == "minmax":
    scaler = MinMaxScaler().fit(X)

X_scaled = scaler.transform(X)
X_copy["HFI"] = X_scaled[:, 0]
X_copy["NDVI"] = X_scaled[:, 1]
X_copy["LAI"] = X_scaled[:, 2]
X_copy["FRP"] = X_scaled[:, 3]

sns.pairplot(X_copy, diag_kind="kde")
