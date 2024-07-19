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
import tensorflow as tf

# Custom R² metric function
def r2_metric(y_true, y_pred):
    SS_res = tf.reduce_sum(tf.square(y_true - y_pred))
    SS_tot = tf.reduce_sum(tf.square(y_true - tf.reduce_mean(y_true)))
    return 1 - SS_res / (SS_tot + tf.keras.backend.epsilon())


# tunning_path = Path(data_dir) / "tuning"
# bashComand = "rm -rf " + str(tunning_path)
# os.system(bashComand)

# Mark the start time for the run
startTime = datetime.now()

# Base configuration parameters
base_config = dict(
    method="averaged-v11",
    years=["2021", "2022", "2023"],
    feature_vars=[
        "R-CLIMO_FRP-Total_Fuel_Load",
        # "R-OFFSET_NORM-Total_Fuel_Load",
        # "R-hour_sin-Total_Fuel_Load",
        "U-lat_sin-Total_Fuel_Load",
        "U-lon_sin-Total_Fuel_Load",
        "U-lat_cos-Total_Fuel_Load",
        "U-lon_cos-Total_Fuel_Load",
    ],
    target_vars=["FRP"],
    transform=True,
    package="tf",
    model_type="MLP",
    # main_cases=True,
    # shuffle_data=True,
    feature_engineer=True,
    min_fire_size=0,  # hectares
    filter_std=True,
)

# Different scaler types to evaluate
scaler_types = [
    {"feature_scaler_type": "standard", "target_scaler_type": True},
    {"feature_scaler_type": "standard", "target_scaler_type": False},
    {"feature_scaler_type": "robust", "target_scaler_type": True},
    {"feature_scaler_type": "robust", "target_scaler_type": False},
    {"feature_scaler_type": "minmax", "target_scaler_type": True},
    {"feature_scaler_type": "minmax", "target_scaler_type": False},
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
            units=hp.Int("units_layer_1", min_value=64, max_value=256, step=64),
            activation="relu",
            input_shape=(n_features,),
        )
    )
    model.add(
        Dense(
            units=hp.Int("units_layer_2", min_value=64, max_value=256, step=64),
            activation="relu",
        )
    )
    # Conditional addition of layer 3
    if hp.Boolean("use_layer_3"):
        model.add(
            Dense(
                units=hp.Int("units_layer_3", min_value=64, max_value=256, step=64),
                activation="relu",
            )
        )
    # Conditional addition of layer 4
    if hp.Boolean("use_layer_4"):
        model.add(
            Dense(
                units=hp.Int("units_layer_4", min_value=64, max_value=256, step=64),
                activation="relu",
            )
        )

    model.add(Dense(n_targets, activation="relu"))

    # Choose the optimizer
    optimizer_choice = hp.Choice("optimizer", values=["adam"])
    if optimizer_choice == "adam":
        optimizer = Adam(learning_rate=hp.Choice("learning_rate", values=[1e-4, 1e-5]))
    elif optimizer_choice == "sgd":
        optimizer = SGD(learning_rate=hp.Choice("learning_rate", values=[1e-4, 1e-5]))
    else:
        optimizer = RMSprop(
            learning_rate=hp.Choice("learning_rate", values=[1e-4, 1e-5])
        )

    # Choose the loss function
    loss_choice = hp.Choice("loss", values=["log_cosh"])

    model.compile(
        optimizer=optimizer,
        loss=loss_choice,
        # metrics=[r2_metric]  # Include R² in metrics
    )
    return model


# Hyperparameter tuner
tuner = kt.RandomSearch(
    build_model,
    objective="val_loss",
    # objective=kt.Objective('val_r2_score', direction='max'),  # Optimize for validation R²
    max_trials=75,
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
    y_train, X_train, X_val, y_val = mlD.get_training()

    # Shuffle the training data
    X_train, y_train = shuffle(X_train, y_train, random_state=42)

    # # Setup early stopping
    # early_stopping = EarlyStopping(
    #     monitor="val_loss",
    #     min_delta=0,
    #     patience=5,
    #     verbose=1,
    #     mode="auto",
    #     baseline=None,
    #     restore_best_weights=True,
    # )

    # Search for best hyperparameters
    tuner.search(X_train, y_train, epochs=75, validation_split=0.1)
    # tuner.search(
    #     X_train, y_train, epochs=50
    # )

    # Get the best model
    best_models = tuner.get_best_models(num_models=4)  # [0]

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
            epochs=75,
            batch_size=64,
            verbose=1,
            # callbacks=[early_stopping],
        )

        # Predict using the best model
        y_out_this_nhn = best_model.predict(X_val)

        # Access the optimizer and learning rate
        optimizer_info = best_models[0].optimizer
        learning_rate = (
            optimizer_info.learning_rate.numpy()
        )  # .numpy() converts the tensor to a float

        # Access the loss function
        loss_function = best_models[0].loss
        print("Loss Function:", loss_function)
        print("Optimizer:", optimizer_info)
        print("Learning Rate:", learning_rate)
        logger.info("Loss Function:", loss_function)
        logger.info("Optimizer:", optimizer_info)
        logger.info("Learning Rate:", learning_rate)
        # Save model
        mlD.save_model_tunning(best_model, y_out_this_nhn, save_dir, logger, history)

    # Log run time
    logger.info("Total Run Time: %s", datetime.now() - startTime)
    print("-----------------------------------------------------")
