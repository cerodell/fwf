#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import sys
import json
import joblib
import logging
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, TimeDistributed

from sklearn.inspection import permutation_importance
from sklearn.preprocessing import StandardScaler, RobustScaler
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
time_steps = 24  # LSTM time steps
keep_vars = ["S", "HFI", "LAI", "NDVI", "hour_sin", "hour_cos"]
scaler_type = "standard"  ##robust or standard
n_features = len(keep_vars)  # Number of features used for the model
# Define and compile LSTM model
model = Sequential(
    [
        LSTM(32, input_shape=(time_steps, n_features), return_sequences=True),
        LSTM(32, input_shape=(time_steps, n_features), return_sequences=True),
        # LSTM(32, input_shape=(time_steps, n_features), return_sequences=True),
        TimeDistributed(Dense(32, activation="relu")),
        TimeDistributed(Dense(32, activation="relu")),
        # TimeDistributed(Dense(32, activation='relu')),
        TimeDistributed(Dense(1, activation="relu")),
    ]
)
model.compile(optimizer=Adam(learning_rate=0.01), loss="mse")

# Prepare directory to save model output
make_dir = Path(data_dir) / "lstm/"
make_dir.mkdir(parents=True, exist_ok=True)

# Create directory for saving model configurations based on the model details
save_dir = create_model_directory(str(make_dir), model, model_type="LSTM")
logger = activate_logging(save_dir)
logger.info("Start of Run: %s", startTime)
logger.info("Model directory created: %s", str(save_dir))

# Initialize MLP model and load dataset
mlD = MLDATA(config={"method": f"averaged-lstm-{time_steps}h"})
df = mlD.open_ml_ds()

# Sampling dataset for test and training
IDS = np.unique(df["id"].values)
sample_size = int(0.1 * len(IDS))
test_case_ids = np.random.choice(IDS, size=sample_size, replace=False)
test_case_ids = np.append(test_case_ids, [25485086, 25407482, 24360611])
df_test = df[df["id"].isin(test_case_ids)]
unique_test_df = df_test.drop_duplicates(subset="id", keep="first")
fires_array = np.stack(
    [unique_test_df["id"].values, unique_test_df["local_time"].dt.year.values]
)

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
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# Reshape data for LSTM input
X_train = X_train.reshape(-1, time_steps, n_features)
X_test = X_test.reshape(-1, time_steps, n_features)
y_train = y_train.values.reshape(-1, time_steps, 1)

# Define early stopping criteria
early_stopping = EarlyStopping(
    monitor="val_loss",
    min_delta=0,
    patience=5,
    verbose=1,
    mode="auto",
    baseline=None,
    restore_best_weights=True,
)

# Train the model with early stopping
model.fit(
    X_train,
    y_train,
    epochs=100,
    batch_size=32,
    verbose=1,
    validation_split=0.1,
    callbacks=[early_stopping],
)

# Predict using the trained model
y_out_this_nhn = model.predict(X_test)
y_out_this_nhn = y_out_this_nhn.ravel()


# Save model and scaler
model_path = save_dir / "model.keras"
model.save(model_path)
scaler_path = save_dir / "scaler.joblib"
joblib.dump(scaler, scaler_path)
np.savetxt(save_dir / "test_cases.txt", fires_array, fmt="%d", delimiter=",")

# Save model configuration and statistics
config = {
    "model_config": model.get_config(),
    "features_used": keep_vars,
    "scaler_info": str(scaler_path),
    "model_info": str(model_path),
}
config_path = save_dir / "config.json"
with open(config_path, "w") as json_file:
    json.dump(config, json_file, indent=4)

stats_dict = {
    "rmse": RMSE(y_test, y_out_this_nhn),
    "mbe": MBE(y_test, y_out_this_nhn),
    "r2_score": r2_score(y_test, y_out_this_nhn),
    "pearson_r": np.round(stats.pearsonr(y_test, y_out_this_nhn)[0], 2),
    "length": len(df),
}
for key, value in stats_dict.items():
    print(f"{key}: {value}")

# Save statistics
stats_path = save_dir / "stats.json"
with open(stats_path, "w") as json_file:
    json.dump(stats_dict, json_file, indent=4)

print("Model name: ", str(scaler_path).split("/")[-2])
logger.info("Total Run Time: %s", datetime.now() - startTime)
print("-----------------------------------------------------")


# # # Plot results
# plt.scatter(y_out_this_nhn, y_test)
# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[200:400], color='tab:red')
# ax.plot(y_test.values[200:400], color='black')
# plt.show()


# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[10:200], color='tab:red')
# ax.plot(y_test.values[10:200], color='black')
# plt.show()

# fig, ax = plt.subplots()
# ax.plot(y_out_this_nhn[400:600], color='tab:red')
# ax.plot(y_test.values[400:600], color='black')
# plt.show()
