#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import numpy as np
import xarray as xr
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest, f_regression

from sklearn.metrics import r2_score
from scipy import stats
from utils.stats import MBE
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
config = dict(
    keep_vars=[
        "R",
        "U",
        "Live_Wood",
        "Dead_Wood",
        "Live_Leaf",
        "Dead_Foliage",
        "hour_sin",
        "hour_cos",
    ]
    # filter_std = 1
)

mlD = MLDATA(config=config)
df = mlD.open_ml_ds()


y = df["FRP"]
X = df[config["keep_vars"]]

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


if dist_test == True:
    plt.figure(figsize=(20, 20))
    sns.pairplot(df, diag_kind="kde")
    plt.savefig(
        str(save_dir) + "/distributions.png", dpi=300, format="png", bbox_inches="tight"
    )


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
