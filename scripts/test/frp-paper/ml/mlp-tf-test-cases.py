#!/Users/crodell/miniconda3/envs/fwx/bi\npython

import context
import json
import salem
import joblib
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib

from utils.ml_data import MLDATA
from tensorflow.keras.models import load_model

import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir


all_fire = True
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense"
method = "averaged-v15"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"

with open(f"{model_dir}/config.json", "r") as json_data:
    config = json.load(json_data)["user_config"]


fire_cases = np.loadtxt(f"{model_dir}/test_cases.txt", delimiter=",")
test_ids = fire_cases[0].astype(int)
test_years = fire_cases[1].astype(int)

mlD = MLDATA(config=config)
df = mlD.open_ml_ds()
df_test = df[df["id"].isin(test_ids)].reset_index()

X = df_test[config["feature_vars"]]

# Load the scaler
scaler = joblib.load(f"{model_dir}/feature-scaler.joblib")
X_new_scaled = scaler.transform(X)

# Load the model
model = load_model(f"{model_dir}/model.keras")

startFRP = datetime.now()
# print("Start prediction:", startFRP)
y_out_this_nhn = model(X_new_scaled).numpy()
if config["target_scaler_type"] != None:
    print("rescaling target")
    y_out_this_nhn = y_out_this_nhn * config["FRP_MAX"]
#     y_out_this_nhn = target_scaler.inverse_transform(y_out_this_nhn)\
if config["transform"] == True:
    print("retransforming target")
    y_out_this_nhn = np.expm1(y_out_this_nhn)
    df_test["FRP"] = np.expm1(df_test["FRP"])

# FRP_FULL = y_out_this_nhn.ravel().reshape(shape)
FRP_FULL = y_out_this_nhn.ravel()

df_test["P_FRP"] = FRP_FULL


for var in config["target_vars"]:
    if var.lower() == "fre":
        units = "(MJ)"
    elif var.lower() == "frp":
        units = "(MW)"
    y_t = df_test[f"{var}"]
    y_nhn = df_test[f"P_{var}"]
    mbe = str(np.round(MBE(y_t, y_nhn), 2))
    rmse = np.round(RMSE(y_t, y_nhn), 2)
    r2 = np.round(r2_score(y_t, y_nhn), 2)
    r = np.round(stats.pearsonr(y_t, y_nhn)[0], 2)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(y_nhn, y_t, color="tab:red", s=15)
    ax.set_xlabel(f"Modeled {var.upper()} {units}")
    ax.set_ylabel(f"Observed {var.upper()} {units}")
    ax.set_title(f"MBE: {mbe}   RMSE: {rmse}   r2: {r2}   r: {r}")
    ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
    if var == "FRP":
        min_lim = -100
        max_lim = np.max(np.stack([y_nhn, y_t])) - min_lim
    else:
        min_lim = -5e5
        max_lim = np.max(np.stack([y_nhn, y_t])) - min_lim
    ax.set_xlim(min_lim, max_lim)
    ax.set_ylim(min_lim, max_lim)


year_l = []
mbe_l, rmse_l, r2_l, r_l, id_l = [], [], [], [], []
for id in test_ids:
    fire_case = df_test[df_test["id"] == id]
    fire_case = fire_case.set_index("time")
    full_range = pd.date_range(
        start=fire_case.index.min(), end=fire_case.index.max(), freq="h"
    )
    df_reindexed = fire_case.reindex(full_range)
    y_t, y_nhn = df_reindexed["FRP"].dropna(), df_reindexed["P_FRP"].dropna()

    # date_times = df_reindexed.index
    # fig = plt.figure(figsize=(12, 4))
    # ax = fig.add_subplot(1, 1, 1)
    # ax.set_title(id, loc="left")
    # title = (
    #     "MBE: "
    #     + str(np.round(MBE(y_t, y_nhn), 2))
    #     + "\n"
    #     + "rmse: "
    #     + str(np.round(RMSE(y_t, y_nhn), 2))
    #     + "\n"
    #     + "r2_score: "
    #     + str(np.round(r2_score(y_t, y_nhn), 2))
    #     + "\n"
    #     + "r: "
    #     + str(np.round(stats.pearsonr(y_t, y_nhn)[0], 2))
    #     + "\n"
    # )

    # ax.set_title(title, loc="right")
    # ax.plot(date_times, df_reindexed["FRP"])
    # ax.plot(date_times, df_reindexed["P_FRP"])
    # print("MBE: ", str(np.round(MBE(y_t, y_nhn), 2)))
    # print("rmse: ", np.round(RMSE(y_t, y_nhn), 2))
    # print("r2: ", np.round(r2_score(y_t, y_nhn), 2))
    # print("r: ", np.round(stats.pearsonr(y_t, y_nhn)[0], 2))
    mbe_l.append(str(np.round(MBE(y_t, y_nhn), 2)))
    rmse_l.append(np.round(RMSE(y_t, y_nhn), 2))
    r2_l.append(np.round(r2_score(y_t, y_nhn), 2))
    r_l.append(np.round(stats.pearsonr(y_t, y_nhn)[0], 2))
    id_l.append(id)
    year_l.append(fire_case.index.year[0])

mbe_l, rmse_l, r2_l, r_l, id_l, year_l = (
    np.array(mbe_l),
    np.array(rmse_l),
    np.array(r2_l),
    np.array(r_l),
    np.array(id_l),
    np.array(year_l),
)
# # ticks = [10, 20, 50, 100, 200, 300, 500, 800, 1000, 1500,2000, 3000]
# # ax.set_xticks(ticks)
# # ax.set_yticks(ticks)
# fig.savefig(str(save_dir) + f"/{target}-scatter.png")


good_ids = id_l[r2_l > 0.3]
for i in good_ids:
    fire_case = df_test[df_test["id"] == float(i)]
    fire_case = fire_case.set_index("time")
    full_range = pd.date_range(
        start=fire_case.index.min(), end=fire_case.index.max(), freq="h"
    )
    df_reindexed = fire_case.reindex(full_range)
    y_t, y_nhn = df_reindexed["FRP"].dropna(), df_reindexed["P_FRP"].dropna()

    date_times = df_reindexed.index
    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title(int(fire_case["id"].values[0]), loc="left")
    title = (
        "MBE: "
        + str(np.round(MBE(y_t, y_nhn), 2))
        + "\n"
        + "rmse: "
        + str(np.round(RMSE(y_t, y_nhn), 2))
        + "\n"
        + "r2_score: "
        + str(np.round(r2_score(y_t, y_nhn), 2))
        + "\n"
        + "r: "
        + str(np.round(stats.pearsonr(y_t, y_nhn)[0], 2))
        + "\n"
    )

    ax.set_title(title, loc="right")
    ax.plot(date_times, df_reindexed["FRP"])
    ax.plot(date_times, df_reindexed["P_FRP"])
