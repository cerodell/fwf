#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import os
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
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
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
import keras_tuner as kt

# import tensorflow as tf
# from tensorflow.keras import backend as K

# def r2_score(y_true, y_pred):
#     SS_res = K.sum(K.square(y_true - y_pred))
#     SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
#     return 1 - SS_res / (SS_tot + K.epsilon())


# Mark the start time for the run
startTime = datetime.now()

# Base configuration parameters
base_config = dict(
    method="averaged-v5",
    years=["2021", "2022", "2023"],
    feature_vars=[
        "SAZ_sin-Total_Fuel_Load",
        "SAZ_cos-Total_Fuel_Load",
        "S-hour_sin-lat_cos-Total_Fuel_Load",
        "S-hour_cos-lat_cos-Total_Fuel_Load",
        "S-hour_sin-lat_sin-Total_Fuel_Load",
        "S-hour_cos-lat_sin-Total_Fuel_Load",
        "S-hour_sin-lon_cos-Total_Fuel_Load",
        "S-hour_cos-lon_cos-Total_Fuel_Load",
        "S-hour_sin-lon_sin-Total_Fuel_Load",
        "S-hour_cos-lon_sin-Total_Fuel_Load",
    ],
    target_vars=["FRP", "FRE"],
    transform=True,
    package="tf",
    model_type="MLP",
    main_cases=True,
    shuffle_data=True,
    feature_engineer=True,
    min_fire_size=500,  # hectares
    filter_std=False,
)

# Different scaler types to evaluate
scaler_types = [
    {"feature_scaler_type": "standard", "target_scaler_type": None},
    {"feature_scaler_type": "robust", "target_scaler_type": None},
]
base_config["n_features"] = len(base_config["feature_vars"])
base_config["n_targets"] = len(base_config["target_vars"])
n_features = base_config["n_features"]
n_targets = base_config["n_targets"]

# Hyperparameter tuning function
def build_model(hp):
    model = Sequential()
    model.add(
        Dense(
            units=hp.Int("units_layer_1", min_value=32, max_value=128, step=32),
            activation="relu",
            input_shape=(n_features,),
        )
    )
    model.add(Dropout(hp.Float("dropout_1", min_value=0.0, max_value=0.5, step=0.1)))

    model.add(
        Dense(
            units=hp.Int("units_layer_2", min_value=32, max_value=128, step=32),
            activation="relu",
        )
    )
    model.add(Dropout(hp.Float("dropout_2", min_value=0.0, max_value=0.5, step=0.1)))

    # Conditional addition of layer 3
    if hp.Boolean("use_layer_3"):
        model.add(
            Dense(
                units=hp.Int("units_layer_3", min_value=32, max_value=128, step=32),
                activation="relu",
            )
        )
        model.add(
            Dropout(hp.Float("dropout_3", min_value=0.0, max_value=0.5, step=0.1))
        )

    # Conditional addition of layer 4
    if hp.Boolean("use_layer_4"):
        model.add(
            Dense(
                units=hp.Int("units_layer_4", min_value=32, max_value=128, step=32),
                activation="relu",
            )
        )
        model.add(
            Dropout(hp.Float("dropout_4", min_value=0.0, max_value=0.5, step=0.1))
        )

    model.add(Dense(n_targets, activation="relu"))

    # Choose the optimizer
    optimizer_choice = hp.Choice("optimizer", values=["adam", "sgd", "rmsprop"])
    if optimizer_choice == "adam":
        optimizer = Adam(
            learning_rate=hp.Choice("learning_rate", values=[1e-2, 1e-3, 1e-4])
        )
    elif optimizer_choice == "sgd":
        optimizer = SGD(
            learning_rate=hp.Choice("learning_rate", values=[1e-2, 1e-3, 1e-4])
        )
    else:
        optimizer = RMSprop(
            learning_rate=hp.Choice("learning_rate", values=[1e-2, 1e-3, 1e-4])
        )

    # Choose the loss function
    loss_choice = hp.Choice(
        "loss", values=["log_cosh", "mean_absolute_error", "mean_squared_error"]
    )

    model.compile(
        optimizer=optimizer,
        loss=loss_choice,
        # metrics=[r2_score]  # Include R² in metrics
    )
    return model


tunning_path = Path(data_dir) / "tuning"
bashComand = "rm -rf " + str(tunning_path)
os.system(bashComand)


# Hyperparameter tuner
tuner = kt.RandomSearch(
    build_model,
    objective="val_loss",
    # objective=kt.Objective('val_r2_score', direction='max'),  # Optimize for validation R²
    max_trials=50,
    executions_per_trial=1,
    directory=Path(data_dir) / "tuning",
    project_name="mlp_tuning",
)

# Iterate over each scaler configuration
for scaler_config in scaler_types:
    # Merge base config with scaler config
    config = {**base_config, **scaler_config}

    # Initialize MLP model and load dataset
    mlD = MLDATA(config)

    # Get training data
    y_train, X_train, y_test, X_test = mlD.get_training()

    # Shuffle the training data
    X_train, y_train = shuffle(X_train, y_train, random_state=42)

    # Setup early stopping
    early_stopping = EarlyStopping(
        monitor="val_loss",
        min_delta=0,
        patience=5,
        verbose=1,
        mode="auto",
        baseline=None,
        restore_best_weights=True,
    )

    # Search for best hyperparameters
    tuner.search(
        X_train, y_train, epochs=50, validation_split=0.1, callbacks=[early_stopping]
    )

    # Get the best model
    best_models = tuner.get_best_models(num_models=1)[0]

    for best_model in best_models:
        # Prepare directory to save model output and active logging script
        make_dir = (
            Path(data_dir)
            / f"{config['model_type'].lower()}/{config['package'].lower()}/{config['method']}/{scaler_config['feature_scaler_type']}"
        )
        make_dir.mkdir(parents=True, exist_ok=True)
        save_dir, logger = create_model_directory(
            str(make_dir), best_model, model_type=config["model_type"]
        )
        logger.info("Start of Run: %s", startTime)
        logger.info("Model directory created: %s", str(save_dir))

        # Train the best model
        history = best_model.fit(
            X_train,
            y_train,
            epochs=400,
            batch_size=32,
            verbose=1,
            validation_split=0.1,
            callbacks=[early_stopping],
            shuffle=True,  # Ensure shuffling at each epoch
        )

        # Predict using the best model
        y_out_this_nhn = best_model.predict(X_test)

        # Save model
        mlD.save_model_tunning(best_model, y_out_this_nhn, save_dir, logger, history)

    # Log run time
    logger.info("Total Run Time: %s", datetime.now() - startTime)
    print("-----------------------------------------------------")
