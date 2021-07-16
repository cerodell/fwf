import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import scipy.stats
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter
from pylab import *
import matplotlib as mpl
import matplotlib.ticker as plticker
import matplotlib.ticker as mticker


from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText
import matplotlib.pylab as pylab

params = {"xtick.labelsize": 14, "ytick.labelsize": 14}


class MidpointNormalize(mpl.colors.Normalize):
    def __init__(self, vmin, vmax, midpoint=0, clip=False):
        self.midpoint = midpoint
        mpl.colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        normalized_min = max(
            0,
            1
            / 2
            * (1 - abs((self.midpoint - self.vmin) / (self.midpoint - self.vmax))),
        )
        normalized_max = min(
            1,
            1
            / 2
            * (1 + abs((self.vmax - self.midpoint) / (self.midpoint - self.vmin))),
        )
        normalized_mid = 0.5
        x, y = [self.vmin, self.midpoint, self.vmax], [
            normalized_min,
            normalized_mid,
            normalized_max,
        ]
        return np.ma.masked_array(np.interp(value, x, y))


pylab.rcParams.update(params)

wrf_model = "wrf3"

domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2018, 10, 1)
intercomp_today_dir = date.strftime("%Y%m%d")
date_range = pd.date_range("2018-04-01", "2018-10-01")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)
ds = ds.chunk(chunks="auto")
ds = ds.unify_chunks()
for var in list(ds):
    ds[var].encoding = {}


if wrf_model == "wrf4":
    wrf_dir = "/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21041100"
    ### Open WRF d02 domain
    filein = str(wrf_dir) + f"/wrfout_d02_2021-04-11_00:00:00"
    wrf_d02 = xr.open_dataset(filein)

    ### Open WRF d03 domain
    filein = str(wrf_dir) + f"/wrfout_d03_2021-04-11_00:00:00"
    wrf_d03 = xr.open_dataset(filein)

elif wrf_model == "wrf3":
    wrf_dir = "/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18021900"
    ### Open WRF d02 domain
    filein = str(wrf_dir) + f"/wrfout_d02_2018-02-19_00:00:00"
    wrf_d02 = xr.open_dataset(filein)

    ### Open WRF d03 domain
    filein = str(wrf_dir) + f"/wrfout_d03_2018-02-19_00:00:00"
    wrf_d03 = xr.open_dataset(filein)
else:
    exit


if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

df = ds.to_dataframe().dropna()
df = df.reset_index()
df = df[~np.isnan(df.bui)]
unique, counts = np.unique(df.wmo.values, return_counts=True)
# wmo_of_int = unique[counts > 140]
# df = df[df.wmo.isin(wmo_of_int)]
# unique, counts = np.unique(df.wmo.values, return_counts=True)


var_list = list(ds)[::3]
time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


var_list = ["precip"]

# var_list = ['bui', 'dc', 'dmc', 'ffmc', 'fwi', 'isi', 'precip', 'rh', 'td', 'temp', 'wdir', 'ws']

for var in var_list:
    wmos, r2s, rmses, bias, wmo_lats, wmo_lons = [], [], [], [], [], []
    print(var)
    name = var_dict[var]["description"]
    for wmo in unique:
        df_i = df.loc[df["wmo"] == wmo]
        df_i = df_i[~np.isnan(df_i[var])]
        r2value = round(
            stats.pearsonr(df_i[var].values, df_i[var + "_day1"].values)[0], 2
        )
        rmse = round(
            mean_squared_error(
                df_i[var].values, df_i[var + "_day1"].values, squared=False
            ),
            2,
        )
        wmos.append(wmo)
        r2s.append(r2value)
        rmses.append(rmse)
        bias.append(np.mean(df_i[var + "_day1"].values - df_i[var].values))
        wmo_lats.append(df_i.lats.values[0])
        wmo_lons.append(df_i.lons.values[0])

    wmos, r2s, rmses, bias, wmo_lats, wmo_lons = (
        np.array(wmos),
        np.array(r2s),
        np.array(rmses),
        np.array(bias),
        np.array(wmo_lats),
        np.array(wmo_lons),
    )

    thres = 0.4
    wmos, r2s, rmses, bias, wmo_lats, wmo_lons = (
        wmos[r2s > thres],
        r2s[r2s > thres],
        rmses[r2s > thres],
        bias[r2s > thres],
        wmo_lats[r2s > thres],
        wmo_lons[r2s > thres],
    )

    ##############################################################################

    ## set plot title and save dir/name
    save_file = f"/images/fwf-{wrf_model}-{domain}-{var}-bias-{intercomp_today_dir}.png"
    save_dir = str(data_dir) + save_file

    ## bring in state/prov boundaries
    states_provinces = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none",
    )

    ## chose where to center longitude..
    ##..by shiftting 180 you can plot over international dateline
    ## NOTE once you do this you also have to shift you longitdues in your data
    ## i did this by adding 180 to the lons...see line 107-110 as example
    proj = ccrs.PlateCarree(central_longitude=180)
    # box_proj = ccrs.PlateCarree(central_longitude=0)

    ## make fig for make with projection
    fig = plt.figure(figsize=[12, 8])
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    # ax.set_title(
    #     f'Root Mean Square Error of {res} NWP derived {name} \n at {676} Weather Stations {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
    #     fontsize=14,
    # )
    ax.set_title(
        f"NWP vs OBS | 24 HOUR ACCUMULATED PRECIPITATION | Mean Bias Error",
        # f'NWP-FWI vs OBS-FWI | Fire Weather Index | Mean Bias Error',
        fontsize=20,
    )
    ## add map features
    gl = ax.gridlines(
        draw_labels=True,
        crs=ccrs.PlateCarree(),
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False

    gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 10)))
    ax.add_feature(cfeature.LAND, zorder=1)
    ax.add_feature(cfeature.LAKES, zorder=1)
    ax.add_feature(cfeature.OCEAN, zorder=1)
    ax.add_feature(cfeature.BORDERS, zorder=1)
    ax.add_feature(cfeature.COASTLINE, zorder=1)
    ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
    ax.set_xlabel("Longitude", fontsize=18)
    ax.set_ylabel("Latitude", fontsize=18)

    ## create tick mark labels and style
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.tick_params(axis="both", which="major", labelsize=14)
    ax.tick_params(axis="both", which="minor", labelsize=14)

    ## add title and adjust subplot buffers
    # ax.set_title(Plot_Title, fontsize=20, weight="bold")
    # cm = plt.cm.get_cmap('RdBu')

    # Cnorm = matplotlib.colors.Normalize(
    #     vmin=0, vmax= 14
    # )
    # for index, row in df.iterrows():
    print(np.max(bias))
    vmin = bias.min()
    vmax = bias.max()

    norm = MidpointNormalize(vmin=vmin, vmax=vmax, midpoint=0)
    cmap = "RdBu_r"

    contourf = ax.scatter(
        wmo_lons + 180, wmo_lats, c=bias, s=50, zorder=10, cmap=cmap, norm=norm
    )

    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
    fig.add_axes(ax_cb)
    cbar = plt.colorbar(contourf, cax=ax_cb)
    # cbar.set_label('Root Mean Square Error')
    cbar.set_label("Bias")

    if domain == "d02":
        ## get d02 lats and lon
        lats, lons = np.array(wrf_d02.XLAT), np.array(wrf_d02.XLONG)
        lats, lons = lats[0], lons[0]
        lons += 180

        ## plot d02
        ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(
            lons[:, -1].T,
            lats[:, -1].T,
            color="k",
            linewidth=2,
            zorder=8,
            alpha=1,
            label="12 km WRF",
        )

    elif domain == "d03":
        ## get d03 lats and lon
        lats, lons = np.array(wrf_d03.XLAT), np.array(wrf_d03.XLONG)
        lats, lons = lats[0], lons[0]
        lons += 180

        ## plot d03
        ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(
            lons[:, -1].T,
            lats[:, -1].T,
            color="k",
            linewidth=2,
            zorder=8,
            alpha=1,
            label="4 km WRF",
        )
    else:
        exit
    ## add legend
    # ax.legend(
    #     loc="upper center",
    #     bbox_to_anchor=(0.5, 1.08),
    #     ncol=5,
    #     fancybox=True,
    #     shadow=True,
    # )
    # plt.tight_layout()

    fig.savefig(save_dir, dpi=240)

    ##############################################################################

    ## set plot title and save dir/name
    save_file = (
        f"/images/fwf-{wrf_model}-{domain}-{var}-pearson-{intercomp_today_dir}.png"
    )
    save_dir = str(data_dir) + save_file

    ## bring in state/prov boundaries
    states_provinces = cfeature.NaturalEarthFeature(
        category="cultural",
        name="admin_1_states_provinces_lines",
        scale="50m",
        facecolor="none",
    )

    ## chose where to center longitude..
    ##..by shiftting 180 you can plot over international dateline
    ## NOTE once you do this you also have to shift you longitdues in your data
    ## i did this by adding 180 to the lons...see line 107-110 as example
    proj = ccrs.PlateCarree(central_longitude=180)
    # box_proj = ccrs.PlateCarree(central_longitude=0)

    ## make fig for make with projection
    fig = plt.figure(figsize=[12, 8])
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    # ax.set_title(
    #     f'Pearson r Value of {res} NWP derived {name} \n at {676} Weather Stations {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
    #     fontsize=14,
    # )
    ax.set_title(
        f"NWP vs OBS | 24 HOUR ACCUMULATED PRECIPITATION  | Pearson’s r ",
        # f'NWP-FWI vs OBS-FWI | Fire Weather Index | Pearson’s r ',
        fontsize=20,
    )
    ## add map features
    gl = ax.gridlines(
        draw_labels=True,
        crs=ccrs.PlateCarree(),
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False

    gl.xlocator = mticker.FixedLocator(list(np.arange(-180, 180, 10)))
    ax.add_feature(cfeature.LAND, zorder=1)
    ax.add_feature(cfeature.LAKES, zorder=1)
    ax.add_feature(cfeature.OCEAN, zorder=1)
    ax.add_feature(cfeature.BORDERS, zorder=1)
    ax.add_feature(cfeature.COASTLINE, zorder=1)
    ax.add_feature(states_provinces, edgecolor="gray", zorder=2)
    ax.set_xlabel("Longitude", fontsize=18)
    ax.set_ylabel("Latitude", fontsize=18)

    ## create tick mark labels and style
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.tick_params(axis="both", which="major", labelsize=14)
    ax.tick_params(axis="both", which="minor", labelsize=14)

    ## add title and adjust subplot buffers
    # ax.set_title(Plot_Title, fontsize=20, weight="bold")
    cm = plt.cm.get_cmap("jet_r")

    Cnorm = matplotlib.colors.Normalize(vmin=0, vmax=1)
    # for index, row in df.iterrows():
    contourf = ax.scatter(
        wmo_lons + 180,
        wmo_lats,
        c=r2s,
        s=50,
        zorder=10,
        cmap=cm,
        norm=Cnorm,
    )

    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
    fig.add_axes(ax_cb)
    cbar = plt.colorbar(contourf, cax=ax_cb)
    cbar.set_label("Pearsons r Value")

    if domain == "d02":
        ## get d02 lats and lon
        lats, lons = np.array(wrf_d02.XLAT), np.array(wrf_d02.XLONG)
        lats, lons = lats[0], lons[0]
        lons += 180

        ## plot d02
        ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(
            lons[:, -1].T,
            lats[:, -1].T,
            color="k",
            linewidth=2,
            zorder=8,
            alpha=1,
            label="12 km WRF",
        )

    elif domain == "d03":
        ## get d03 lats and lon
        lats, lons = np.array(wrf_d03.XLAT), np.array(wrf_d03.XLONG)
        lats, lons = lats[0], lons[0]
        lons += 180

        ## plot d03
        ax.plot(lons[0], lats[0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[-1].T, lats[-1].T, color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(lons[:, 0], lats[:, 0], color="k", linewidth=2, zorder=8, alpha=1)
        ax.plot(
            lons[:, -1].T,
            lats[:, -1].T,
            color="k",
            linewidth=2,
            zorder=8,
            alpha=1,
            label="4 km WRF",
        )
    else:
        exit
    ## add legend
    # ax.legend(
    #     loc="upper center",
    #     bbox_to_anchor=(0.5, 1.08),
    #     ncol=5,
    #     fancybox=True,
    #     shadow=True,
    # )
    # plt.tight_layout()

    fig.savefig(save_dir, dpi=240)


##############################################################################
df = df.loc[df["wmo"].isin(wmos)]


var_list = list(ds)[::3]
time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
length = len(fwi_list)

fig = plt.figure(figsize=[10, 12])  # figsize=[8, 8]
# fig.suptitle(
#     f'Comparison of FWF {res} vs NRCAN at {len(wmos)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
#     fontsize=14,
# )
fig.suptitle(
    f"NWP-FWI vs OBS-FWI",
    fontsize=22,
)
for i in range(length):
    # plt.subplot(i+1, 1, 1)
    ax = fig.add_subplot(length + 1, 1, i + 1)
    var = fwi_list[i]
    # df_final = df[np.abs(df[var] - df[var].mean()) <= (3 * df[var].std())]
    df_final = df[~np.isnan(df[var])]

    # df_final = df_final[
    #     np.abs(df_final[var + "_day1"] - df_final[var + "_day1"].mean())
    #     <= (3 * df_final[var + "_day1"].std())
    # ]

    r2value = round(
        stats.pearsonr(df_final[var].values, df_final[var + "_day1"].values)[0], 2
    )
    rmse = str(
        round(
            mean_squared_error(
                df_final[var].values, df_final[var + "_day1"].values, squared=False
            ),
            2,
        )
    )
    anchored_text = AnchoredText(
        r"$r$ " + f"{r2value} \n rmse: {rmse}",
        loc="upper right",
        prop={"size": 12, "zorder": 10},
    )

    # df_final = df[np.abs(df[var] - df[var].mean()) <= (2 * df[var].std())]
    # df_final = df_final[
    #     np.abs(df_final[var + "_day1"] - df_final[var + "_day1"].mean())
    #     <= (2 * df_final[var + "_day1"].std())
    # ]
    df_final = df_final.groupby("time").mean()
    var_obs = df_final[var].values
    var_model = df_final[var + "_day1"].values
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=14)
    except:
        pass
    ax.set_title(var_dict[var]["description"], fontsize=14)
    ax.plot(df_final.index, var_obs, label="Observation", zorder=2, color=colors[0])
    ax.plot(df_final.index, var_model, label="Forecast", zorder=2, color=colors[3])
    ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
    ax.add_artist(anchored_text)
    if var == "dc":
        ax.set_ylim([0, 850])
    elif var == "ffmc":
        ax.set_ylim([45, 130])
    elif var == "fwi":

        ax.set_ylim([0, 35])
    else:
        pass

    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        # ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.12, 1.6),
            ncol=2,
            fancybox=True,
            shadow=True,
            fontsize=14,
        )
    else:
        pass
    # loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
    # ax.yaxis.set_major_locator(loc)

ax.set_xlabel("Time")
fig.tight_layout(h_pad=0.1)

fig.savefig(
    str(data_dir) + f"/images/stats/fwi-vars-{domain}-{intercomp_today_dir}-mean.png"
)
plt.close()


##########################################################################
met_list = ["temp", "rh", "ws", "precip"]
met_unit = ["C", "%", "km h^-1", "mm"]
length = len(met_list)

fig = plt.figure(figsize=[10, 12])  # figsize=[8, 8]
# fig.suptitle(
#     f'Comparison of {wrf_model.upper()} {res} vs Observations at {len(wmos)} Weather Stations \n {date_range[0].strftime("%Y%m%d")} - {date_range[-1].strftime("%Y%m%d")}',
#     fontsize=14,
# )
fig.suptitle(
    f"NWP-FWI vs OBS-FWI",
    fontsize=22,
)
for i in range(length):
    # plt.subplot(i+1, 1, 1)
    ax = fig.add_subplot(length + 1, 1, i + 1)
    var = met_list[i]
    # df_final = df[np.abs(df[var] - df[var].mean()) <= (3 * df[var].std())]
    df_final = df[~np.isnan(df[var])]
    # df_final = df_final[
    #     np.abs(df_final[var + "_day1"] - df_final[var + "_day1"].mean())
    #     <= (3 * df_final[var + "_day1"].std())
    # ]
    r2value = round(
        stats.pearsonr(df_final[var].values, df_final[var + "_day1"].values)[0], 2
    )
    rmse = str(
        round(
            mean_squared_error(
                df_final[var].values, df_final[var + "_day1"].values, squared=False
            ),
            2,
        )
    )
    anchored_text = AnchoredText(
        r"$r$ " + f"{r2value} \n rmse: {rmse}",
        loc="upper right",
        prop={"size": 12, "zorder": 10},
    )

    # df_final = df[np.abs(df[var] - df[var].mean()) <= (2 * df[var].std())]
    # df_final = df_final[
    #     np.abs(df_final[var + "_day1"] - df_final[var + "_day1"].mean())
    #     <= (2 * df_final[var + "_day1"].std())
    # ]
    df_final = df_final.groupby("time").mean()
    var_obs = df_final[var].values
    var_model = df_final[var + "_day1"].values
    try:
        ax.set_ylabel(fr"$({var_dict[var]['units']})$", fontsize=12)
    except:
        pass
    ax.set_title(var_dict[var]["description"], fontsize=14)
    ax.plot(df_final.index, var_obs, label="Observation", zorder=2, color=colors[0])
    ax.plot(df_final.index, var_model, label="Forecast", zorder=2, color=colors[3])
    ax.yaxis.grid(linewidth=0.4, linestyle="--")
    ax.xaxis.grid(linewidth=0.4, linestyle="--")
    ax.add_artist(anchored_text)
    if var == "rh":
        ax.set_ylim([20, 100])
    else:
        pass

    if i != length - 1:
        ax.tick_params(axis="x", labelbottom=False)
    else:
        pass
    if i == 0:
        ax.legend()
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.1, 1.3),
            ncol=2,
            fancybox=True,
            shadow=True,
            fontsize=14,
        )
    else:
        pass

ax.set_xlabel("Time")
fig.tight_layout()
fig.savefig(
    str(data_dir) + f"/images/stats/met-vars-{domain}-{intercomp_today_dir}-mean.png"
)
plt.close()
