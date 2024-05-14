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
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
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

# Configuration parameters
# Configuration parameters
config = dict(
    method="averaged",
    keep_vars=[
        "R",
        "U",
        "Live_Wood",
        "Dead_Wood",
        "Live_Leaf",
        "Dead_Foliage",
        "hour_sin",
        "hour_cos",
    ],
    scaler_type="standard",  ##robust or standard minmax
    transform=True,
    min_fire_size=10000,
    package="sk",
    model_type="RF",
    main_cases=True,
    shuffle_data=True,
)
config["n_features"] = len(config["keep_vars"])

## Initialize MLP model and load dataset
mlD = MLDATA(config)

# Define and compile RF model
model = RandomForestRegressor(
    verbose=True,
    max_depth=10,
    n_estimators=300,
    max_features="sqrt",
    min_samples_leaf=4,
    min_samples_split=10,
    random_state=42,
)

# Prepare directory to save model output and active logging script
make_dir = (
    Path(data_dir) / f"{config['model_type'].lower()}/{config['package'].lower()}/"
)
make_dir.mkdir(parents=True, exist_ok=True)
save_dir, logger = create_model_directory(
    str(make_dir), model, model_type=config["model_type"]
)
logger.info("Start of Run: %s", startTime)
logger.info("Model directory created: %s", str(save_dir))


## Get Training Data
y_train, X_train, y_test, X_test = mlD.get_training()

startTrain = datetime.now()
print("Training model")
model.fit(X_train, y_train)
logger.info("Training Time: %s", datetime.now() - startTrain)

# Predict using the trained model
y_out_this_nhn = model.predict(X_test)

## Save model
mlD.save_model(model, y_out_this_nhn, save_dir, logger)

## Log run time
logger.info("Total Run Time: %s", datetime.now() - startTime)
print("-----------------------------------------------------")

if config["transform"] == True:
    y_out_this_nhn = np.expm1(y_out_this_nhn)
    y_test = np.expm1(y_test)


print("Total Run Time: ", datetime.now() - startTime)
print("-----------------------------------------------------")


# # # Plot results
# plt.scatter(y_out_this_nhn[200:400],y_test.values[200:400])
# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[200:400], color='tab:red')
# ax.plot(y_test.values[200:400], color='black')
# plt.show()


# x = 400
# y = x + 250
# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[x:y], color='tab:red')
# ax.plot(y_test.values[x:y], color='black')
# plt.show()

# fig, ax = plt.subplots()
# ax.plot(df_test['R'].values[x:y], color='black')
