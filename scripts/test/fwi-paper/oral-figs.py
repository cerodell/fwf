import context

import json
import numpy as np
import pandas as pd
from pathlib import Path

import matplotlib.pyplot as plt

from context import data_dir, root_dir

# plt.rc("font", family="sans-serif")
# plt.rc("text", usetex=True)
plt.rcParams.update({"font.size": 24})

model = "wrf"
trail_name = "04"

with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)
save_dir = str(data_dir) + "/images/oral/"


var = "fwi"
day1_df = pd.read_csv(
    str(data_dir) + f"/intercomp/{trail_name}/{model}/{var}-stats.csv"
)
day1_df["domain"] = day1_df["domain"].str.strip()
stdev_obs = float(day1_df[day1_df["domain"] == "obs"]["std_dev"])

day2_df = pd.read_csv(
    str(data_dir) + f"/intercomp/{trail_name}/{model}_day2/{var}-stats.csv"
)


# %%

# Sample data
models = [f"daily", "h1200", "h1600", "max"]
custom_labels = ["DFWI", "HFWI h12", "HFWI h16", "HFWI Max"]
correlation_coefficients = [
    float(day1_df[day1_df["domain"] == method]["r"].iloc[0])
    for method in [f"{domain}-{item}" for item in models]
]
mean_bias_errors = [
    float(day1_df[day1_df["domain"] == method]["mbe"].iloc[0])
    for method in [f"{domain}-{item}" for item in models]
]
# Create a figure with subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)

# Bar chart for Correlation Coefficients
axes[0].bar(
    models, correlation_coefficients, alpha=0.7, label="Correlation Coefficient"
)
axes[0].set_ylim(0, 1)  # Correlation coefficient range
axes[0].set_title("Correlation Coefficients")
# axes[0].set_ylabel('Correlation Coefficient')
axes[0].set_xticklabels(
    custom_labels, rotation=30, ha="right"
)  # Rotate labels for readability
axes[0].grid(axis="y", linestyle="--", alpha=0.7)

# Bar chart for Mean Bias Errors
axes[1].bar(
    models, mean_bias_errors, alpha=0.7, color="orange", label="Mean Bias Error"
)
axes[1].axhline(0, color="black", linewidth=0.8, linestyle="--")  # Reference line at 0
axes[1].set_title("Mean Bias Errors")
# axes[1].set_ylabel('Mean Bias Error')
axes[1].grid(axis="y", linestyle="--", alpha=0.7)
axes[1].set_xticklabels(
    custom_labels, rotation=30, ha="right"
)  # Rotate labels for readability

# Adjust layout for better spacing
plt.tight_layout()

# Show the combined plot
plt.savefig(str(save_dir) + f"/bar-chart-stats.png", dpi=250, bbox_inches="tight")

# %%
