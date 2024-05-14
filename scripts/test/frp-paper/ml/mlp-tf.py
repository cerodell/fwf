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
    package="tf",
    model_type="MLP",
    main_cases=True,
    shuffle_data=True,
)
config["n_features"] = len(config["keep_vars"])

## Initialize MLP model and load dataset
mlD = MLDATA(config)

## Setup MLP model
model = Sequential(
    [
        Dense(32, activation="relu", input_shape=(config["n_features"],)),
        # Dropout(0.2),
        Dense(32, activation="relu"),
        # Dropout(0.2),
        Dense(1, activation="relu"),  # Output layer
    ]
)

## Compile model
model.compile(optimizer=Adam(learning_rate=0.01), loss="log_cosh")

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
    y_out_this_nhn = np.expm1(y_out_this_nhn)
    y_test = np.expm1(y_test)

# # # # Plot results
# plt.scatter(y_out_this_nhn[200:400],y_test.values[200:400])
# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[200:400], color='tab:red')
# ax.plot(y_test.values[200:400], color='black')
# plt.show()

# x = 00
# y = x + 250
# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[x:y], color='tab:red')
# ax.plot(y_test.values[x:y], color='black')
# plt.show()

# fig, ax = plt.subplots()
# ax.plot(df_test['R'].values[x:y], color='black')
