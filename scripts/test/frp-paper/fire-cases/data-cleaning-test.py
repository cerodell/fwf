#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib

from utils.ml_data import MLDATA
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from sklearn.utils import shuffle


method = "averaged-v12"
years = ["2021", "2022", "2023"]
feature_vars = [
    "ASPECT_sin",
    "ASPECT_cos",
    "HGT",
    "GS",
    "R-hour_sin-Total_Fuel_Load",
    "R-hour_cos-Total_Fuel_Load",
    "U-lat_sin-Total_Fuel_Load",
    "U-lon_sin-Total_Fuel_Load",
    "U-lat_cos-Total_Fuel_Load",
    "U-lon_cos-Total_Fuel_Load",
]


target_vars = ["FRP"]
feature_scaler_type = "minmax"  ##robust or standard minmax
target_scaler_type = True  ##robust or standard minmax
transform = True
package = "tf"
model_type = "MLP"
smoothing = False
main_cases = False
shuffle_data = False
feature_engineer = False
min_fire_size = 1000  ## hectors,
burn_time = (48,)
filter_std = True
wrf = False
user_config = {"method": method, "min_fire_size": min_fire_size, "burn_time": burn_time}
mlD = MLDATA(config=user_config)
df = mlD.open_ml_ds()


# phi_sin = -np.pi

# df["hour_sin"] = (
#     0.1 + (np.sin((2 * np.pi * df["solar_hour"] / 24) + phi_sin) + 1) * 0.45
# )
# df["hour_cos"] = (
#     0.1 + (np.cos((2 * np.pi * df["solar_hour"] / 24) + phi_sin) + 1) * 0.45
# )


# df["hour_sin"] =  df["hour_sin"]**2
# df["hour_cos"] =   df["hour_cos"]**2


og_len = len(df)
if transform == True:
    df["FRP"] = np.log1p(df["FRP"])
    df["FRE"] = np.log1p(df["FRE"])
    # df['R'] =df['R']**2
    # df['S'] = np.log1p(df['S'])
    # df['U'] = np.log1p(df['U'])
    # df['Total_Fuel_Load'] = np.log1p(df['Total_Fuel_Load'])
    # df['CLIMO_FRP'] = df['CLIMO_FRP'] / df['CLIMO_FRP'].max()
plt.figure()
# df['FRP'].plot.hist(bins =200)
if filter_std:
    ################ FRP ###################
    frp_max_threshold = 1000
    frp_min_threshold = 1
    print(
        f'Number pf FRP obs above {frp_max_threshold} MW {len(df[np.expm1(df["FRP"]) > frp_max_threshold])}'
    )
    print(
        f'Number pf FRP obs below {frp_min_threshold} MW {len(df[np.expm1(df["FRP"]) < frp_min_threshold])}'
    )
    print("-------------------------------------")

    for var in ["FRP"]:
        print("==================================")
        print(f"MAX {var}: ", np.expm1(df[var]).max())
        print(f"MIN {var}: ", np.expm1(df[var]).min())
        mean_frp = df[var].mean()
        std_frp = df[var].std()
        threshold = 3
        # Define the lower and upper bounds
        lower_bound = mean_frp - threshold * std_frp
        upper_bound = mean_frp + threshold * std_frp
        # Filter the DataFrame
        df = df[(df[var] >= lower_bound) & (df[var] <= upper_bound)]
        print(f"NEW MAX {var}: ", np.expm1(df[var]).max())
        print(f"NEW MIN {var}: ", np.expm1(df[var]).min())
    print("-------------------------------------")
    print(
        f'Number pf FRP obs above {frp_max_threshold} MW {len(df[np.expm1(df["FRP"]) > frp_max_threshold])}'
    )
    print(
        f'Number pf FRP obs below {frp_min_threshold} MW {len(df[np.expm1(df["FRP"]) < frp_min_threshold])}'
    )


# plt.figure()
# df['FRP'].plot.hist(bins =200)

# df['CLIMO_FRP'] = np.log1p(df['CLIMO_FRP'])
print(f"Percentage of data dropped:  {100-((len(df)/og_len)*100)}")


for feature in feature_vars:
    # Split the feature name to identify the components
    components = feature.split("-")
    components_array = []
    for comp in components:
        components_array.append(df[comp].values)

    # Assign the new feature to the dataset
    try:
        df[feature] = np.prod(components_array, axis=0)
    except:
        if wrf == False:
            df[feature] = (
                ("time", "y", "x"),
                np.prod(components_array, axis=0),
            )
        elif wrf == True:
            df[feature] = (
                ("time", "south_north", "west_east"),
                np.prod(components_array, axis=0),
            )

# if transform == True:
# df['R-hour_sin-Total_Fuel_Load'] = np.log1p(df['R-hour_sin-Total_Fuel_Load'])

print(
    stats.pearsonr(
        df["ASPECT"],
        df["SAZ"],
    )[0]
)

# print(stats.pearsonr(
#            df['FRP'],
#            df['R-CLIMO_FRP-Total_Fuel_Load'],
#         )[0])

print(
    stats.pearsonr(
        df["FRP"],
        df["R-hour_sin-Total_Fuel_Load"],
    )[0]
)

print("Number of fires: ", len(np.unique(df["id"].values)))
user_config["num_fire"] = str(len(np.unique(df["id"].values)))
IDS = np.unique(df["id"].values)

# Split into 70% train and 30% remaining
train_ids, remaining_ids = train_test_split(IDS, test_size=0.30, random_state=100)

# Split the remaining 30% into 15% validation and 15% test
val_ids, test_ids = train_test_split(remaining_ids, test_size=0.50, random_state=100)

# Verify the splits
print(f"Training IDs: {len(train_ids)}")
print(f"Validation IDs: {len(val_ids)}")
print(f"Testing IDs: {len(test_ids)}")

df_train = df[df["id"].isin(train_ids)]
unique_train_df = df_train.drop_duplicates(subset="id", keep="first")
train_fires_array = np.stack(
    [
        unique_train_df["id"].values,
        unique_train_df["local_time"].dt.year.values,
    ]
)

df_val = df[df["id"].isin(val_ids)]
unique_val_df = df_val.drop_duplicates(subset="id", keep="first")
val_fires_array = np.stack(
    [
        unique_val_df["id"].values,
        unique_val_df["local_time"].dt.year.values,
    ]
)

df_test = df[df["id"].isin(test_ids)]
unique_test_df = df_test.drop_duplicates(subset="id", keep="first")
test_fires_array = np.stack(
    [
        unique_test_df["id"].values,
        unique_test_df["local_time"].dt.year.values,
    ]
)

print(f"Training percentage: {np.round(100*len(df_train)/len(df),1)}")
print(f"Validation percentage: {np.round(100*len(df_val)/len(df),1)}")
print(f"Testing percentage: {np.round(100*len(df_test)/len(df),1)}")
user_config["num_fire_train"] = str(len(unique_train_df.values))
user_config["num_fire_val"] = str(len(unique_val_df.values))
user_config["num_fire_test"] = str(len(unique_test_df.values))
user_config["pre_fire_train"] = np.round(100 * len(df_train) / len(df), 1)
user_config["pre_fire_val"] = np.round(100 * len(df_val) / len(df), 1)
user_config["pre_fire_test"] = np.round(100 * len(df_test) / len(df), 1)


# Function to add perturbations
def add_perturbations(df, scale):
    df = df_train.loc[df_train["FRP"] > np.log1p(500)]
    df = df[feature_vars + target_vars]
    perturbations = np.random.normal(loc=0, scale=scale, size=df.shape).astype(
        "float32"
    )
    perturbed_df = df.copy()
    perturbed_df = pd.DataFrame(
        df.values + perturbations, columns=feature_vars + target_vars
    )
    return perturbed_df


if transform == True:
    # cold_fires = df_train.loc[df_train["FRP"] < np.log1p(1)]
    # cool_fires = df_train.loc[df_train["FRP"] < np.log1p(10)]
    scale = 0.01
    warm_fires = add_perturbations(df_train.loc[df_train["FRP"] > 4], scale)
    hot_fires = add_perturbations(df_train.loc[df_train["FRP"] > 5], scale)
    hotter_fires = add_perturbations(df_train.loc[df_train["FRP"] > 6], scale)
    # hotter_still_fire = add_perturbations(df_train.loc[df_train["FRP"] > np.log1p(2000)],scale)
    # hottest_fires = add_perturbations(df_train.loc[df_train["FRP"] > np.log1p(3000)],scale)
else:
    # cold_fires = df_train.loc[df_train["FRP"] < 1]
    # cool_fires = df_train.loc[df_train["FRP"] < 10]
    warm_fires = add_perturbations(df_train.loc[df_train["FRP"] > 500], 0.01)
    hot_fires = add_perturbations(df_train.loc[df_train["FRP"] > 1000], 0.01)
    hotter_fires = add_perturbations(df_train.loc[df_train["FRP"] > 1500], 0.01)
    hotter_still_fire = add_perturbations(df_train.loc[df_train["FRP"] > 2000], 0.01)
    hottest_fires = add_perturbations(df_train.loc[df_train["FRP"] > 3000], 0.01)

# if transform == True:
#     # cold_fires = df_train.loc[df_train["FRP"] < np.log1p(1)]
#     # cool_fires = df_train.loc[df_train["FRP"] < np.log1p(10)]
#     warm_fires = df_train.loc[df_train["FRP"] > np.log1p(500)]
#     hot_fires = df_train.loc[df_train["FRP"] > np.log1p(1000)]
#     hotter_fires = df_train.loc[df_train["FRP"] > np.log1p(1500)]
#     hotter_still_fire = df_train.loc[df_train["FRP"] > np.log1p(2000)]
#     hottest_fires = df_train.loc[df_train["FRP"] > np.log1p(3000)]
# else:
#     # cold_fires = df_train.loc[df_train["FRP"] < 1]
#     # cool_fires = df_train.loc[df_train["FRP"] < 10]
#     warm_fires = df_train.loc[df_train["FRP"] > 500]
#     hot_fires = df_train.loc[df_train["FRP"] > 1000]
#     hotter_fires = df_train.loc[df_train["FRP"] > 1500]
#     hotter_still_fire = df_train.loc[df_train["FRP"] > 2000]
#     hottest_fires = df_train.loc[df_train["FRP"] > 3000]

df_train = pd.concat(
    [
        df_train,
        # cold_fires,
        # cool_fires,
        warm_fires,
        hot_fires,
        hotter_fires,
        # hotter_still_fire,
        # hottest_fires,
    ]
)
df_train.reset_index(drop=True, inplace=True)


X_train = df_train[feature_vars].copy()
X_val = df_val[feature_vars].copy()
X_test = df_test[feature_vars].copy()


y_train = df_train[target_vars]
y_val = df_val[target_vars]
y_test = df_test[target_vars]

if shuffle_data:
    X_train, y_train = shuffle(X_train, y_train, random_state=42)

# Scale features
if feature_scaler_type == "standard":
    feature_scaler = StandardScaler().fit(X_train)
elif feature_scaler_type == "robust":
    feature_scaler = RobustScaler().fit(X_train)
elif feature_scaler_type == "minmax":
    feature_scaler = MinMaxScaler().fit(X_train)

if target_scaler_type == True:
    # target_scaler = RobustScaler().fit(y_train)
    user_config["FRP_MAX"] = float(y_train["FRP"].max())
    # user_config["FRE_MAX"] =float(y_train['FRE'].max())
    y_train = y_train / y_train.max()


X_train = feature_scaler.transform(X_train)
X_val = feature_scaler.transform(X_val)
X_test = feature_scaler.transform(X_test)

# y_train = target_scaler.transform(y_train)
y_train_df = pd.DataFrame(y_train, columns=target_vars)
# y_train_df.plot.hist(bins=200)


feature_scaler = feature_scaler
# target_scaler = target_scaler

train_fires_array = train_fires_array
val_fires_array = val_fires_array
test_fires_array = test_fires_array
length_of_training = len(y_train)
X_val = X_val
y_val = y_val
df_val = df_val

X_train_df = pd.DataFrame(X_train, columns=feature_vars)
X_val_df = pd.DataFrame(X_val, columns=feature_vars)
X_test_df = pd.DataFrame(X_test, columns=feature_vars)


print(
    stats.pearsonr(
        y_val["FRP"],
        X_val_df["R-hour_sin-Total_Fuel_Load"],
    )[0]
)

# for var in list(X_train_df):
#     fig = plt.figure()
#     ax = fig.add_subplot(1,1,1)
#     X_train_df[var].plot.hist(ax = ax, bins =200)
#     ax.set_title(var.title())
