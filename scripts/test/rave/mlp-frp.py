import context
import salem
import joblib
import random
import string
import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from scipy import stats
from utils.stats import MBE

from context import data_dir, root_dir


trail = "test3"
spatially_averaged = True
norm_fwi = True
# keep_vars = ['FFMC', 'HFI','LAI', 'NDVI', 'HGT', 'GS', 'Live_Leaf', 'Live_Wood', 'Dead_Foliage', 'Dead_Wood', 'hour', 'month']
keep_vars = ["FFMC", "HFI", "LAI", "NDVI", "HGT", "GS", "hour", "month"]

filein = f"/Volumes/WFRT-Ext23/mlp-data/"
df_2021 = (
    xr.open_dataset(filein + "2021-fires-all-spatially-averaged-norm-fwi.nc")
    .to_dataframe()
    .reset_index()
)
df_2022 = (
    xr.open_dataset(filein + "2022-fires-all-spatially-averaged-norm-fwi.nc")
    .to_dataframe()
    .reset_index()
)

df = pd.concat([df_2021, df_2022], ignore_index=True)

df["local_time"] = pd.to_datetime(df["time"]) - pd.to_timedelta(
    df["ZoneST"].astype(int), unit="h"
)

df["hour"] = df["local_time"].dt.hour
df["month"] = df["local_time"].dt.month

# df['hour'] = (df['hour'] - 0) / (24 - 0)
# df['month'] = (df['month'] - 1) / (12 - 1)
# df['FFMC'] = (df['FFMC'] - 0) / (101 - 0)
# df['HFI'] = (df['HFI'] - 0) / (df['HFI'].max() - 0)

# df.loc[df['NFWI'] < 0, 'NFWI'] = 0
# df = df.drop(df[df['NFWI'] > 50].index)

# for var in ['LAI', 'NDVI', 'HGT', 'GS', 'Live_Leaf', 'Live_Wood', 'Dead_Foliage', 'Dead_Wood',]:
#     df[var] = (df[var] - df[var].min()) / (df[var].max() - df[var].min())


y = df["FRP"]
X = df[keep_vars]
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

scaler = StandardScaler().fit(X_train)
joblib.dump(scaler, str(data_dir) + f"/mlp/scaler.joblib")

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)


def rmse(target, prediction):
    return np.sqrt(((target - prediction) ** 2).sum() / len(target))


num_models = 1  # number of models to build for the ensemble
min_nhn = 14  # minimum number of hidden neurons to loop through (nhn = 'number hidden neurons')
max_nhn = 14  # maximum number of hidden neurons to loop through
min_hidden_layers = (
    3  # minimum number of hidden layers to loop through (nhl = 'number hidden layers')
)
max_hidden_layers = (
    3  # maximum number of hidden layers to loop through (nhl = 'number hidden layers')
)
batch_size = 32
solver = "adam"  # use stochastic gradient descent as an optimization method (weight updating algorithm)
activation = "relu"
learning_rate_init = 0.01
#####

max_iter = 1500  # max number of epochs to run
early_stopping = True  # True = stop early if validation error begins to rise
validation_fraction = 0.1  # fraction of training data to use as validation


y_out_all_nhn = []
y_out_ensemble = []
RMSE_ensemble = []  # RMSE for each model in the ensemble
RMSE_ensemble_cumsum = []  # RMSE of the cumulative saltation for each model
nhn_best = []
nhl_best = []


# Initialize an empty DataFrame
df_model = pd.DataFrame()
headers = [
    "name",
    "model_num",
    "num_hidden_neurons",
    "num_hidden_layers",
    "rmse",
    "score",
    "batch_size",
    "solver",
    "activation",
    "learning_rate_init",
    "max_iter",
    "early_stopping",
    "validation_fraction",
]

# Simulate discovering these headers one by one in a loop
for header in headers:
    # Check if the header is not already in the DataFrame
    if header not in df.columns:
        # Add the new column with NaN values
        df_model[header] = pd.NA

print(df_model)


for model_num in range(num_models):  # for each model in the ensemble

    print("Model Number: " + str(model_num))

    RMSE = []
    y_out_all_nhn = []
    nhn = []
    nhl = []

    for num_hidden_layers in range(min_hidden_layers, max_hidden_layers + 1):

        print("\t # Hidden Layers = " + str(num_hidden_layers))

        for num_hidden_neurons in range(
            min_nhn, max_nhn + 1
        ):  # for each number of hidden neurons

            print("\t\t # hidden neurons = " + str(num_hidden_neurons))

            hidden_layer_sizes = (num_hidden_neurons, num_hidden_layers)
            model = MLPRegressor(
                hidden_layer_sizes=hidden_layer_sizes,
                verbose=False,
                max_iter=max_iter,
                early_stopping=early_stopping,
                validation_fraction=validation_fraction,
                batch_size=batch_size,
                solver=solver,
                activation=activation,
                learning_rate_init=learning_rate_init,
            )

            model.fit(X_train, y_train)  # train the model
            model_score = model.score(X_test, y_test)

            y_out_this_nhn = model.predict(
                X_test
            )  # model prediction for this number of hidden neurons (nhn)
            y_out_all_nhn.append(
                y_out_this_nhn
            )  # store all models -- will select best one best on RMSE

            model_rmse = rmse(y_test, y_out_this_nhn)
            model_mbe = MBE(y_test, y_out_this_nhn)
            model_pearson = np.round(stats.pearsonr(y_test, y_out_this_nhn)[0], 2)
            print(f"\t\t # score: {model_score}")
            print(f"\t\t # rmse: {model_rmse}")
            print(f"\t\t # mbe: {model_mbe}")
            print(f"\t\t # pearsonr: {model_pearson}")

            RMSE.append(model_rmse)  # RMSE between cumulative curves

            nhn.append(num_hidden_neurons)
            nhl.append(num_hidden_layers)
            # Save the model to a file
            name = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            row = {
                "name": name,
                "model_num": model_num,
                "num_hidden_neurons": num_hidden_neurons,
                "num_hidden_layers": num_hidden_layers,
                "rmse": model_rmse,
                "mbe": model_mbe,
                "pearsonr": model_pearson,
                "score": model_score,
                "batch_size": batch_size,
                "solver": solver,
                "activation": activation,
                "learning_rate_init": learning_rate_init,
                "max_iter": max_iter,
                "early_stopping": early_stopping,
                "validation_fraction": validation_fraction,
            }
            df_model = pd.concat([df_model, pd.DataFrame([row])], ignore_index=True)

            joblib.dump(model, str(data_dir) + f"/mlp/{trail}/model-{name}.joblib")

    indBest = RMSE.index(np.min(RMSE))  # index of model with lowest RMSE
    RMSE_ensemble.append(np.min(RMSE))
    nhn_best.append(nhn[indBest])
    nhl_best.append(nhl[indBest])
    # nhn_best.append(indBest+1) #the number of hidden neurons that achieved best model performance of this model iteration
    y_out_ensemble.append(y_out_all_nhn[indBest])

    print(
        "\t BEST: "
        + str(nhl_best[model_num])
        + " hidden layers, "
        + str(nhn_best[model_num])
        + " hidden neurons"
    )

y_out_ensemble_mean = np.mean(y_out_ensemble, axis=0)
RMSE_ensemble_mean = rmse(y_out_ensemble_mean, y_test)
df_model.to_csv(str(data_dir) + f"/mlp/{trail}/model-config.csv")

plt.figure(figsize=(12, 8))

plt.subplot(241)
plt.scatter(len(RMSE_ensemble), RMSE_ensemble_mean, c="k", marker="*")
plt.scatter(range(len(RMSE_ensemble)), RMSE_ensemble)
plt.xlabel("Model #")
plt.ylabel("RMSE")
plt.title("Error")

plt.subplot(242)
plt.scatter(range(len(nhn_best)), nhn_best)
plt.xlabel("Model #")
plt.ylabel("# Hidden Neurons")
plt.title("Hidden Neurons")

plt.subplot(243)
plt.scatter(range(len(nhl_best)), nhl_best)
plt.xlabel("Model #")
plt.ylabel("# Hidden Layers")
plt.title("Hidden Layers")

plt.subplot(244)
plt.scatter(y_test, y_out_ensemble_mean)
# plt.plot((np.min(y_test),np.max(y_test)),'k--')
plt.xlabel("y_test")
plt.ylabel("y_model")
plt.title("Ensemble")

plt.subplot(212)
plt.plot(y_out_ensemble_mean)
plt.plot(np.array(y_test), alpha=0.5, color="tab:red")

plt.tight_layout()

plt.show()

saveIt = 0


plt.figure(figsize=(12, 5))
plt.plot(range(len(y_test)), y_test, label="Observations", zorder=0, alpha=0.3)
plt.plot(
    range(len(y_test)),
    np.transpose(y_out_ensemble[-1]),
    color="k",
    alpha=0.4,
    label="Individual Models",
    zorder=1,
)  # plot first ensemble member with a label
# plt.plot(range(len(y_test)),np.transpose(y_out_ensemble[1:]),color = 'k',alpha = 0.4,zorder=1) #plot remaining ensemble members without labels for a nicer legend
# plt.plot(range(len(y_test)),y_out_ensemble_mean,color = 'k',label = 'Ensemble',zorder=2, linewidth = 3)
plt.xlabel("Time", fontsize=20)
plt.ylabel("y", fontsize=20)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.title("MLP Model Results", fontsize=24)
plt.legend(fontsize=16, loc="best")
plt.xlim(0, 200)
plt.ylim(0, 1000)

plt.tight_layout()

plt.show()

# from scipy import stats
# for i in range(len(y_out_ensemble)):
#     print(i)
#     print('pearsonr: ' + str(np.round(stats.pearsonr(y_test, y_out_ensemble[i])[0],2)))
