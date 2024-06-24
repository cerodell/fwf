#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import joblib
import random
import string
import itertools
import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import make_scorer, mean_squared_error

from sklearn.inspection import permutation_importance
from utils.sk import activate_logging, create_model_directory
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from utils.ml_data import MLDATA

from context import data_dir, root_dir
from joblib import parallel_backend

# Mark the start time for the run
startTime = datetime.now()
print(startTime)
# Configuration parameters
keep_vars = ["S", "HFI", "LAI", "NDVI", "hour_sin", "hour_cos"]
keep_vars = [
    "F",
    "FMC",
    "H",
    "HFI",
    "ISI",
    "LAI",
    "NDVI",
    "R",
    "ROS",
    "S",
    "SFC",
    "T",
    "TFC",
    "U",
    "W",
    "WD",
    "r_o_hourly",
    "HGT",
    "GS",
    "ASPECT_sin",
    "ASPECT_cos",
    "SAZ_sin",
    "SAZ_cos",
    "Live_Leaf",
    "Live_Wood",
    "Dead_Foliage",
    "Dead_Wood",
    "hour_sin",
    "hour_cos",
]

# Configuration parameters
config = dict(
    method="averaged-v5",
    years=["2021", "2022", "2023"],
    feature_vars=[
        # "R",
        # "U",
        # "S",
        # 'R-LAI-hour_sin',
        # 'R-LAI',
        # 'LAI',
        # 'R-NDVI-hour_sin',
        # 'R-NDVI',
        # 'NDVI',
        "SAZ_sin",
        "SAZ_cos",
        # "hour_cos",
        # "hour_sin",
        # "Live_Wood",
        # "Dead_Wood",
        # "Live_Leaf",
        # "Dead_Foliage",
        # "R-hour_sin",
        # "R-hour_cos",
        # "F-hour_sin",
        # "F-hour_cos",
        # "S-hour_sin",
        # "S-hour_cos",
        # "U-Live_Wood",
        # "U-Dead_Wood",
        # "U-Live_Leaf",
        # "U-Dead_Foliage",
        # "R-Live_Wood",
        # "R-Dead_Wood",
        # "R-Live_Leaf",
        # "R-Dead_Foliage",
        # "Total_Fuel_Load",
        "R-hour_sin-Total_Fuel_Load",
        "F-hour_cos-Total_Fuel_Load",
        # "U-lat_sin-Total_Fuel_Load",
        "U-lat_cos-Total_Fuel_Load",
        # "U-lon_sin-Total_Fuel_Load",
        "U-lon_cos-Total_Fuel_Load",
        # "R-hour_sin-Live_Wood",
        # "R-hour_cos-Live_Wood",
        # "R-hour_sin-Dead_Wood",
        # "R-hour_cos-Dead_Wood",
        # "R-hour_sin-Live_Leaf",
        # "R-hour_cos-Live_Leaf",
        # "R-hour_sin-Dead_Foliage",
        # "R-hour_cos-Dead_Foliage",
        # "U-lat_sin-Live_Wood",
        # "U-lat_cos-Live_Wood",
        # "U-lon_sin-Live_Wood",
        # "U-lon_cos-Live_Wood",
        # "U-lat_sin-Dead_Wood",
        # "U-lat_cos-Dead_Wood",
        # "U-lon_sin-Dead_Wood",
        # "U-lon_cos-Dead_Wood",
        # "U-lat_sin-Live_Leaf",
        # "U-lat_cos-Live_Leaf",
        # "U-lon_sin-Live_Leaf",
        # "U-lon_cos-Live_Leaf",
        # "U-lat_sin-Dead_Foliage",
        # "U-lat_cos-Dead_Foliage",
        # "U-lon_sin-Dead_Foliage",
        # "U-lon_cos-Dead_Foliage",
    ],
    target_vars=["FRP", "FRE"],
    feature_scaler_type="robust",  ##robust or standard minmax
    target_scaler_type=None,  ##robust or standard minmax
    transform=True,
    package="tf",
    model_type="MLP",
    main_cases=False,
    shuffle_data=True,
    feature_engineer=True,
    filter_std=True,
    min_fire_size=0,  ## hectors
)
config["n_features"] = len(config["feature_vars"])
config["n_targets"] = len(config["target_vars"])


# Define and compile RF model
model = RandomForestRegressor(verbose=True, n_estimators=100, random_state=42)

# Prepare directory to save model output
make_dir = Path(data_dir) / "rf/sk/"
make_dir.mkdir(parents=True, exist_ok=True)


# Initialize MLP model and load dataset
mlD = MLDATA(config=config)
df = mlD.open_ml_ds()

y = df["FRP"]
X = df[config["feature_vars"]]


# Prepare K-Fold cross-validation
kf = KFold(n_splits=5, shuffle=True, random_state=42)

feature_importances = np.zeros(X.shape[1])

for train_index, test_index in kf.split(X):
    trainTime = datetime.now()
    print("train time start: ", trainTime)
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    # Initialize and fit the scaler on the training data
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train the model on the scaled training data
    model.fit(X_train_scaled, y_train)
    # Accumulate feature importances
    feature_importances += model.feature_importances_
    print("Time to train: ", datetime.now() - trainTime)

# Average feature importances
feature_importances /= kf.get_n_splits()

# Display normalized feature importances
feature_names = X.columns
importances = pd.DataFrame(
    feature_importances, index=feature_names, columns=["importance"]
).sort_values("importance", ascending=False)


importances.to_csv(str(data_dir) + "/mlp/feature-selection/rf-weights.csv")
print(importances)
