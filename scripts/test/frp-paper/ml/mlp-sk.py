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

from sklearn.neural_network import MLPRegressor
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
keep_vars = [
    "R",
    "U",
    "Live_Wood",
    "Dead_Wood",
    "Live_Leaf",
    "Dead_Foliage",
    "hour_sin",
    "hour_cos",
]
scaler_type = "standard"  ##robust or standard or minmax
n_features = len(keep_vars)
transform = True  ## set to None if not using

# Define and compile MLP model
model = MLPRegressor(
    hidden_layer_sizes=(32, 32),
    verbose=True,
    max_iter=1500,
    early_stopping=True,
    validation_fraction=0.1,
    batch_size=32,
    solver="adam",
    activation="relu",
    learning_rate_init=0.01,
)

# Prepare directory to save model output
make_dir = Path(data_dir) / "mlp/sk/"
make_dir.mkdir(parents=True, exist_ok=True)

# Create directory for saving model configurations based on the model details
save_dir = create_model_directory(str(make_dir), model, model_type="MLP")
logger = activate_logging(save_dir)
logger.info("Start of Run: %s", startTime)
logger.info("Model directory created: %s", str(save_dir))

# Initialize MLP model and load dataset
mlD = MLDATA(
    config={"method": "averaged", "transform": transform, "min_fire_size": 10000}
)
df = mlD.open_ml_ds()
logger.info("Min Fire Size: %s", float(df["area_ha"].min()))
logger.info("Max Fire Size: %s", float(df["area_ha"].max()))


# Sampling dataset for test and training
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
if transform == True:
    hot_fires = df_train.loc[df_train["FRP"] > np.log1p(1000)]
    hotter_fires = df_train.loc[df_train["FRP"] > np.log1p(2000)]
else:
    hot_fires = df_train.loc[df_train["FRP"] > 1000]
    hotter_fires = df_train.loc[df_train["FRP"] > 2000]
df_train = pd.concat([df_train, large_fires, larger_fires, hot_fires, hotter_fires])
df_train.reset_index(drop=True, inplace=True)


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


startTrain = datetime.now()
print("Training model")
model.fit(X_train, y_train)
logger.info("Training Time: %s", datetime.now() - startTrain)

# Predict using the trained model
y_out_this_nhn = model.predict(X_test)
# Save model and scaler
model_path = save_dir / "model.joblib"
joblib.dump(model, model_path)
scaler_path = save_dir / "scaler.joblib"
joblib.dump(scaler, scaler_path)
np.savetxt(save_dir / "test_cases.txt", test_cases, fmt="%d", delimiter=",")


# Save model configuration and statistics
config = {
    "model_config": model.get_params(),
    "features_used": keep_vars,
    "scaler_type": scaler_type,
    "scaler_info": str(scaler_path),
    "model_info": str(model_path),
}
config_path = save_dir / "config.json"
with open(config_path, "w") as json_file:
    json.dump(config, json_file, indent=4)

stats_dict = {
    "rmse": str(RMSE(y_test, y_out_this_nhn)),
    "mbe": str(MBE(y_test, y_out_this_nhn)),
    "r2_score": str(r2_score(y_test, y_out_this_nhn)),
    "pearson_r": str(np.round(stats.pearsonr(y_test, y_out_this_nhn)[0], 2)),
    "length": str(len(df)),
}
for key, value in stats_dict.items():
    print(f"{key}: {value}")


print("-----------------------------------------------------")
result = permutation_importance(
    model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1
)
# Display importance
feature = keep_vars
for i in range(n_features):
    print(
        f"Feature {feature[i]}: Importance {result.importances_mean[i]:.4f} ± {result.importances_std[i]:.4f}"
    )
    stats_dict[feature[i]] = (
        f"importances_mean {result.importances_mean[i]}",
        f"importances_std: {result.importances_std[i]}",
    )


# Save statistics
stats_path = save_dir / "stats.json"
with open(stats_path, "w") as json_file:
    json.dump(stats_dict, json_file, indent=4)

print("Total Run Time: ", datetime.now() - startTime)
print("-----------------------------------------------------")
