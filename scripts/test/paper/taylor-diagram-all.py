import context

import numpy as np
import pandas as pd
from pathlib import Path


import skill_metrics as sm
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from context import data_dir

model = "nwp"
trail_name = "02"

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/{model}/taylor/")
save_dir.mkdir(parents=True, exist_ok=True)

var_list = [
    "ffmc",
    "dmc",
    "dc",
    "bui",
    "isi",
    "fwi",
    "temp",
    "td",
    "rh",
    "ws",
    "wdir",
    "rh",
]
# var_list = ['fwi']
for var in var_list:
    day1_df = pd.read_csv(str(data_dir) + f"/intercomp/02/nwp/{var}-stats.csv")
    day1_df["domain"] = day1_df["domain"].str.strip()
    stdev_obs = float(day1_df[day1_df["domain"] == "obs"]["std_dev"])

    day2_df = pd.read_csv(str(data_dir) + f"/intercomp/02/nwp_day2/{var}-stats.csv")
    day2_df["domain"] = day2_df["domain"].str.strip()
    stdev_obs2 = float(day2_df[day2_df["domain"] == "obs"]["std_dev"])
    if stdev_obs != stdev_obs2:
        raise ValueError("We have an issue! The day1 and day2 std dont match")

    def stats_tuple(df, domain):
        dfi = df[df["domain"] == domain]
        return (dfi["std_dev"], dfi["rms"], dfi["r"])

    def get_mbe(df, domain):
        mbe = round(float(df[df["domain"] == domain]["mbe"]), 2)
        if mbe < 0:
            mbe = "{:.2f}".format(mbe)
        else:
            mbe = " " + "{:.2f}".format(mbe)
        return mbe

    obs_name = "Observed                       1 Day Bias,    2 Day Bias"

    if var == "rh":
        name = "min"
    else:
        name = "max"

    wrf_d03_noon = f"WRF 4km Noon               {get_mbe(day1_df, 'd03-noon')},             {get_mbe(day2_df, 'd03-noon')}"
    wrf_d02_noon = f"WRF 12km Noon             {get_mbe(day1_df, 'd02-noon')},             {get_mbe(day2_df, 'd02-noon')}"
    hrdps_noon = f"HRDPS 2.5km Noon        {get_mbe(day1_df, 'hrdps-noon')},              {get_mbe(day2_df, 'hrdps-noon')}"
    rdps_noon = f"RDPS 10km Noon             {get_mbe(day1_df, 'rdps-noon')},              {get_mbe(day2_df, 'rdps-noon')}"
    try:
        wrf_d03_max = f"WRF 4km {name.capitalize()}                 {get_mbe(day1_df, f'd03-{name}')},             {get_mbe(day2_df, f'd03-{name}')}"
        wrf_d02_max = f"WRF 12km {name.capitalize()}               {get_mbe(day1_df, f'd02-{name}')},             {get_mbe(day2_df, f'd02-{name}')}"
        hrdps_max = f"HRDPS 2.5km {name.capitalize()}          {get_mbe(day1_df, f'hrdps-{name}')},             {get_mbe(day2_df, f'hrdps-{name}')}"
        rdps_max = f"RDPS 10km {name.capitalize()}               {get_mbe(day1_df, f'rdps-{name}')},             {get_mbe(day2_df, f'rdps-{name}')}"
    except:
        pass
    try:
        wrf_d03_hourly = f"WRF 4km Hourly             {get_mbe(day1_df, 'd03-hourly')},             {get_mbe(day2_df, 'd03-hourly')}"
        wrf_d02_hourly = f"WRF 12km Hourly           {get_mbe(day1_df, 'd02-hourly')},             {get_mbe(day2_df, 'd02-hourly')}"
        hrdps_hourly = f"HRDPS 2.5km Hourly      {get_mbe(day1_df, 'hrdps-hourly')},             {get_mbe(day2_df, 'hrdps-hourly')}"
        rdps_hourly = f"RDPS 10km Hourly           {get_mbe(day1_df, 'rdps-hourly')},             {get_mbe(day2_df, 'rdps-hourly')}"
    except:
        pass
    # ## DATA ####################################################################### #

    LEGEND_SUBPLOT = 2
    try:
        day1_dict = {
            wrf_d03_noon: stats_tuple(day1_df, "d03-noon"),
            wrf_d03_max: stats_tuple(day1_df, f"d03-{name}"),
            wrf_d03_hourly: stats_tuple(day1_df, "d03-hourly"),
            wrf_d02_noon: stats_tuple(day1_df, "d02-noon"),
            wrf_d02_max: stats_tuple(day1_df, f"d02-{name}"),
            wrf_d02_hourly: stats_tuple(day1_df, "d02-hourly"),
            hrdps_noon: stats_tuple(day1_df, "hrdps-noon"),
            hrdps_max: stats_tuple(day1_df, f"hrdps-{name}"),
            hrdps_hourly: stats_tuple(day1_df, "hrdps-hourly"),
            rdps_noon: stats_tuple(day1_df, "rdps-noon"),
            rdps_max: stats_tuple(day1_df, f"rdps-{name}"),
            rdps_hourly: stats_tuple(day1_df, "rdps-hourly"),
        }
        day2_dict = {
            wrf_d03_noon: stats_tuple(day2_df, "d03-noon"),
            wrf_d03_max: stats_tuple(day2_df, f"d03-{name}"),
            wrf_d03_hourly: stats_tuple(day2_df, "d03-hourly"),
            wrf_d02_noon: stats_tuple(day2_df, "d02-noon"),
            wrf_d02_max: stats_tuple(day2_df, f"d02-{name}"),
            wrf_d02_hourly: stats_tuple(day2_df, "d02-hourly"),
            hrdps_noon: stats_tuple(day2_df, "hrdps-noon"),
            hrdps_max: stats_tuple(day2_df, f"hrdps-{name}"),
            hrdps_hourly: stats_tuple(day2_df, "hrdps-hourly"),
            rdps_noon: stats_tuple(day2_df, "rdps-noon"),
            rdps_max: stats_tuple(day2_df, f"rdps-{name}"),
            rdps_hourly: stats_tuple(day2_df, "rdps-hourly"),
        }
    except:
        try:
            day1_dict = {
                wrf_d03_noon: stats_tuple(day1_df, "d03-noon"),
                wrf_d03_max: stats_tuple(day1_df, f"d03-{name}"),
                wrf_d02_noon: stats_tuple(day1_df, "d02-noon"),
                wrf_d02_max: stats_tuple(day1_df, f"d02-{name}"),
                hrdps_noon: stats_tuple(day1_df, "hrdps-noon"),
                hrdps_max: stats_tuple(day1_df, f"hrdps-{name}"),
                rdps_noon: stats_tuple(day1_df, "rdps-noon"),
                rdps_max: stats_tuple(day1_df, f"rdps-{name}"),
            }
            day2_dict = {
                wrf_d03_noon: stats_tuple(day2_df, "d03-noon"),
                wrf_d03_max: stats_tuple(day2_df, "d03-max"),
                wrf_d02_noon: stats_tuple(day2_df, "d02-noon"),
                wrf_d02_max: stats_tuple(day2_df, "d02-max"),
                hrdps_noon: stats_tuple(day2_df, "hrdps-noon"),
                hrdps_max: stats_tuple(day2_df, "hrdps-max"),
                rdps_noon: stats_tuple(day2_df, "rdps-noon"),
                rdps_max: stats_tuple(day2_df, "rdps-max"),
            }
        except:
            day1_dict = {
                wrf_d03_noon: stats_tuple(day1_df, "d03-noon"),
                wrf_d02_noon: stats_tuple(day1_df, "d02-noon"),
                hrdps_noon: stats_tuple(day1_df, "hrdps-noon"),
                rdps_noon: stats_tuple(day1_df, "rdps-noon"),
            }
            day2_dict = {
                wrf_d03_noon: stats_tuple(day2_df, "d03-noon"),
                wrf_d02_noon: stats_tuple(day2_df, "d02-noon"),
                hrdps_noon: stats_tuple(day2_df, "hrdps-noon"),
                rdps_noon: stats_tuple(day2_df, "rdps-noon"),
            }

    SUBPLOTS_DATA = [
        {
            "axis_idx": (0),
            "title": "(a) 1 day lead time",
            "y_label": True,
            "x_label": False,
            "observed": (stdev_obs, 0.00, 1.00),
            "modeled": day1_dict,
        },
        {
            "axis_idx": (1),
            "title": "(b) 2 day lead time",
            "y_label": False,
            "x_label": False,
            "observed": (stdev_obs, 0.00, 1.00),
            "modeled": day2_dict,
        },
    ]

    MARKERS = {
        obs_name: {
            "marker": "^",
            "color_edge": "#000000",
            "color_face": "#000000",
            "markersize": 9,
        },
        wrf_d03_noon: {
            "marker": "o",
            "color_edge": "#000000",
            "color_face": "#777777",
            "markersize": 9,
        },
        wrf_d02_noon: {
            "marker": "o",
            "color_edge": "#AA0000",
            "color_face": "#DD3333",
            "markersize": 9,
        },
        hrdps_noon: {
            "marker": "o",
            "color_edge": "#00AA00",
            "color_face": "#33DD33",
            "markersize": 9,
        },
        rdps_noon: {
            "marker": "o",
            "color_edge": "#0000AA",
            "color_face": "#3333DD",
            "markersize": 9,
        },
    }
    try:
        EXTREMS = {
            wrf_d03_max: {
                "marker": "v",
                "color_edge": "#000000",
                "color_face": "#777777",
                "markersize": 9,
            },
            wrf_d02_max: {
                "marker": "v",
                "color_edge": "#AA0000",
                "color_face": "#DD3333",
                "markersize": 9,
            },
            hrdps_max: {
                "marker": "v",
                "color_edge": "#00AA00",
                "color_face": "#33DD33",
                "markersize": 9,
            },
            rdps_max: {
                "marker": "v",
                "color_edge": "#0000AA",
                "color_face": "#3333DD",
                "markersize": 9,
            },
        }
        MARKERS.update(EXTREMS)
    except:
        pass
    try:
        HOURLIES = {
            wrf_d03_hourly: {
                "marker": "s",
                "color_edge": "#000000",
                "color_face": "#777777",
                "markersize": 9,
            },
            wrf_d02_hourly: {
                "marker": "s",
                "color_edge": "#AA0000",
                "color_face": "#DD3333",
                "markersize": 9,
            },
            hrdps_hourly: {
                "marker": "s",
                "color_edge": "#00AA00",
                "color_face": "#33DD33",
                "markersize": 9,
            },
            rdps_hourly: {
                "marker": "s",
                "color_edge": "#0000AA",
                "color_face": "#3333DD",
                "markersize": 9,
            },
        }
        MARKERS.update(HOURLIES)
    except:
        pass

    # ## PLOT STYLE ################################################################# #

    FONT_FAMILY = "Times New Roman"
    FONT_SIZE = 9

    # specify some styles for the correlation component
    COLS_COR = {"grid": "#DDDDDD", "tick_labels": "#000000", "title": "#000000"}

    # specify some styles for the standard deviation
    COLS_STD = {
        "grid": "#DDDDDD",
        "tick_labels": "#000000",
        "ticks": "#DDDDDD",
        "title": "#000000",
    }

    # specify some styles for the root mean square deviation
    STYLES_RMS = {"color": "#AAAADD", "linestyle": "--"}

    # ## CONSTANTS ################################################################## #

    OUTPUT_FILE_PATH = "taylor16.png"

    # ## MAIN ####################################################################### #

    if __name__ == "__main__":

        plt.close("all")

        # update figures global properties
        plt.rcParams.update({"font.size": FONT_SIZE, "font.family": FONT_FAMILY})

        # create figure with 2 lines and 3 columns
        fig_size = (10, 4)
        fig, axs = plt.subplots(1, 3, figsize=fig_size, sharey=True)
        del fig_size

        # build subplot by subplot
        for subplot_data in SUBPLOTS_DATA:

            # get subplot object and ensure it will be a square
            # y-axis labels will only appear on leftmost subplot
            ax = axs[subplot_data["axis_idx"]]
            ax.set(adjustable="box", aspect="equal")

            # create the plot with the observed data
            stdev, crmsd, ccoef = subplot_data["observed"]
            sm.taylor_diagram(
                ax,
                np.asarray((stdev, stdev)),
                np.asarray((crmsd, crmsd)),
                np.asarray((ccoef, ccoef)),
                markercolors={
                    "face": MARKERS[obs_name]["color_edge"],
                    "edge": MARKERS[obs_name]["color_face"],
                },
                markersize=MARKERS[obs_name]["markersize"],
                markersymbol=MARKERS[obs_name]["marker"],
                styleOBS=":",
                colOBS=MARKERS[obs_name]["color_edge"],
                alpha=1.0,
                titleSTD="off",
                titleRMS="on",
                showlabelsRMS="on",
                # tickSTD = range(0,25,5),
                # axismax = 20,
                # tickRMS = [6,12,18],
                colRMS=STYLES_RMS["color"],
                #   tickRMSangle = 115,
                styleRMS=STYLES_RMS["linestyle"],
                colscor=COLS_COR,
                colsstd=COLS_STD,
                styleCOR="-",
                styleSTD="-",
                colframe="#DDDDDD",
                labelweight="normal",
                titlecorshape="linear",
            )

            # add label below the marker
            ax.text(
                stdev,
                -0.5,
                "Obsv.",
                verticalalignment="top",
                horizontalalignment="center",
                fontsize=FONT_SIZE + 1,
                fontweight="bold",
            )

            # get rid of variables not to be used anymore
            del stdev, crmsd, ccoef

            # create one overlay for each model marker
            for model_id, (stdev, crmsd, ccoef) in subplot_data["modeled"].items():
                marker = MARKERS[model_id]
                sm.taylor_diagram(
                    ax,
                    np.asarray((stdev, stdev)),
                    np.asarray((crmsd, crmsd)),
                    np.asarray((ccoef, ccoef)),
                    markersymbol=marker["marker"],
                    markercolors={
                        "face": marker["color_face"],
                        "edge": marker["color_edge"],
                    },
                    markersize=marker["markersize"],
                    alpha=1.0,
                    overlay="on",
                    styleCOR="-",
                    styleSTD="-",
                )

                # get rid of variables not to be used anymore
                del model_id, stdev, crmsd, ccoef, marker

            # set titles (upper, left, bottom)
            ax.set_title(subplot_data["title"], loc="left", y=1.1)

            # add y label
            if subplot_data["y_label"]:
                ax.set_ylabel(
                    "Standard Deviation", fontfamily=FONT_FAMILY, fontsize=FONT_SIZE + 2
                )

            # add xlabel or hide xticklabels
            if subplot_data["x_label"]:
                ax.set_xlabel(
                    "Standard Deviation", fontfamily=FONT_FAMILY, fontsize=FONT_SIZE + 2
                )
            else:
                ax.set_xticklabels(ax.get_xticklabels(), color=ax.get_facecolor())

            # # just for the peace of mind...
            del subplot_data, ax

        # create legend in the last subplot
        ax = axs[LEGEND_SUBPLOT]
        ax.axis("off")

        # build legend handles
        legend_handles = []
        legend_handles.append(
            mlines.Line2D(
                [],
                [],
                color=STYLES_RMS["color"],
                linestyle=STYLES_RMS["linestyle"],
                label="RMSE",
            )
        )

        for marker_label, marker_desc in MARKERS.items():
            marker = mlines.Line2D(
                [],
                [],
                marker=marker_desc["marker"],
                markersize=marker_desc["markersize"],
                markerfacecolor=marker_desc["color_face"],
                markeredgecolor=marker_desc["color_edge"],
                linestyle="None",
                label=marker_label,
            )
            legend_handles.append(marker)
            del marker_label, marker_desc, marker

        # create legend and free memory
        ax.legend(handles=legend_handles, loc="center")
        del ax, legend_handles
        # avoid some overlapping
        plt.tight_layout()

        # # Write plot to file
        plt.savefig(
            str(save_dir) + f"/{var}.png", dpi=150, facecolor="w", bbox_inches="tight"
        )
        del MARKERS, SUBPLOTS_DATA, LEGEND_SUBPLOT
