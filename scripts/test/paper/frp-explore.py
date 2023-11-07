import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from scipy import stats
from pathlib import Path
import plotly.express as px
import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable


from context import data_dir, root_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################


## define model domain and path to fwf data
domain = "d03"
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

# define case study name and bounding box of fire
# case_study = 'sparks_lake'
# min_lat = 50.9
# max_lat = 51.2
# min_lon = -121.0
# max_lon = -120.7
# date_range = pd.date_range("2021-06-20", "2021-07-12", freq='H')
# doi = pd.to_datetime('2021-07-01')

# case_study = 'kimiwan_complex'
# min_lat = 55.655
# max_lat = 56.33
# min_lon = -117.22
# max_lon = -116.05
# date_range = pd.date_range("2023-05-10", "2023-05-25", freq='H')
# doi = pd.to_datetime('2023-05-13')


case_study = "lazy_fire"
min_lat = 53.01
max_lat = 53.46
min_lon = -102.83
max_lon = -102.13
date_range = pd.date_range("2021-07-25", "2021-08-04", freq="H")
doi = pd.to_datetime("2021-08-01")

################## END INPUTS ####################

#################### OPEN FILES ####################
## open FRP data
df = pd.read_csv(
    str(data_dir) + f"/frp/SUOMI-VIIRS-C2-CSV/fire_archive_SV-C2_359209.csv"
)
# df = pd.read_csv(str(data_dir) + f"/frp/SUOMI-VIIRS-C2-CSV/fire_nrt_SV-C2_359209.csv")

## open static data of wrf/FWF model
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
pyproj_srs = static_ds.attrs["pyproj_srs"]

## Open Fuels Data and subset
fc_df = pd.read_csv(str(data_dir) + "/fbp/fuel_converter.csv")
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
fc_dict = fc_df.transpose().to_dict()
################## END OPEN ####################


########################### FUNCTIONS ##########################


def get_locs(pyproj_srs, df):
    # get_locs_time = datetime.now()
    gpm25 = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    ).to_crs(pyproj_srs)

    x = xr.DataArray(
        np.array(gpm25.geometry.x),
        dims="loc",
        coords=dict(loc=np.arange(len(df))),
    )
    y = xr.DataArray(
        np.array(gpm25.geometry.y),
        dims="loc",
        coords=dict(loc=np.arange(len(df))),
    )
    try:
        x = x.assign_coords(frp=("loc", df["frp"]))
        y = y.assign_coords(frp=("loc", df["frp"]))
    except:
        pass
    return x, y


def open_fwf(doi, model):
    if model == "hourly":
        indexer = slice(0, 24)
    elif model == "daily":
        indexer = 0
    ds = (
        salem.open_xr_dataset(
            filein + f"/fwf-{model}-{domain}-{doi.strftime('%Y%m%d06')}.nc"
        )
        .isel(time=indexer)
        .chunk("auto")
    )

    return ds[["S", "F"]]


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


######################### END FUNCTIONS ##########################


########################### Modify datasets #######################

## Adjust acquisition time to be datetime compatible
df["acq_time"] = (
    df["acq_time"].astype(str).apply(lambda x: "0" + x if len(x) <= 3 else x)
)

## create datetime column named DateTime
df["DateTime"] = pd.to_datetime(df["acq_date"] + "T" + df["acq_time"].astype(str))

## index dataframe to be in the date range of interest
df = df.loc[(df["DateTime"] >= date_range[0]) & (df["DateTime"] <= date_range[-1])]


## Filter the DataFrame based on the bounding box of fire
df = df[
    (df["latitude"] >= min_lat)
    & (df["latitude"] <= max_lat)
    & (df["longitude"] >= min_lon)
    & (df["longitude"] <= max_lon)
]

## set DateTime as dataframe index
df = df.set_index("DateTime")

## Group by DateTime and take mean of time and resample to hourly frequency, computing mean within each group
## currently this is only used to get the first and last overpass hours
df_grouped = df.groupby(df.index)["frp"].mean()
oidx = df_grouped.index
nidx = pd.date_range(oidx.min(), oidx.max(), freq="H")
res = df_grouped.reindex(oidx.union(nidx)).interpolate("index").reindex(nidx)
res.index = pd.to_datetime(res.index.astype(str))
res.index = res.index.round("H")


## create data range of times when there where hotspot detects and open the related FWF model data
date_range2 = pd.date_range(res.index[0], res.index[-1], freq="D")
## open fwf hourly
hds = xr.combine_nested([open_fwf(doi, "hourly") for doi in date_range2], "time")
hds["time"] = hds["Time"]
## open fwf daily
dds = xr.combine_nested([open_fwf(doi, "daily") for doi in date_range2], "time")
dds["time"] = dds["Time"]

## Slice static dataset for plotting wrf grid and hotspots onto a map
xx, yy = get_locs(pyproj_srs, df)
buff = 10000
ds_map = static_ds.sel(
    south_north=slice(yy.min() - buff, yy.max() + buff),
    west_east=slice(xx.min() - buff, xx.max() + buff),
)


## find UTC of set to localtime based on ~center of Fire
df_center = pd.DataFrame(
    {
        "latitude": [np.mean([min_lat, min_lat])],
        "longitude": [np.mean([min_lon, min_lon])],
    }
)
center_x, center_y = get_locs(pyproj_srs, df_center)
utc_offset = static_ds["ZoneDT"].interp(
    west_east=center_x, south_north=center_y, method="nearest"
)


##################################### END MODS ####################################


############################## Analyzing datasets  ##############################

## find unique times of the VIRRS overpasses
frp = df.groupby("DateTime")["frp"]
times = list(frp.groups)
hFWI, dFWI = [], []
## loop time for each over pass
for time in times:
    #   print(time)
    ## index on unique time
    df_time = df.loc[time]
    if str(type(df_time)) == "<class 'pandas.core.series.Series'>":
        df_time = pd.DataFrame([df_time])
    ## get fwf model data at nearst hour of VIRRS overpass
    hds_time = hds.sel(time=time.round("H").strftime("%Y%m%dT%H"))
    dds_time = dds.sel(time=time.strftime("%Y%m%dT"))

    ## find the the nearest mode grid(s) for each hot spot and store the frp data for those grids
    ## when the interp funtion is applied, the x and y dataarrays have the frp data stored as coordinates.
    x, y = get_locs(pyproj_srs, df_time)
    hds_locs = hds_time.interp(west_east=x, south_north=y, method="nearest")
    dds_locs = dds_time.interp(west_east=x, south_north=y, method="nearest")

    # Create a tuple of the lat lon of the wrf grids hotpsot are located
    array_tuple = np.stack([hds_locs["XLAT"], hds_locs["XLONG"]], axis=1)
    darray_tuple = np.stack([dds_locs["XLAT"], dds_locs["XLONG"]], axis=1)

    # Find the unique pairs so we dont duplicate the process
    unique_pairs = np.unique(array_tuple, axis=0)
    h_grid_cell, d_grid_cell = [], []
    ## loop unique wrf grids and average the FRP values that land within one grid
    ## store this in a new list to merge after all locations sampled
    for i in range(len(unique_pairs)):
        index = np.where(array_tuple == unique_pairs[i])
        hds_loc_cell = hds_locs.isel(loc=index[0])
        hds_loc_cell = hds_loc_cell.assign(FRP=hds_loc_cell["frp"])
        hds_loc_cell = hds_loc_cell.mean(dim="loc")
        h_grid_cell.append(hds_loc_cell)

        dds_loc_cell = dds_locs.isel(loc=index[0])
        dds_loc_cell = dds_loc_cell.assign(FRP=dds_loc_cell["frp"])
        dds_loc_cell = dds_loc_cell.mean(dim="loc")
        dds_loc_cell["Time"] = hds_loc_cell["Time"]
        dds_loc_cell["time"] = dds_loc_cell["Time"]
        d_grid_cell.append(dds_loc_cell)

    ## combine all FWI/FRP from a single sat overpass (one time) into a dataset
    hds_cell = xr.combine_nested(h_grid_cell, "time")
    dds_cell = xr.combine_nested(d_grid_cell, "time")
    hFWI.append(hds_cell.mean())
    dFWI.append(dds_cell.mean())

## combine all FWI/FRP from a fire into a single dataset
hourly_ds = xr.combine_nested(hFWI, "time")
daily_ds = xr.combine_nested(dFWI, "time")

## convert utc to local time of fire incident
hourly_ds["time"] = hourly_ds["Time"] = hourly_ds["Time"] - np.timedelta64(
    int(utc_offset), "h"
)
daily_ds["time"] = daily_ds["Time"] = daily_ds["Time"] - np.timedelta64(
    int(utc_offset), "h"
)

## solve r coleration
pearsonr_h = stats.pearsonr(hourly_ds["S"], hourly_ds["FRP"])
pearsonr_d = stats.pearsonr(daily_ds["S"], hourly_ds["FRP"])

############################## End Analyzing datasets  ##############################


#################### Plot to explore FRP on a zoom able map ####################
print(f"{len(df)} number of observations")
fig = px.scatter_mapbox(
    df,
    lat="latitude",
    lon="longitude",
    color="acq_date",
    size=f"frp",
    # color_continuous_scale="Viridis",
    hover_name="frp",
    # center={"lat": 58.0, "lon": -110.0},
    center={"lat": (max_lat + min_lat) / 2, "lon": (max_lon + min_lon) / 2},
    hover_data=["daynight", "acq_date", "acq_time"],
    mapbox_style="carto-positron",
    zoom=8,
)
# fig.layout.coloraxis.colorbar.title = "2m T Bias"
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()

################################## END PLOT ###################################


################# Plot Hot spots on WRF Grid ###################
## TODO colorize based on time of overpass

# # Filter rows based on the target datetime
# df_sample = df[df.index.date == doi.date()]
# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(1, 1, 1)
# XLONG = ds_map['XLONG'].values
# XLONG = XLONG[1:,1:] - np.diff(XLONG).mean()
# XLAT = ds_map['XLAT'].values
# XLAT = XLAT[1:,1:] - np.diff(XLAT).mean()
# shape = XLAT.shape

# for i in range(shape[0]):
#     ax.plot(XLONG[i,:], XLAT[i,:], color = 'k', lw = 0.5, zorder = 10)
# for j in range(shape[1]):
#     ax.plot(XLONG[:,j], XLAT[:,j], color = 'k', lw = 0.5, zorder = 10)
# sc = ax.scatter(df_sample['longitude'], df_sample['latitude'], zorder = 9, c = df_sample['frp'])
# cbar = plt.colorbar(sc, ax=ax, pad=0.008)
# ax.set_title(f"Fire Radiative Power {case_study.replace('_',' ')}", fontsize=14)
# cbar.set_label('FRP', rotation=270, fontsize=14, labelpad =20)
# ax.set_xlabel('Longitude', fontsize=16)
# ax.set_ylabel('Latitude', fontsize=16)
# plt.savefig(str(data_dir) + f"/images/paper/frp-grid-{case_study.replace('_','-')}-{doi.strftime('%Y%m%dT%H%M')}.png" ,
#             dpi=250,
#             bbox_inches="tight"
#             )
############## End hotspot on wrf grid plot ###################


######################## Plot Fuel Type ########################
# fuels = ds_map['FUELS'].values
# lngs = ds_map.XLONG.values
# lats = ds_map.XLAT.values
# fillarray = fuels

# National_FBP_Fueltypes_2014 = fc_df.National_FBP_Fueltypes_2014.values
# levels = []
# for i in range(0, len(National_FBP_Fueltypes_2014)):
#     fillarray[fillarray == National_FBP_Fueltypes_2014[i]] = i
#     levels.append(i)

# ## make fig for make with projection
# fig = plt.figure(figsize=(8, 8))
# ax = fig.add_subplot(1, 1, 1)
# divider = make_axes_locatable(ax)
# ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

# ## add map features
# ax.set_xlabel("Longitude", fontsize=18)
# ax.set_ylabel("Latitude", fontsize=18)
# ax.tick_params(axis="both", which="major", labelsize=14)
# ax.tick_params(axis="both", which="minor", labelsize=14)

# ## give plot a title
# if domain == "d02":
#     res = "12 km"
# elif domain == "d03":
#     res = "4 km"
# else:
#     res = ""
# Plot_Title = f"Canadian Forest FBP Fuel Type Grid for WRF Domain {res}"
# ax.set_title(Plot_Title, fontsize=16, weight="bold")

# ## Add color bar with fuels labels
# colors = fc_df.Colors.values.tolist()
# cmap = matplotlib.colors.ListedColormap(colors)
# Cnorm = matplotlib.colors.BoundaryNorm(levels, cmap.N)
# contourf = ax.pcolormesh(lngs, lats, fillarray + 0.5, zorder=10, norm=Cnorm, cmap=cmap)
# fig.add_axes(ax_cb)
# ticks = fc_df.CFFDRS.values

# tick_levels = list(np.array(levels) + 0.5)
# cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
# cbar.ax.set_yticklabels(ticks)  # set ticks of your format
# cbar.ax.axes.tick_params(length=0)
################################ End Fuel Type plot ##############################

################################ Plot FRP vs FWI ############################
start = pd.to_datetime(date_range2[0]).strftime("%B %d")
stop = pd.to_datetime(date_range2[-1]).strftime("%B %d")
start_save = pd.to_datetime(date_range2[0]).strftime("%Y%m%d")
stop_save = pd.to_datetime(date_range2[-1]).strftime("%Y%m%d")
year = pd.to_datetime(date_range2[-1]).strftime("%Y")
hfwi = hourly_ds["S"].values
hfrp = hourly_ds["FRP"].values
dfwi = daily_ds["S"].values
# %%
fig = plt.figure(figsize=(12, 4))
fig.suptitle(f"FWI vs FRP", fontsize=20)
ax = fig.add_subplot(1, 1, 1)
ax.set_title(
    f"{start} - {stop}, {year} \n",
    loc="right",
    fontsize=14,
)
ax.set_title(
    f"r: {round(pearsonr_h[0],2)} Hourly FWI \nr: {round(pearsonr_d[0],2)}   Daily FWI ",
    loc="right",
    fontsize=10,
)
ax2 = ax.twinx()
ax.plot(hourly_ds.Time, hfwi, color="tab:blue", ls="-.", lw=0.6)
ax.scatter(hourly_ds.Time, hfwi, color="tab:blue", label="Hourly", s=52)

ax.plot(daily_ds.Time, dfwi, color="tab:blue", ls="--", lw=0.6)
ax.scatter(daily_ds.Time, dfwi, color="tab:blue", marker="^", label="Daily", s=52)

set_axis_postion(ax, "FWI")

ax2.plot(hourly_ds.Time, hfrp, color="tab:red", ls="-.", lw=0.6)
ax2.scatter(hourly_ds.Time, hfrp, color="tab:red", label="FRP")
ax.scatter(daily_ds.Time, hfwi, color="tab:red", label="FRP", zorder=0, s=46)

set_axis_postion(ax2, "FRP")
tkw = dict(size=4, width=1.5, labelsize=14)
ax.tick_params(
    axis="x",
    **tkw,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d-%H"))
ax.set_xlabel("Local DateTime (MM-DD-HH)", fontsize=16)
ax.legend(
    loc="upper right",
    # bbox_to_anchor=(0.5, 1.08),
    ncol=3,
    fancybox=True,
    shadow=True,
    fontsize=13,
)

plt.savefig(
    str(data_dir)
    + f"/images/paper/frp-timeseries--{case_study.replace('_','-')}-{start_save}-{stop_save}.png",
    dpi=250,
    bbox_inches="tight",
)

print(f"hourly pearsonr: {pearsonr_h[0]}")
print(f"daily pearsonr: {pearsonr_d[0]}")
################### End Plot FRP vs FWI ###################
