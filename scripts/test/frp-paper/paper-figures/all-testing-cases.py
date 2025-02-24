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
method = "averaged-v20"
ml_pack = "tf"
target_vars = "FRP"
model_dir = str(data_dir) + f"/mlp/{ml_pack}/{method}/{target_vars}/{mlp_test_case}"
persist = True

df = pd.read_csv(
    f"/Users/crodell/fwf/data/ml-data/test-data/all-cases-{method[-3:]}-persist-{persist}.csv"
)


def setBold(txt):
    return r"$\bf{" + str(txt) + "}$"


var = "FRP"
if var.lower() == "fre":
    units = "(MJ)"
elif var.lower() == "frp":
    units = "(MW)"
OBS_FRP = df[f"obs_avg"]
MODELED_FRP = df[f"mlp_avg"]

print(df["obs_avg"].quantile(0.50))

mae = str(np.round(MAE(OBS_FRP, MODELED_FRP), 2))
rmse = np.round(RMSE(OBS_FRP, MODELED_FRP), 2)
r2 = np.round(r2_score(OBS_FRP, MODELED_FRP), 2)
r = np.round(stats.pearsonr(OBS_FRP, MODELED_FRP)[0], 2)

fig = plt.figure(figsize=(14, 5))
ax = fig.add_subplot(1, 2, 1)
sc = ax.scatter(MODELED_FRP, OBS_FRP, s=1, c=df["local_hours"], cmap="hsv")
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Local Hour", pad=0.01)
ax.set_xlabel(f"Modeled {var.upper()} {units}")
ax.set_ylabel(f"Observed {var.upper()} {units}")
ax.set_title(
    setBold("Fire")
    + " "
    + setBold("Radiative ")
    + " "
    + setBold("Power")
    + f"\n MAE: {mae} MW RMSE: {rmse} MW  "
    + r"$R^{2}$"
    + f": {r2}   r: {r}",
    fontsize=14,
)
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.set_yscale("log")
ax.set_ylim(0.2, 3500)
ax.set_xscale("log")
ax.set_xlim(0.2, 3500)


var = "FRE"
if var.lower() == "fre":
    units = "(MJ)"
elif var.lower() == "frp":
    units = "(MW)"
OBS_FRP = df[f"obs_sum"]
MODELED_FRP = df[f"mlp_sum"]

print(f"{float(df['obs_sum'].quantile(0.50)):.2e}")

mae = str(np.round(MAE(OBS_FRP, MODELED_FRP), 2))
rmse = np.round(RMSE(OBS_FRP, MODELED_FRP), 2)
r2 = np.round(r2_score(OBS_FRP, MODELED_FRP), 2)
r = np.round(stats.pearsonr(OBS_FRP, MODELED_FRP)[0], 2)
if var == "FRP":
    min_lim = -100
    max_lim = np.max(np.stack([OBS_FRP, MODELED_FRP])) - min_lim
else:
    min_lim = -5e5
    max_lim = np.max(np.stack([OBS_FRP, MODELED_FRP])) - min_lim
ax = fig.add_subplot(1, 2, 2)
sc = ax.scatter(MODELED_FRP, OBS_FRP, s=1, c=df["local_hours"], cmap="hsv")
cbar = plt.colorbar(sc, ax=ax, orientation="vertical", label="Local Hour", pad=0.01)
ax.set_xlabel(f"Modeled {var.upper()} {units}")
ax.set_ylabel(f"Observed {var.upper()} {units}")
fre_mae = f"{float(mae):.2e}"
fre_rmse = f"{float(rmse):.2e}"
fre_r2 = f"{float(r2):.2f}"
fre_r = f"{float(r):.2f}"
ax.set_title(
    setBold("Fire")
    + " "
    + setBold("Radiative ")
    + " "
    + setBold("Energy")
    + f"\n MAE: {fre_mae} MJ   RMSE: {fre_rmse} MJ "
    + r"$R^{2}$"
    + f": {fre_r2}   r: {fre_r}",
    fontsize=14,
)
ax.axline((0, 0), slope=1, color="k", linestyle="--", lw=0.5)
ax.set_yscale("log")
ax.set_ylim(1000, max_lim)
ax.set_xscale("log")
ax.set_xlim(1000, max_lim)

if save_fig == True:
    fig.savefig(
        str(data_dir) + f"/images/frp-paper/all-testing-cases-stats-{method[-3:]}.png",
        bbox_inches="tight",
        dpi=240,
    )

if paper_fig == True:
    fig.savefig(
        f"/Users/crodell/ams-frp/all-testing-cases-stats-{method[-3:]}.png",
        bbox_inches="tight",
        dpi=240,
    )


# # Assuming OBS_FRP and MODELED_FRP are defined
# fig, ax = plt.subplots(figsize=(10, 6))

# # Logarithmic scale for better visualization
# ax.set_yscale('log')

# # Plotting the boxplots
# sns.boxplot(data=[OBS_FRP, MODELED_FRP], ax=ax, showfliers=False)

# # Overlay with individual points
# sns.stripplot(data=[OBS_FRP, MODELED_FRP], ax=ax, color="0.3", size=2, jitter=True)

# # Set labels
# ax.set_xticklabels(['OBS', 'MLP'])
# ax.set_ylabel("FRP (MW)")
# ax.set_title("Comparison of Observed and Modeled FRP")

# # Set y-axis limits (adjust as necessary)
# ax.set_ylim(0.1, 5000)

# plt.show()
