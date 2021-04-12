import context
import json
import numpy as np
import pandas as pd
import xarray as xr

from pathlib import Path
from netCDF4 import Dataset

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.offsetbox import AnchoredText


from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from scipy import stats, signal

from context import data_dir, vol_dir, gog_dir
from datetime import datetime, date, timedelta

wrf_model = "wrf3"
domain = "d02"
var = "HFI"
year = "2018"

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)


## Path to fuel converter spreadsheet
fuel_converter = str(data_dir) + "/fbp/fuel_converter.csv"

## Open fuels converter
fc_df = pd.read_csv(fuel_converter)
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
## set index
# fc_df = fc_df.set_index("CFFDRS")
fc_dict = fc_df.transpose().to_dict()

## path to save compare dataset
filein = str(vol_dir) + f"/fwf-v-nrcan-{domain}-{year}0401-{year}0930.zarr"

comp_ds = xr.open_zarr(filein)
df = comp_ds.to_dataframe()
# df = df[df['EPS'].notna()]
df = df.dropna()
df = df.reset_index()
df["time"] = pd.to_datetime(df["time"])

unique, counts = np.unique(df.wmo.values, return_counts=True)
wmo_of_int = unique[counts > 140]
date_range = comp_ds.time.values

date_range = pd.date_range(date_range[0], date_range[-2])

var_list = [
    "CFB",
    "FMC",
    "HFI",
    "ROS",
    "SFC",
    "TFC",
    "ffmc",
    "dmc",
    "dc",
    "isi",
    "bui",
    "fwi",
    "ws",
    "temp",
    "rh",
    "precip",
]

df_wmo = df[df.wmo.isin(wmo_of_int)]
lats, lons = (
    df_wmo[df_wmo.time == df_wmo.time.values].lats,
    df_wmo[df_wmo.time == df_wmo.time.values].lons,
)
df_stats = df_wmo
df_wmo = df_wmo.groupby("time").mean()
df_wmo = df_wmo.reset_index()


def reject_outliers(x, y, m=3):
    return (
        x[abs(x - np.mean(x)) < m * np.std(x)],
        y[abs(x - np.mean(x)) < m * np.std(x)],
    )


#####################################################################################
####################   Make Time Series of Mean WMO vs FWF   ########################
#####################################################################################
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

########################
### FBP
########################
fig = plt.figure(figsize=[10, 12])
if len(date_range) > 1:
    fig.suptitle(
        f'Comp of FWF vs NRCAN at {len(wmo_of_int)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
        fontsize=14,
    )
else:
    fig.suptitle(
        f'Comp of FWF vs NRCAN \n {str(date_range[0].strftime("%Y%m%d"))} \n Number of WxStations {len(wmo_of_int)}',
        fontsize=14,
    )

var_list = ["CFB", "FMC", "HFI", "ROS", "SFC", "TFC"]
length = len(var_list)
for i in range(length):
    var = var_list[i]
    ax = fig.add_subplot(length + 1, 1, i + 1)
    df_stats_i = df_stats[~np.isnan(df_stats[var])]
    fwf_array = df_stats_i[f"{var}_day1"].values
    ncr_array = df_stats_i[f"{var}"].values

    # fwf_array = df_wmo[f'{var}_day1'].values
    # ncr_array = df_wmo[f'{var}'].values
    r = round(stats.pearsonr(ncr_array, fwf_array)[0], 2)
    rmse = str(
        round(
            mean_squared_error(ncr_array, fwf_array, squared=False),
            2,
        )
    )
    anchored_text = AnchoredText(
        r"$r$ " + f"\t {r} \n rmse: {rmse}",
        loc="upper right",
        prop={"size": 8, "zorder": 10},
    )
    fwf_array = df_wmo[f"{var}_day1"].values
    ncr_array = df_wmo[f"{var}"].values
    ax.plot(date_range, ncr_array, label="NRCAN", color=colors[0])
    ax.plot(date_range, fwf_array, label="FWF", color=colors[3])
    ax.set_title(var_dict[var]["description"], fontsize=10)
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=8)
    except:
        pass
    myFmt = DateFormatter("%Y-%m-%d")
    # ax.xaxis.set_major_formatter(myFmt)
    ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.add_artist(anchored_text)
    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        # ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.1, 1.4),
            ncol=2,
            fancybox=True,
            shadow=True,
        )
    else:
        pass

ax.set_xlabel("Time")
# plt.gcf().autofmt_xdate()

fig.tight_layout(h_pad=0.1)
fig.savefig(str(data_dir) + f"/images/fbp/fbp-{domain}-{year}-mean.png")
# plt.close()

########################
### FWI
########################
fig = plt.figure(figsize=[10, 12])
if len(date_range) > 1:
    fig.suptitle(
        f'Comp of FWF vs NRCAN at {len(wmo_of_int)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
        fontsize=14,
    )
else:
    fig.suptitle(
        f'Comp of FWF vs NRCAN \n {str(date_range[0].strftime("%Y%m%d"))} \n Number of WxStations {len(wmo_of_int)}',
        fontsize=14,
    )

var_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
length = len(var_list)
for i in range(length):
    var = var_list[i]
    ax = fig.add_subplot(length + 1, 1, i + 1)
    fwf_array = df_stats[f"{var}_day1"].values
    ncr_array = df_stats[f"{var}"].values
    # fwf_array = df_wmo[f'{var}_day1'].values
    # ncr_array = df_wmo[f'{var}'].values
    r = round(stats.pearsonr(ncr_array, fwf_array)[0], 2)
    rmse = str(
        round(
            mean_squared_error(ncr_array, fwf_array, squared=False),
            2,
        )
    )
    anchored_text = AnchoredText(
        r"$r$ " + f"\t {r} \n rmse: {rmse}",
        loc="upper right",
        prop={"size": 8, "zorder": 10},
    )
    fwf_array = df_wmo[f"{var}_day1"].values
    ncr_array = df_wmo[f"{var}"].values
    ax.plot(date_range, ncr_array, label="NRCAN", color=colors[0])
    ax.plot(date_range, fwf_array, label="FWF", color=colors[3])
    ax.set_title(var_dict[var]["description"], fontsize=10)
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=8)
    except:
        pass
    myFmt = DateFormatter("%Y-%m-%d")
    # ax.xaxis.set_major_formatter(myFmt)
    ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.add_artist(anchored_text)
    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        # ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.1, 1.4),
            ncol=2,
            fancybox=True,
            shadow=True,
        )
    else:
        pass

    if var == "dc":
        ax.set_ylim([0, 850])
    elif var == "ffmc":
        ax.set_ylim([0, 120])
    else:
        pass

ax.set_xlabel("Time")
# plt.gcf().autofmt_xdate()

fig.tight_layout(h_pad=0.1)
fig.savefig(str(data_dir) + f"/images/fbp/fwi-{domain}-{year}-mean.png")
# plt.close()

########################
### Met
########################
fig = plt.figure(figsize=[10, 12])
if len(date_range) > 1:
    fig.suptitle(
        f'Comp of FWF vs NRCAN at {len(wmo_of_int)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
        fontsize=14,
    )
else:
    fig.suptitle(
        f'Comp of FWF vs NRCAN \n {str(date_range[0].strftime("%Y%m%d"))} \n Number of WxStations {len(wmo_of_int)}',
        fontsize=14,
    )

var_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
length = len(var_list)
for i in range(length):
    var = var_list[i]
    ax = fig.add_subplot(length + 1, 1, i + 1)
    fwf_array = df_stats[f"{var}_day1"].values
    ncr_array = df_stats[f"{var}"].values
    # fwf_array = df_wmo[f'{var}_day1'].values
    # ncr_array = df_wmo[f'{var}'].values
    r = round(stats.pearsonr(ncr_array, fwf_array)[0], 2)
    rmse = str(
        round(
            mean_squared_error(ncr_array, fwf_array, squared=False),
            2,
        )
    )
    anchored_text = AnchoredText(
        r"$r$ " + f"\t {r} \n rmse: {rmse}",
        loc="upper right",
        prop={"size": 8, "zorder": 10},
    )
    fwf_array = df_wmo[f"{var}_day1"].values
    ncr_array = df_wmo[f"{var}"].values
    ax.plot(date_range, ncr_array, label="NRCAN", color=colors[0])
    ax.plot(date_range, fwf_array, label="FWF", color=colors[3])
    ax.set_title(var_dict[var]["description"], fontsize=10)
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=8)
    except:
        pass
    # myFmt = DateFormatter("%Y-%m-%d")
    # ax.xaxis.set_major_formatter(myFmt)
    ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.add_artist(anchored_text)
    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        # ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.1, 1.4),
            ncol=2,
            fancybox=True,
            shadow=True,
        )
    else:
        pass
    if var == "rh":
        ax.set_ylim([20, 110])
    elif var == "wdir":
        ax.set_ylim([0, 400])
    else:
        pass

ax.set_xlabel("Time")
# plt.gcf().autofmt_xdate()

fig.tight_layout(h_pad=0.1)
fig.savefig(str(data_dir) + f"/images/fbp/met-{domain}-{year}-mean.png")
# plt.close()

#####################################################################################
####################   Make Time Series of Individual WMO vs FWF   ########################
#####################################################################################

# for wmo in wmo_of_int:
#     df_wmo = df[df.wmo == wmo]
# fig = plt.figure(figsize=[14, 14])
# if len(date_range) > 1:
#     lat, lon, fueltype = str(df_wmo.lats.values[0]), str(df_wmo.lons.values[0]),  fc_df['CFFDRS'][fc_df['Code']==df_wmo.fueltype.values[0]].tolist()[0]
#     fig.suptitle(f'Comp of FWF vs NRCAN \n WMO: {wmo}  Fueltype: {fueltype}  Lat: {lat[:5]}   Lon: {lon[:7]}   Prov: {df_wmo.prov.values[0]} \n{date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}', fontsize=14)
# else:
#     fig.suptitle(f'Comp of FWF vs NRCAN \n {str(date_range[0].strftime("%Y%m%d"))} \n Number of WxStations {len(wmo_of_int)}', fontsize=14)
# for i in range(len(var_list)):
#     # print(var)
#     ax = fig.add_subplot( 4, 4, i+1)
#     # fwf_array_ = comp_ds[f'{var}_day1'].values.ravel()
#     # ncr_array_ = comp_ds[f'{var}'].values.ravel()
#     fwf_array = df_wmo[f'{var}_day1'].values
#     ncr_array = df_wmo[f'{var}'].values

#     r = round(stats.pearsonr(ncr_array, fwf_array)[0],2)
#     rmse = str(round(mean_squared_error(ncr_array, fwf_array, squared=False),2,))
#     # print(np.unique(np.isnan(ncr_array)))
#     ax.plot(date_range, ncr_array, label = 'NRCAN')
#     ax.plot(date_range, fwf_array, label = 'FWI')
#     ax.set_title(var + f' p_r: {r}  rmse: {rmse}', fontsize=12)
#     ax.set_xlabel('Time', fontsize=8)
#     ax.set_ylabel('Values', fontsize=8)
#     myFmt = DateFormatter("%Y-%m-%d")
# ax.xaxis.set_major_formatter(myFmt)
#     if i == 0:
#         # ax.legend()
#         ax.legend(
#             loc="upper center",
#             bbox_to_anchor=(0.5, 1.4),
#             ncol=2,
#             fancybox=True,
#             shadow=True,
#         )
#     else:
#         pass
#     # ax.legend()
# plt.gcf().autofmt_xdate()

# fig.tight_layout(h_pad = 0.1)

# fig.savefig(str(data_dir) + f"/images/fbp/fwb-{domain}-mean.png")
# plt.close()


#####################################################################################
#####################   Make Scatter Plot of WMO V FWF   ########################
#####################################################################################
# for i in range(len(var_list)):
#     print(var)
#     ax = fig.add_subplot( 4, 4, i+1)
#     # fwf_array_ = comp_ds[f'{var}_day1'].values.ravel()
#     # ncr_array_ = comp_ds[f'{var}'].values.ravel()
#     fwf_array_ = df[f'{var}_day1'].values
#     ncr_array_ = df[f'{var}'].values
#     fwf_array  = fwf_array_[~np.isnan(ncr_array_)]
#     ncr_array = ncr_array_[~np.isnan(ncr_array_)]
#     if var != 'CFB':
#         ncr_array_f = ncr_array[(fwf_array>0.09) & (ncr_array > 0.09)]
#         fwf_array_f = fwf_array[(fwf_array>0.09) & (ncr_array > 0.09)]
#     else:
#         ncr_array_f = ncr_array[(fwf_array>0.09) & (ncr_array > 0.09)]
#         fwf_array_f = fwf_array[(fwf_array>0.09) & (ncr_array > 0.09)]


#     r = round(stats.pearsonr(ncr_array_f, fwf_array_f)[0],2)
#     rmse = str(round(mean_squared_error(ncr_array_f, fwf_array_f, squared=False),2,))
#     print(np.unique(np.isnan(ncr_array)))
#     ax.scatter(fwf_array_f, ncr_array_f, s = 5)
#     ax.set_title(var + f' p_r: {r}  rmse: {rmse}', fontsize=12)
#     ax.set_xlabel('FWF', fontsize=8)
#     ax.set_ylabel('NRCAN', fontsize=8)
# fig.tight_layout(h_pad = 0.1)
# plt.show()


#####################################################################################
#####################   Make Map of WMO locations   ###############################
#####################################################################################

# ## make fig for make with projection
# fig = plt.figure(figsize=[16, 8])
# ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# divider = make_axes_locatable(ax)
# ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
# ## bring in state/prov boundaries
# states_provinces = cfeature.NaturalEarthFeature(
#     category="cultural",
#     name="admin_1_states_provinces_lines",
#     scale="50m",
#     facecolor="none",
# )


# ## add map features
# ax.gridlines()
# ax.add_feature(cfeature.LAND, zorder=1)
# ax.add_feature(cfeature.LAKES, zorder=8)
# ax.add_feature(cfeature.OCEAN, zorder=8)
# ax.add_feature(cfeature.BORDERS, zorder=1)
# ax.add_feature(cfeature.COASTLINE, zorder=1)
# ax.add_feature(states_provinces, edgecolor="gray", zorder=6)
# ax.set_xlabel("Longitude", fontsize=18)
# ax.set_ylabel("Latitude", fontsize=18)

# ## create tick mark labels and style
# ax.set_xticks(list(np.arange(-160, -40, 10)), crs=ccrs.PlateCarree())
# ax.set_yticks(list(np.arange(30, 80, 10)), crs=ccrs.PlateCarree())
# ax.tick_params(axis="both", which="major", labelsize=14)
# ax.tick_params(axis="both", which="minor", labelsize=14)

# ax.scatter(lons, lats, zorder=10, s=100, color="red")

# ## add title and adjust subplot buffers
# if domain == "d02":
#     res = "12 km"
# elif domain == "d03":
#     res = "4 km"
# else:
#     res = ""
# Plot_Title = f"WMO locs {res}"
# ax.set_title(Plot_Title, fontsize=20, weight="bold")


# ## set map bounds
# if wrf_model == "wrf3":
#     ax.set_xlim([-140, -60])
#     ax.set_ylim([36, 70])
# elif wrf_model == "wrf4":
#     ax.set_xlim([-174, -30])
#     ax.set_ylim([25, 80])
# else:
#     pass

# fig.savefig(str(data_dir) + f"/images/fbp/wmo-locs.png")
