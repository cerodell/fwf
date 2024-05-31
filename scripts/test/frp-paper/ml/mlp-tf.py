#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import json
import joblib
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
from keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed, Dropout
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from sklearn.utils import shuffle
from sklearn.linear_model import LinearRegression

from sklearn.inspection import permutation_importance
from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from utils.ml_data import MLDATA
from utils.tf import activate_logging, create_model_directory
from context import data_dir


# Mark the start time for the run
startTime = datetime.now()

# Configuration parameters
config = dict(
    method="averaged-v2",
    keep_vars=[
        # "R",
        # "U",
        # "S",
        "R_hour_sin_Live_Wood",
        "R_hour_cos_Live_Wood",
        "R_hour_sin_Dead_Wood",
        "R_hour_cos_Dead_Wood",
        "R_hour_sin_Live_Leaf",
        "R_hour_cos_Live_Leaf",
        "R_hour_sin_Dead_Foliage",
        "R_hour_cos_Dead_Foliage",
        # "U_Live_Wood",
        # "U_Dead_Wood",
        # "U_Live_Leaf",
        # "F_Dead_Foliage",
        # "F_Dead_Foliage",
        # "R_hour_sin",
        # "R_hour_cos",
        # "R_lat_sin",
        # "R_lat_cos",
        # "R_lon_sin",
        # "R_lon_cos",
        # "U_lat_sin_total_fuel",
        # "U_lat_cos_total_fuel",
        # "U_lon_sin_total_fuel",
        # "U_lon_cos_total_fuel",
        "U_lat_sin_Live_Wood",
        "U_lat_cos_Live_Wood",
        "U_lon_sin_Live_Wood",
        "U_lon_cos_Live_Wood",
        "U_lat_sin_Dead_Wood",
        "U_lat_cos_Dead_Wood",
        "U_lon_sin_Dead_Wood",
        "U_lon_cos_Dead_Wood",
        "F_lat_sin_Live_Leaf",
        "F_lat_cos_Live_Leaf",
        "F_lon_sin_Live_Leaf",
        "F_lon_cos_Live_Leaf",
        "F_lat_sin_Dead_Foliage",
        "F_lat_cos_Dead_Foliage",
        "F_lon_sin_Dead_Foliage",
        "F_lon_cos_Dead_Foliage",
    ],
    scaler_type="standard",  ##robust or standard minmax
    transform=False,
    min_fire_size=1000,
    package="tf",
    model_type="MLP",
    main_cases=True,
    shuffle_data=True,
    feature_engineer=True,
)
config["n_features"] = len(config["keep_vars"])

## Initialize MLP model and load dataset
mlD = MLDATA(config)

## Setup MLP model
model = Sequential(
    [
        Dense(64, activation="relu", input_shape=(config["n_features"],)),
        # Dropout(0.2),
        Dense(64, activation="relu"),
        # Dropout(0.2),
        # Dense(64, activation="relu"),
        # # Dropout(0.2),
        # Dense(64, activation="relu"),
        # # Dropout(0.2),
        Dense(1, activation="relu"),  # Output layer
    ]
)

## Compile model
model.compile(optimizer=Adam(learning_rate=0.001), loss="log_cosh")

# Prepare directory to save model output and active logging script
make_dir = (
    Path(data_dir)
    / f"{config['model_type'].lower()}/{config['package'].lower()}/{config['method']}/"
)
make_dir.mkdir(parents=True, exist_ok=True)
save_dir, logger = create_model_directory(
    str(make_dir), model, model_type=config["model_type"]
)
logger.info("Start of Run: %s", startTime)
logger.info("Model directory created: %s", str(save_dir))

## Define early stopping criteria
early_stopping = EarlyStopping(
    monitor="val_loss",
    min_delta=0,
    patience=5,
    verbose=1,
    mode="auto",
    baseline=None,
    restore_best_weights=True,
)

## Get Training Data
y_train, X_train, y_test, X_test = mlD.get_training()

## Train the model with early stopping
model.fit(
    X_train,
    y_train,
    epochs=400,
    batch_size=32,
    verbose=1,
    validation_split=0.1,
    callbacks=[early_stopping],
)

## Predict using the trained model
y_out_this_nhn = model.predict(X_test)
y_out_this_nhn = y_out_this_nhn.ravel()

## Save model
mlD.save_model(model, y_out_this_nhn, save_dir, logger)

## Log run time
logger.info("Total Run Time: %s", datetime.now() - startTime)
print("-----------------------------------------------------")

if config["transform"] == True:
    print(f'transform: {config["transform"]}')
    y_out_this_nhn = np.expm1(y_out_this_nhn)
    y_test = np.expm1(y_test)


mbe, rmse = str(np.round(MBE(y_test.values, y_out_this_nhn), 2)), np.round(
    RMSE(y_test.values, y_out_this_nhn), 2
)
r2, r = np.round(r2_score(y_test.values, y_out_this_nhn), 2), np.round(
    stats.pearsonr(y_test.values, y_out_this_nhn)[0], 2
)


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.scatter(y_out_this_nhn, y_test.values, color="tab:red", s=15)
ax.set_xlabel("Modeled FRP (MW)")
ax.set_ylabel("Observed FRP (MW)")
ax.set_title(f"MBE: {mbe}   RMSE: {rmse}   r2: {r2}   r: {r}")
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
fig.savefig(str(save_dir) + "/scatter.png")
