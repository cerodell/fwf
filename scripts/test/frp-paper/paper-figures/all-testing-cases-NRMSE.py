#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import numpy as np
import xarray as xr
import pandas as pd
import seaborn as sns
import matplotlib

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from scipy import stats
from utils.stats import MBE, RMSE, MAE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir

matplotlib.rcParams.update({"font.size": 16})
plt.rc("font", family="sans-serif")
plt.rc("text", usetex=True)

save_fig = False
paper_fig = True
all_fire = True
mlp_test_case = "MLP_64U-Dense_64U-Dense_1U-Dense-Main"
method = "averaged-v19"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
persist = True

df = pd.read_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/all-cases-{method[-3:]}-persist-{persist}.csv"
)


df["mlp_avg"] = df["mlp_avg"] - df["mlp_avg"].min()


# Step 1: Define custom thresholds for fire intensity categories (adjust these as needed)
thresholds = [
    0,
    100,
    500,
    1000,
    np.inf,
]  # Custom thresholds for Low, Medium, High, Very High

# Step 2: Create custom labels programmatically based on the thresholds
labels = [
    f"{int(thresholds[i])}-{int(thresholds[i+1])} (MW)"
    if thresholds[i + 1] != np.inf
    else f"{int(thresholds[i])}+ (MW)"
    for i in range(len(thresholds) - 1)
]

# Step 3: Categorize the data based on the thresholds using pd.cut()
df["intensity_category"] = pd.cut(
    df["obs_avg"], bins=thresholds, labels=labels, include_lowest=True
)

# Step 4: Calculate RMSE for each data point
df["rmse"] = np.sqrt((df["mlp_avg"] - df["obs_avg"]) ** 2)

# Step 5: Group by intensity category and calculate the mean RMSE and count for each category
rmse_by_category = (
    df.groupby("intensity_category")
    .agg(rmse=("rmse", "mean"), count=("rmse", "size"))
    .reset_index()
)

# Step 6: Normalize RMSE (divide each mean RMSE by the maximum RMSE)
rmse_by_category["normalized_rmse"] = (
    rmse_by_category["rmse"] / rmse_by_category["rmse"].max()
)

# Print the count in each bin
print("Count in each bin:\n", rmse_by_category[["intensity_category", "count"]])

# Step 7: Plot normalized RMSE by fire intensity category (based on custom thresholds)
plt.figure(figsize=(8, 5))
bars = plt.bar(
    rmse_by_category["intensity_category"],
    rmse_by_category["normalized_rmse"],
    color="green",
)

# Step 8: Add count labels above the bars
for bar, count in zip(bars, rmse_by_category["count"]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{count}",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.xlabel("Fire Intensity Category")
plt.ylabel("Normalized RMSE")
plt.title("Normalized RMSE by Fire Intensity")
# plt.grid(True)
plt.show()


# Step 1: Define custom thresholds for fire intensity categories
thresholds = [
    0,
    100,
    500,
    1000,
    np.inf,
]  # Custom thresholds for Low, Medium, High, Very High

# Step 2: Create custom labels for the Fire Intensity Categories
labels = [
    f"{int(thresholds[i])}-{int(thresholds[i+1])}"
    if thresholds[i + 1] != np.inf
    else f"{int(thresholds[i])}+"
    for i in range(len(thresholds) - 1)
]

# Step 3: Categorize the data based on the thresholds using pd.cut()
df["intensity_category"] = pd.cut(
    df["obs_avg"], bins=thresholds, labels=labels, include_lowest=True
)

# Step 4: Calculate RMSE for each data point
df["rmse"] = np.sqrt((df["mlp_avg"] - df["obs_avg"]) ** 2)

# Step 5: Group by local hour and fire intensity category to calculate the mean RMSE for each hour
rmse_by_hour_category = (
    df.groupby(["local_hours", "intensity_category"])
    .agg(rmse=("rmse", "mean"))
    .reset_index()
)

# Step 6: Normalize RMSE by fire intensity category
rmse_by_hour_category["normalized_rmse"] = rmse_by_hour_category.groupby(
    "intensity_category"
)["rmse"].transform(lambda x: x / x.max())

# Step 7: Plot normalized RMSE by hour with multiple lines for each fire intensity category
plt.figure(figsize=(10, 6))

# Loop through each Fire Intensity Category and plot the RMSE by hour
for category in labels:
    subset = rmse_by_hour_category[
        rmse_by_hour_category["intensity_category"] == category
    ]
    plt.plot(
        subset["local_hours"],
        subset["normalized_rmse"],
        marker="o",
        label=f"Category {category}",
    )

# Labels and title
plt.xlabel("Local Hour")
plt.ylabel("Normalized RMSE")
plt.title("Normalized RMSE by Hour and Fire Intensity Category")
plt.legend(title="Fire Intensity Category")
plt.grid(True)

plt.show()
