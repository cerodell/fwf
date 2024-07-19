#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import numpy as np
import xarray as xr
import pandas as pd
from scipy import stats

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from datetime import datetime
from utils.ml_data import MLDATA

from context import data_dir, root_dir

# Mark the start time for the run
startTime = datetime.now()

# Configuration parameters
keep_vars = ["FRP", "HFI", "S", "ISI", "W", "H", "T"]
scaler_type = "robust"  ##robust or standard or minmax


# Initialize MLP model and load dataset
mlD = MLDATA(config={"method": f"averaged-v9"})
df = mlD.open_ml_ds()

df["FRP_OG"] = df["FRP"]
df["FRR_OG"] = df["FRE"]

df["FRP"] = np.log1p(df["FRP"])
df["FRE"] = np.log1p(df["FRE"])


# # Scale features
# if self.feature_scaler_type == "standard":
#     feature_scaler = StandardScaler().fit(X_train)
# elif self.feature_scaler_type == "robust":
#     feature_scaler = RobustScaler().fit(X_train)
# elif self.feature_scaler_type == "minmax":
#     feature_scaler = MinMaxScaler().fit(X_train)


print(
    stats.pearsonr(
        df["FRE"],
        df["R"],
    )[0]
)
# print('--------------------------------')
# df['Total_Fuel_Load_NORM'] = df['Total_Fuel_Load'] / df['Total_Fuel_Load'].max()
# df['S_NORM'] = df['S'] / df['S'].max()

# df["FRP_LOG"] = np.log1p(df["FRP"])
# df["FRE_LOG"] = np.log1p(df["FRE"])

# df["OFFSET_NORM"].plot.hist(bins=200)

# df['eng_feature'] = df['Total_Fuel_Load'] * df['S'] * df['OFFSET_NORM']
# df['eng_feature1'] = df['Total_Fuel_Load'] * df['S'] * df['hour_sin']

df["FRP"].iloc[:200].plot()

df_fire = df[df["id"] == 26418461]
# df = df.set_index(['Datetime'])
df_fire = df_fire.set_index(pd.DatetimeIndex(df_fire["time"]))
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
df_fire["eng_feature"].plot(ax=ax, label="Product")
df_fire["eng_feature1"].plot(ax=ax, label="Weighted")
ax.legend()


df_fire["FRP"].plot()


df_fire


# X = df[keep_vars]
# X = X.loc[X["HFI"] > 100]
# X = X.loc[X["FRP"] < 4000]

# # X_copy = X.copy()
# sns.pairplot(X, diag_kind="kde")


# X["HFI"] = np.log1p(X["HFI"])
# X["FRP"] = np.log1p(X["FRP"])
# X["S"] = np.log1p(X["S"])
# X["ISI"] = np.log1p(X["ISI"])
# X["W"] = np.log1p(X["W"])

# sns.pairplot(X, diag_kind="kde")

# # Scale features
# if scaler_type == "standard":
#     scaler = StandardScaler().fit(X)
# elif scaler_type == "robust":
#     scaler = RobustScaler().fit(X)
# elif scaler_type == "minmax":
#     scaler = MinMaxScaler().fit(X)

# X_scaled = scaler.transform(X)
# X_copy["HFI"] = X_scaled[:, 0]
# X_copy["NDVI"] = X_scaled[:, 1]
# X_copy["LAI"] = X_scaled[:, 2]
# X_copy["FRP"] = X_scaled[:, 3]

# sns.pairplot(X_copy, diag_kind="kde")
