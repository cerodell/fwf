#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import numpy as np
import xarray as xr
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from netCDF4 import Dataset
from wrf import getvar, get_cartopy


from utils.ml_data import MLDATA
from context import data_dir, root_dir


tree_test = False
fit_test = False
cor_test = True
dist_test = True
num_hidden_neurons = 32
num_hidden_layers = 4
solver = "adam"  # use stochastic gradient descent as an optimization method (weight updating algorithm)
activation = "relu"
learning_rate_init = 0.01
batch_size = 32
max_iter = 1500  # max number of epochs to run
early_stopping = True  # True = stop early if validation error begins to rise
validation_fraction = 0.1  # fraction of training data to use as validation
save_dir = Path(str(data_dir) + "/images/rave/mlp/features/")
save_dir.mkdir(parents=True, exist_ok=True)
# Configuration parameters
config = dict(
    method="averaged-v7",
    feature_vars=[
        "SAZ_sin",
        "SAZ_cos",
        "ASPECT_sin",
        "ASPECT_cos",
        "HGT",
        "GS",
        # "U-lat_sin",
        "U-lat_sin-Total_Fuel_Load",
        "U-lat_cos-Total_Fuel_Load",
        "U-lon_sin-Total_Fuel_Load",
        "U-lon_cos-Total_Fuel_Load",
        # "U",
        # "Total_Fuel_Load",
        "R-hour_sin-Total_Fuel_Load",
        "R-hour_cos-Total_Fuel_Load",
        # "R-hour_cos",
        # "R-lat_sin",
        # "R-lat_cos",
        # "R-lon_sin",
        # "R-lon_cos",
        # "U-lat_sin",
        # "U-lat_cos",
        # "U-lon_sin",
        # "U-lon_cos",
    ],
    scaler_type="standard",  ##robust or standard minmax
    transform=True,
    min_fire_size=1000,
    package="tf",
    model_type="MLP",
    main_cases=True,
    shuffle_data=True,
    feature_engineer=True,
    filter_std=False,
)
# config["n_features"] = len(config["keep_vars"])


mlD = MLDATA(config=config)
df = mlD.open_ml_ds()
df_unique = df.groupby("id").first().reset_index()


# Open the NetCDF file
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_d01_2023-04-20_00:00:00")
# Get the sea level pressure
slp = getvar(ncfile, "slp")
# Get the cartopy mapping object
cart_proj = get_cartopy(slp)


## bring in state/prov boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category="cultural",
    name="admin_1_states_provinces_shp",
    scale="50m",
    facecolor="none",
)


# %%


lat, lon, area_ha = [], [], []
for ID, group in df.groupby("id"):
    lat.append(float(group["lats"].iloc[0]))
    lon.append(float(group["lons"].iloc[0]))
    area_ha.append(float(group["area_ha"].iloc[0]))

from sklearn.preprocessing import MinMaxScaler

# Normalize sizes to a specified range (e.g., 20 to 200)
scaler = MinMaxScaler(feature_range=(2, 400))
normalized_sizes = scaler.fit_transform(np.array(area_ha).reshape(-1, 1)).flatten()


# Create a figure
fig = plt.figure(figsize=(14, 8))
# Set the GeoAxes to the projection used by WRF
ax = plt.axes(projection=cart_proj)

ax.add_feature(cfeature.OCEAN, color="white", zorder=2)
ax.add_feature(states_provinces, linewidth=0.5, edgecolor="black", zorder=5)
ax.coastlines("50m", linewidth=0.8, zorder=5)

## plot wx stations locations
sc = ax.scatter(
    lon,
    lat,
    cmap="viridis",
    vmin=0,
    vmax=1,
    zorder=10,
    alpha=1,
    s=normalized_sizes,
    transform=crs.PlateCarree(),
    linewidth=0.4,
    edgecolors="black",
)


# norm_vars_list = ['R', 'U', 'S', 'Live_Wood', 'Dead_Wood', 'Dead_Foliage','Total_Fuel_Load', 'HGT', 'GS']
# df_i = df[norm_vars_list]
# var_maxs = np.ceil(df_i.max())
# var_mins = np.floor(df_i.min())
# for var in norm_vars_list:
#     config.update({var+'_max': int(var_maxs[var])})
#     config.update({var+'_min': int(var_mins[var])})
#     df[var] = (df[var] - var_mins[var]) / (var_maxs[var] - var_mins[var])


# dfs = df
# feature_names=[
#     # "Live_Wood",
#     # "Dead_Wood",
#     # "Live_Leaf",
#     # "Dead_Foliage",
#     "R-hour_sin-Live_Wood",
#     "R-hour_cos-Live_Wood"
#     # "R-lat_sin",
#     # "R-lat_cos",
#     # "R-lon_sin",
#     # "R-lon_cos",
#     # "U-lat_sin",
#     # "U-lat_cos",
#     # "U-lon_sin",
#     # "U-lon_cos",
# ]


# for feature in feature_names:
#     # Split the feature name to identify the components
#     components = feature.split('-')

#     components_array  =[]
#     for comp in components:
#         components_array.append(dfs[comp].values)

#     # Assign the new feature to the dataset
#     dfs[feature] = np.prod(components_array, axis = 0)

# test = dfs[feature].values
# test2 = dfs['R'].values * dfs['hour_cos'].values * dfs['Live_Wood'].values


# # df_test = df[df['Live_Wood']<0.01]
# plt.scatter(df["R-hour_sin"] * df["Live_Leaf"], df["FRP"])
# plt.scatter(df["R-hour_sin_Live_Wood"], df["R-hour_cos_Live_Wood"])

y = df["FRP"]
df = df[config["keep_vars"]]

# %%
if cor_test == True:
    # get correlations of each features in dataset
    corrmat = df.corr()
    top_corr_features = corrmat.index
    plt.figure(figsize=(20, 20))
    # plot heat map
    g = sns.heatmap(
        df[top_corr_features].corr(), annot=True, cmap="seismic", vmin=-1, vmax=1
    )
    plt.savefig(
        str(save_dir) + "/correlation_heatmap.png",
        dpi=300,
        format="png",
        bbox_inches="tight",
    )


# if dist_test == True:
#     plt.figure(figsize=(20, 20))
#     sns.pairplot(df, diag_kind="kde")
#     plt.savefig(
#         str(save_dir) + "/distributions.png", dpi=300, format="png", bbox_inches="tight"
#     )


# # %%
# if tree_test == True:
#     trees = ExtraTreesClassifier(max_depth=3, n_estimators=10, random_state=0)
#     trees.fit(X,y)
#     print(trees.feature_importances_) #use inbuilt class feature_importances of tree based classifiers
#     #plot graph of feature importances for better visualization
#     feat_importances = pd.Series(trees.feature_importances_, index=X.columns)
#     feat_importances.nlargest(10).plot(kind='barh')
#     plt.show()

#     bestfeatures = SelectKBest(score_func=chi2, k=10)
#     fit = bestfeatures.fit(X,y)
#     dfscores = pd.DataFrame(fit.scores_)
#     dfcolumns = pd.DataFrame(X.columns)
#     #concat two dataframes for better visualization
#     featureScores = pd.concat([dfcolumns,dfscores],axis=1)
#     featureScores.columns = ['Specs','Score']  #naming the dataframe columns
#     print(featureScores.nlargest(10,'Score'))  #print 10 best features

# %%
# if fit_test == True:
#     X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)

#     scaler = StandardScaler().fit(X)
#     X_train = scaler.transform(X_train)
#     X_test = scaler.transform(X_test)

#     hidden_layer_sizes = (num_hidden_neurons, num_hidden_layers)
#     model = MLPRegressor(
#         hidden_layer_sizes=hidden_layer_sizes,
#         verbose=False,
#         max_iter=max_iter,
#         early_stopping=early_stopping,
#         validation_fraction=validation_fraction,
#         batch_size=batch_size,
#         solver=solver,
#         activation=activation,
#         learning_rate_init=learning_rate_init,
#     )

#     model.fit(X_train, y_train)  # train the model
#     score = model.score(X_test, y_test)  # Evaluate model performance with reduced feature set
#     print("Model accuracy:", score)
#     # Permutation importance
#     result = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42, n_jobs=-1)

#     # Display importance
#     feature = list(X.head())
#     for i in range(X.shape[1]):
#         print(f"Feature {feature[i]}: Importance {result.importances_mean[i]:.4f} ± {result.importances_std[i]:.4f}")

#     # Consider a reduced feature set based on importance
#     important_features = ['hour', 'HFI', 'FWI', 'HGT', 'month']  # Example of focusing on more impactful features

#     # Select only the important features from your dataset
#     X_train_reduced = X_train[:, [keep_vars.index(feat) for feat in important_features]]
#     X_test_reduced = X_test[:, [keep_vars.index(feat) for feat in important_features]]

#     # Re-train model to see the impact
#     model.fit(X_train_reduced, y_train)
#     score = model.score(X_test_reduced, y_test)  # Evaluate model performance with reduced feature set
#     print("Model accuracy with reduced features:", score)

#     # Assume X is your feature set and y is the target
#     # Select the top 5 features based on their F-statistic
#     selector = SelectKBest(f_regression, k=9)
#     X_new = selector.fit_transform(X, y)

#     # Get the mask of the selected features - this can help you find which features were selected
#     selected_features = selector.get_support(indices=True)
#     print("Selected features:", [keep_vars[i] for i in selected_features])
