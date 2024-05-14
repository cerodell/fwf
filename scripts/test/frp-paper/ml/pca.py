import context
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from context import data_dir


import context
import salem
import joblib
import numpy as np
import xarray as xr
import pandas as pd

import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from context import data_dir, root_dir


year = "2021"
spatially_averaged = True
norm_fwi = True
keep_vars = [
    "NFWI",
    "FWI",
    "FFMC",
    "HFI",
    "LAI",
    "NDVI",
    "HGT",
    "GS",
    "Live_Leaf",
    "Live_Wood",
    "Dead_Foliage",
    "Dead_Wood",
    "hour",
    "month",
]


filein = f"/Volumes/WFRT-Ext23/mlp-data/{year}-fires-all"
if spatially_averaged == True:
    filein += "-spatially-averaged"
if norm_fwi == True:
    filein += "-norm-fwi"
df = xr.open_dataset(filein + ".nc").to_dataframe().reset_index()


df["local_time"] = pd.to_datetime(df["time"]) - pd.to_timedelta(
    df["ZoneST"].astype(int), unit="h"
)

df["hour"] = df["local_time"].dt.hour
df["month"] = df["local_time"].dt.month

df["hour"] = (df["hour"] - 0) / (24 - 0)
df["month"] = (df["month"] - 1) / (12 - 1)
df["FFMC"] = (df["FFMC"] - 0) / (101 - 0)
df["HFI"] = (df["HFI"] - 0) / (df["HFI"].max() - 0)

df.loc[df["NFWI"] < 0, "NFWI"] = 0
df = df.drop(df[df["NFWI"] > 50].index)

for var in [
    "NFWI",
    "LAI",
    "FWI",
    "NDVI",
    "HGT",
    "GS",
    "Live_Leaf",
    "Live_Wood",
    "Dead_Foliage",
    "Dead_Wood",
]:
    df[var] = (df[var] - df[var].min()) / (df[var].max() - df[var].min())


df = df[keep_vars]
pca = PCA(n_components=3)
PCs = pca.fit_transform(df)
eigvecs = pca.components_
fracVar = pca.explained_variance_ratio_


n_modes = np.shape(df)[1]

fig = plt.figure(figsize=(8, 6))
for i in range(3):
    ax = fig.add_subplot(
        3,
        2,
        2 * i + 1,
        xticks=np.arange(0, n_modes),
        xticklabels=list(df),
        ylabel="e" + str(i + 1),
        title="variance explained = " + str(round(fracVar[i] * 100, 2)) + "%",
    )
    ax.set_xticklabels(ax.get_xticks(), rotation=45)
    ax.plot(eigvecs[i], marker="o")
    ax.set_xticklabels(list(df), rotation=45, ha="right")
    ax = fig.add_subplot(3, 2, 2 * i + 2, ylabel="PC" + str(i + 1))
    ax.scatter(np.arange(len(PCs.T[i])), PCs.T[i], marker="o", s=1)

plt.tight_layout()
