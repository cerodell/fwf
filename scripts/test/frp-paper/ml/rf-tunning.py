#!/Users/crodell/miniconda3/envs/fwx/bin/python
"""
Best parameters: {'max_depth': 10, 'max_features': 'sqrt', 'min_samples_leaf': 4, 'min_samples_split': 10, 'n_estimators': 300}
"""
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
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV


from datetime import datetime
from utils.ml_data import MLDATA

from context import data_dir, root_dir
from joblib import parallel_backend

# Mark the start time for the run
startTime = datetime.now()

# Configuration parameters
keep_vars = ["R", "U", "LAI", "hour_sin", "hour_cos", "Live_Wood", "Dead_Wood"]

scaler_type = "standard"  ##robust or standard or minmax
n_features = len(keep_vars)
transform = True  ## set to None if not using

# Define and compile RF model
model = RandomForestRegressor(verbose=True, random_state=42)

# Initialize MLP model and load dataset
mlD = MLDATA(
    config={"method": "averaged", "transform": transform, "min_fire_size": 10000}
)
df = mlD.open_ml_ds()

### Sampling dataset for test and training
IDS = np.unique(df["id"].values)
sample_size = int(0.1 * len(IDS))
test_case_ids = np.random.choice(IDS, size=sample_size, replace=False)
test_case_ids = np.append(test_case_ids, [25485086, 25407482, 24360611])
df_test = df[df["id"].isin(test_case_ids)]
unique_test_df = df_test.drop_duplicates(subset="id", keep="first")
test_cases = np.stack(
    [unique_test_df["id"].values, unique_test_df["local_time"].dt.year.values]
)

df_train = df[~df["id"].isin(test_case_ids)]
large_fires = df_train.loc[df_train["area_ha"] > 50000]
larger_fires = df_train.loc[df_train["area_ha"] > 100000]
df_train = pd.concat([df_train, large_fires, larger_fires])
df_train.reset_index(drop=True, inplace=True)

df_train = df[~df["id"].isin(test_case_ids)]
y_train = df_train["FRP"]
X_train = df_train[keep_vars]
y_test = df_test["FRP"]
X_test = df_test[keep_vars]


# Scale features
if scaler_type == "standard":
    scaler = StandardScaler().fit(X_train)
elif scaler_type == "robust":
    scaler = RobustScaler().fit(X_train)
elif scaler_type == "minmax":
    scaler = MinMaxScaler().fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)


# Set up the parameter grid
param_grid = {
    "n_estimators": [100, 300, 500],
    "max_features": ["auto", "sqrt", "log2"],
    "max_depth": [None, 10, 20, 30],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
}

# Configure GridSearchCV
grid_search = GridSearchCV(
    estimator=model, param_grid=param_grid, cv=3, n_jobs=-1, verbose=2
)

# Fit the grid search to the data
grid_search.fit(X_train, y_train)

# Best parameters and model
print("Best parameters:", grid_search.best_params_)
best_model = grid_search.best_estimator_


# Make predictions
predictions = best_model.predict(X_test)

# Evaluate the predictions
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)
