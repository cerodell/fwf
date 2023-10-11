import context
import json

import numpy as np
import xarray as xr
import pandas as pd
from scipy import stats
from pathlib import Path
import zentables as zen


from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


#################### OPEN FILES ####################

## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

# r_value, case, method = [], [], []
daily, case, hourly, dates = [], [], [], []
for case_study in case_dict:
    print(case_study)
    case_info = case_dict[case_study]

    domain = case_info["domain"]
    interp_grid_ds = xr.open_dataset(
        str(data_dir)
        + f"/frp/analysis/{domain}/{case_study.replace('_','-')}-interp-grid.nc"
    )

    study_range = interp_grid_ds.Time.values
    start_save = pd.to_datetime(study_range[0]).strftime("%b %d %Y")
    stop_save = pd.to_datetime(study_range[-1]).strftime("%b %d %Y")

    def set_axis_postion(ax, label):
        ax.set_ylabel(label, fontsize=16)
        ax.yaxis.label.set_color(ax.get_lines()[0].get_color())
        tkw = dict(size=4, width=1.5, labelsize=14)
        ax.tick_params(
            axis="y",
            colors=ax.get_lines()[0].get_color(),
            **tkw,
        )
        # ax.grid(True)
        ax.grid(which="major", axis="x", linestyle="--", zorder=2, lw=0.3)

    # ############## End FRP on wrf grid plot ###################

    hfwi = interp_grid_ds["S"].values[1]
    hfrp = interp_grid_ds["FRP"].values[0]
    dfwi = interp_grid_ds["S"].values[0]
    pearsonr_h_interp_final = stats.pearsonr(hfwi, hfrp)
    pearsonr_d_interp_final = stats.pearsonr(dfwi, hfrp)

    hourly.append(pearsonr_h_interp_final[0])
    daily.append(pearsonr_d_interp_final[0])
    # r_value.append(pearsonr_h_interp_final[0])
    # r_value.append(pearsonr_d_interp_final[0])
    # method.append('hourly')
    # method.append('daily')
    case.append(case_study.replace("_", " ").upper())
    dates.append(f"{start_save} - {stop_save}")
    # case.append(case_study)

# merged_df = pd.DataFrame({
#     "r_value": r_value,
#     "method": method,
#     "case": case
# })
merged_df = pd.DataFrame(
    {"hourly": hourly, "daily": daily, "dates": dates, "case": case}
)
merged_df = merged_df[merged_df.hourly > 0.3]

merged_df.reset_index(drop=True, inplace=True)
merged_df = merged_df.round(2)
# grouped_df = merged_df.groupby('var')
pivot_df = merged_df.pivot_table(
    index=["case", "dates"],
    # columns=["dates"],
    # values="Order ID",
    # aggfunc="count",
    margins=False,
)
pivot_df.to_dict()

# pivot_df = pivot_df.reindex(index=case, level=0)

pivot_df.zen.pretty(
    font_size=14,
).format(precision=2)

# # ################################ Plot Interp NEW FRP vs FWI ################################
# start = pd.to_datetime(study_range[0]).strftime("%B %d")
# stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
# start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
# stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
# year = pd.to_datetime(study_range[-1]).strftime("%Y")


# fig = plt.figure(figsize=(12, 4))
# fig.suptitle(f"Fire Weather Index vs Fire Radiative Power", fontsize=18, y=1.08)
# ax = fig.add_subplot(1, 1, 1)

# ax.set_title(
#     f"{case_study.replace('_', ' ').title()}",
#     loc="center",
#     fontsize=14,
# )
# ax.set_title(
#     f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI ",
#     loc="right",
#     fontsize=10,
# )
# ax2 = ax.twinx()
# ax.plot(study_range, hfwi, color="tab:blue", lw=1.2, label="Hourly")
# ax.plot(study_range, dfwi, color="tab:blue", ls="--", lw=1.2, label="Daily")
# ax.plot(study_range, hfwi, color="tab:red", lw=1, label="FRP", zorder=0)

# set_axis_postion(ax, "FWI")

# ax2.plot(study_range, hfrp, color="tab:red", lw=1.2, label="FRP")


# set_axis_postion(ax2, "FRP (MW)")
# tkw = dict(size=4, width=1.5, labelsize=14)
# ax.tick_params(
#     axis="x",
#     **tkw,
# )
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
# ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
# ax.legend(
#     # loc="upper right",
#     bbox_to_anchor=(0.38, 1.18),
#     ncol=3,
#     fancybox=True,
#     shadow=True,
#     fontsize=12,
# )
# fig.autofmt_xdate()

# if save_fig == True:
#     plt.savefig(
#         str(save_dir) + f"/timeseries-interp-final-{start_save}-{stop_save}.png",
#         dpi=250,
#         bbox_inches="tight",
#     )


# ####################### End Plot Interp FRP vs FWI ############################
