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
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed, Dropout

# from tensorflow.keras.callbacks import ReduceLROnPlateau

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
    method="averaged-v15",
    years=["2021", "2022", "2023"],
    feature_vars=[
        "ASPECT_sin",
        "ASPECT_cos",
        "S-hour_sin-Total_Fuel_Load",
        "S-hour_cos-Total_Fuel_Load",
        "Total_Fuel_Load",
        "lat_sin",
        "lon_sin",
        "lat_cos",
        "lon_cos",
    ],
    target_vars=["FRP"],
    feature_scaler_type="minmax",  ##robust or standard minmax
    target_scaler_type=True,  ##robust or standard minmax
    transform=True,
    package="tf",
    model_type="MLP",
    smoothing=False,
    # main-cases=True,
    shuffle_data=True,
    feature_engineer=True,
    min_fire_size=0,  ## hectors,
    burn_time=0,
    filter_std=True,
)
config["n_features"] = len(config["feature_vars"])
config["n_targets"] = len(config["target_vars"])

## Initialize MLP model and load dataset
mlD = MLDATA(config)

## Setup MLP model
model = Sequential(
    [
        Dense(64, activation="relu", input_shape=(config["n_features"],)),
        Dropout(0.1),
        Dense(64, activation="relu"),
        Dropout(0.1),
        Dense(config["n_targets"], activation="relu"),  # Output layer
    ]
)

## Compile model
model.compile(optimizer=Adam(learning_rate=1e-04), loss="log_cosh")

# Prepare directory to save model output and active logging script
make_dir = (
    Path(data_dir)
    / f"{config['model_type'].lower()}/{config['package'].lower()}/{config['method']}/{'_'.join(config['target_vars'])}/"
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
# # ## Define learning rate reduction criteria
# reduce_lr = ReduceLROnPlateau(
#     monitor="val_loss", factor=0.2, patience=3, min-lr=1e-6, verbose=1
# )
# Get Training Data
y_train, X_train, X_val, y_val = mlD.get_training()

## Train the model with early stopping
model.fit(
    X_train,
    y_train,
    epochs=30,
    batch_size=32,
    verbose=1,
    # validation_split=0.1,
    # callbacks=[early_stopping],
)


## Predict using the trained model
y_out_this_nhn = model.predict(X_val)


## Save model
user_config = mlD.save_model(model, y_out_this_nhn, save_dir, logger)


if user_config["target_scaler_type"] == True:
    y_out_this_nhn = y_out_this_nhn * user_config["FRP_MAX"]

if user_config["transform"] == True:
    y_out_this_nhn = np.expm1(y_out_this_nhn)
    y_val = np.expm1(y_val)
else:
    y_val = y_val

y_out_this_nhn = y_out_this_nhn.ravel()
R2 = r2_score(y_val, y_out_this_nhn)
pearsonr = np.round(stats.pearsonr(y_val.values.ravel(), y_out_this_nhn)[0], 2)

# Feature reduction method
feature_contributions_R2 = []
feature_contributions_pearsonr = []

for i in range(config["n_features"]):
    # Create a copy of the training and validation data excluding the ith feature
    X_train_reduced = np.delete(X_train, i, axis=1)
    X_val_reduced = np.delete(X_val, i, axis=1)

    # Reinitialize and retrain the model
    model_reduced = Sequential(
        [
            Dense(64, activation="relu", input_shape=(config["n_features"] - 1,)),
            Dropout(0.1),
            Dense(64, activation="relu"),
            Dropout(0.1),
            Dense(config["n_targets"], activation="relu"),
        ]
    )

    model_reduced.compile(optimizer=Adam(learning_rate=1e-04), loss="log_cosh")
    model_reduced.fit(X_train_reduced, y_train, epochs=30, batch_size=32, verbose=1)

    # Evaluate the reduced model performance
    y_out_this_nhn_reduced = model_reduced.predict(X_val_reduced)
    if user_config["target_scaler_type"] == True:
        y_out_this_nhn_reduced = y_out_this_nhn_reduced * user_config["FRP_MAX"]
    if user_config["transform"] == True:
        y_out_this_nhn_reduced = np.expm1(y_out_this_nhn_reduced)
    y_out_this_nhn_reduced = y_out_this_nhn_reduced.ravel()

    R2_i = r2_score(y_val, y_out_this_nhn_reduced)
    pearsonr_i = np.round(
        stats.pearsonr(y_val.values.ravel(), y_out_this_nhn_reduced)[0], 2
    )

    # Compute the relative contribution C_i
    R2_C = 1 - (R2_i / R2)
    pearsonr_C = 1 - (pearsonr_i / pearsonr)
    feature_contributions_R2.append(R2_C)
    feature_contributions_pearsonr.append(pearsonr_C)

# Plot the feature contributions
feature_names = config["feature_vars"]
print(feature_names)
feature_contributions = np.array(feature_contributions_R2)
print(feature_contributions)
plt.figure(figsize=(10, 6))
plt.bar(feature_names, feature_contributions, color="skyblue")
plt.xlabel("Input Variable")
plt.ylabel("Relative Contribution")
plt.title("Feature Importance using Feature-Reduction Method")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Plot the feature contributions
feature_names = config["feature_vars"]
feature_contributions = np.array(feature_contributions_pearsonr)
print(feature_contributions)
plt.figure(figsize=(10, 6))
plt.bar(feature_names, feature_contributions, color="skyblue")
plt.xlabel("Input Variable")
plt.ylabel("Relative Contribution")
plt.title("Feature Importance using Feature-Reduction Method")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


## Log run time
logger.info("Total Run Time: %s", datetime.now() - startTime)
print("-----------------------------------------------------")


print(config)
