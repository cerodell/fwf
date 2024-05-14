#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import joblib
import numpy as np
import xarray as xr
import pandas as pd

from sklearn.datasets import make_regression
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


from context import data_dir, root_dir


keep_vars = ["FWI", "FFMC", "HFI", "LAI", "NDVI", "HGT", "GS", "hour", "month"]

df_2021 = (
    xr.open_dataset(
        str(data_dir)
        + "/mlp/training-data/2021-fires-all-spatially-averaged-norm-fwi.nc"
    )
    .to_dataframe()
    .reset_index()
)
df_2022 = (
    xr.open_dataset(
        str(data_dir)
        + "/mlp/training-data/2022-fires-all-spatially-averaged-norm-fwi.nc"
    )
    .to_dataframe()
    .reset_index()
)

df = pd.concat([df_2021, df_2022], ignore_index=True)
df.loc[df["HGT"] < 0, "HGT"] = 0

df["local_time"] = pd.to_datetime(df["time"]) - pd.to_timedelta(
    df["ZoneST"].astype(int), unit="h"
)

df["hour"] = df["local_time"].dt.hour
df["month"] = df["local_time"].dt.month

y = df["FRP"]
X = df[keep_vars]


# Define a pipeline to scale data and then fit an MLP regressor
pipeline = make_pipeline(StandardScaler(), MLPRegressor(random_state=1))

# # Define a grid of parameters to search over
# param_grid = {
#     'mlpregressor__hidden_layer_sizes': [(32,32), (64,64), (128,128),
#                                          (32,32,32), (64,64,64), (128,128,128),
#                                          (32,32,32,32), (64,64,64,64), (128,128,128,128)],
#     'mlpregressor__activation': ['tanh', 'relu'],
#     'mlpregressor__solver': ['sgd', 'adam'],
#     'mlpregressor__alpha': [0.0001, 0.001, 0.01],
#     'mlpregressor__validation_fraction': [0.1],
#     'mlpregressor__early_stopping': [True],
#     'mlpregressor__n_iter_no_change': [10, 15],
#     'mlpregressor__max_iter': [1000, 1500, 2000]
# }

# Define a grid of parameters to search over
param_grid = {
    "mlpregressor__hidden_layer_sizes": [
        (32, 32, 32, 32),
        (64, 64, 64, 64),
        (128, 128, 128, 128),
    ],
    "mlpregressor__activation": ["relu"],
    "mlpregressor__solver": ["adam"],
    "mlpregressor__alpha": [0.0001, 0.01],
    "mlpregressor__validation_fraction": [0.1],
    "mlpregressor__early_stopping": [True],
    "mlpregressor__n_iter_no_change": [10, 15],
    "mlpregressor__max_iter": [1000, 2000],
}


# Check if a previous state of the grid search exists
grid_search = GridSearchCV(pipeline, param_grid, cv=5, verbose=1)

# Fit grid search to the data
grid_search.fit(X, y)

# Output the best parameters and best score found during the grid search
print("Best parameters found:", grid_search.best_params_)
print("Best score achieved:", grid_search.best_score_)
