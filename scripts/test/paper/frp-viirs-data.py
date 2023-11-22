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
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.neighbors import KDTree

import cartopy.crs as ccrs
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import make_axes_locatable
from netCDF4 import Dataset
from wrf import ll_to_xy

from context import data_dir, root_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################


## define model domain and path to fwf data
save_fig = True
case_study = "oil_springs_fire"
print(case_study)

################## END INPUTS ####################

#################### OPEN FILES ####################

## open case study json file
with open(str(root_dir) + f"/json/fire-cases.json", "r") as fp:
    case_dict = json.load(fp)

case_info = case_dict[case_study]
domain = case_info["domain"]
date_range = pd.date_range(
    case_info["date_range"][0], case_info["date_range"][1], freq="H"
)
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

# modis_df = pd.read_csv(str(data_dir) + f"/frp/DL_FIRE_M-C61_361602/fire_archive_M-C61_361602.csv")
# modis_df = modis_df[modis_df['confidence'] > 80]
# modis_df['frp'] = modis_df['frp'].where(modis_df['daynight'] == 'D', -338.41 + (1.09* modis_df['frp']))
# modis_df['frp'] = modis_df['frp'].where(modis_df['daynight'] == 'N', 179.46 + (0.78* modis_df['frp']))
# modis_df['frp'] = (modis_df['frp'] - modis_df['frp'].min()) / (modis_df['frp'].max() - modis_df['frp'].min())


viirs_j1_df = pd.read_csv(
    str(data_dir) + f"/frp/DL_FIRE_J1V-C2_361603/fire_nrt_J1V-C2_361603.csv"
)
viirs_j1_df = viirs_j1_df[viirs_j1_df["confidence"].isin(["n", "h"])]
# viirs_j1_df['frp'] = (viirs_j1_df['frp'] - viirs_j1_df['frp'].min()) / (viirs_j1_df['frp'].max() - viirs_j1_df['frp'].min())
if date_range[0] >= pd.Timestamp("2022-09-01"):
    viirs_su_df = pd.read_csv(
        str(data_dir) + f"/frp/DL_FIRE_SV-C2_361604/fire_nrt_SV-C2_361604.csv"
    )
else:
    viirs_su_df = pd.read_csv(
        str(data_dir) + f"/frp/DL_FIRE_SV-C2_361604/fire_archive_SV-C2_361604.csv"
    )
viirs_su_df = viirs_su_df[viirs_su_df["confidence"].isin(["n", "h"])]
# viirs_su_df['frp'] = (viirs_su_df['frp'] - viirs_su_df['frp'].min()) / (viirs_su_df['frp'].max() - viirs_su_df['frp'].min())

df = pd.concat([viirs_j1_df, viirs_su_df])

## open FRP data
# df = pd.read_csv(
#     str(data_dir) + f"/frp/DL_FIRE_SV-C2_361604/fire_archive_SV-C2_361604.csv"
# )
# drop low confidences satellite detections, keep ing only nominal and high detects
# df = df[df["confidence"].isin(["n", "h"])]

## open static data of wrf/FWF model
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
pyproj_srs = static_ds.attrs["pyproj_srs"]

##
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_{domain}_2021-01-14_00:00:00")
wrf_ds = xr.open_dataset(str(data_dir) + f"/wrf/wrfout_{domain}_2021-01-14_00:00:00")
## Open Fuels Data and subset
fc_df = pd.read_csv(str(data_dir) + "/fbp/fuel_converter.csv")
fc_df = fc_df.drop_duplicates(subset=["CFFDRS"])
fc_df["Code"] = fc_df["National_FBP_Fueltypes_2014"]
fc_dict = fc_df.transpose().to_dict()

save_dir = Path(str(data_dir) + f"/images/frp/{case_study}")
save_dir.mkdir(parents=True, exist_ok=True)
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
    try:
        ds = ds[["S", "F", "HFI"]]
    except:
        ds = ds[["S", "F"]]
    return ds


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
    (df["latitude"] >= case_info["min_lat"])
    & (df["latitude"] <= case_info["max_lat"])
    & (df["longitude"] >= case_info["min_lon"])
    & (df["longitude"] <= case_info["max_lon"])
]

## set DateTime as dataframe index
df = df.set_index("DateTime")

## Group by DateTime and take mean of time and resample to hourly frequency, computing mean within each group
## currently this is only used to get the first and last overpass hours
df_grouped = df.groupby(df.index)["frp"].mean()
oidx = df_grouped.index
nidx = pd.date_range(oidx.round("H").min(), oidx.round("H").max(), freq="H")
frp_interp = (
    df_grouped.reindex(oidx.union(nidx))
    .interpolate("index")
    .reindex(nidx)
    .ffill()
    .bfill()
)
frp_interp.index = pd.to_datetime(frp_interp.index.astype(str))


## create data range of times when there where hotspot detects and open the related FWF model data
date_range2 = pd.date_range(
    frp_interp.index[0] - np.timedelta64(1, "D"),
    frp_interp.index[-1] + np.timedelta64(2, "D"),
    freq="D",
)
## open fwf hourly
hds = xr.combine_nested([open_fwf(doi, "hourly") for doi in date_range2], "time")
hds["time"] = hds["Time"]
## open fwf daily
dds = xr.combine_nested([open_fwf(doi, "daily") for doi in date_range2], "time")
dds["time"] = dds["Time"]
dds_resampled = dds.resample(time="1H").nearest()
dds_resampled["time"] = dds_resampled["time"] + np.timedelta64(12, "h")
dds_resampled["Time"] = dds_resampled["time"]

## Slice static dataset for plotting wrf grid and hotspots onto a map
xx, yy = get_locs(pyproj_srs, df)
buff = 10000
if domain == "d02":
    buff = buff * 2
ds_map = static_ds.sel(
    south_north=slice(yy.min() - buff - 5000, yy.max() + buff),
    west_east=slice(xx.min() - buff, xx.max() + buff + 5000),
)

## find UTC of set to localtime based on ~center of Fire
df_center = pd.DataFrame(
    {
        "latitude": [np.mean([case_info["min_lat"], case_info["max_lat"]])],
        "longitude": [np.mean([case_info["min_lon"], case_info["max_lon"]])],
    }
)
center_x, center_y = get_locs(pyproj_srs, df_center)
utc_offset = static_ds["ZoneDT"].interp(
    west_east=center_x, south_north=center_y, method="nearest"
)

XLATr, XLONGr = static_ds.XLAT.values.ravel(), static_ds.XLONG.values.ravel()
fwf_locs = pd.DataFrame({"lats": XLATr, "longs": XLONGr})
## build kdtree
fwf_tree = KDTree(fwf_locs)
print("Fire KDTree built")

##################################### END MODS ####################################


############################## Analyzing datasets  ##############################

## find unique times of the VIIRS overpasses
frp = df.groupby(pd.to_datetime(df.index).strftime("%Y-%m-%d"))["frp"]

times = list(frp.groups)
expected_range = pd.date_range(times[0], times[-1])

hFWII, dFWII = [], []
## loop time for each over pass
obs_size = []
for j in range(len(expected_range)):
    # time = pd.to_datetime(times[j])
    time = expected_range[j]
    print(time)

    ## get fwf model data at nearst hour of VIRRS overpass
    hds_time = hds.sel(time=time.strftime("%Y%m%d"))
    dds_time = dds_resampled.sel(time=time.strftime("%Y%m%d"))
    df_day = df[df.index.date == time.date()]

    if len(df_day) == 0:
        df_day = df[df.index.date == (time.date() - pd.Timedelta(days=1))]
        if len(df_day) == 0:
            raise ValueError(f"To many days with miss data, bad {case_study}")
        else:
            pass
    else:
        pass

    lat, lon = df_day["latitude"], df_day["longitude"]
    inds = []

    for loc in df_day.itertuples(index=True, name="Pandas"):
        ## arange wx station lat and long in a formate to query the kdtree
        single_loc = np.array([loc.latitude, loc.longitude]).reshape(1, -1)
        ## query the kdtree retuning the distacne of nearest neighbor and index
        dist, ind = fwf_tree.query(single_loc, k=1)
        ## set condition to pass on fire farther than 0.1 degrees
        if dist > 0.1:
            pass
        else:
            inds.append(int(ind))

    hds_locs = hds_time.stack(locs=["south_north", "west_east"])
    dds_locs = dds_time.stack(locs=["south_north", "west_east"])
    hds_locs = hds_locs.isel(locs=inds).mean("locs")
    dds_locs = dds_locs.isel(locs=inds).mean("locs")

    ## find the the nearest mode grid(s) for each hot spot and store the frp data for those grids
    ## when the interp funtion is applied, the x and y dataarrays have the frp data stored as coordinates.
    # x, y = get_locs(pyproj_srs, df_day)
    # hds_locs = hds_time.interp(west_east=x, south_north=y, method="nearest").mean("loc")
    # dds_locs = dds_time.interp(west_east=x, south_north=y, method="nearest").mean("loc")

    # x, y = ll_to_xy(ncfile, lat, lon)
    # array_tuple = np.stack([x, y], axis=1)
    # unique_pairs = np.unique(array_tuple, axis=0)
    # hds_locs = hds_time.isel(west_east=unique_pairs[:,0], south_north=unique_pairs[:,1]).mean(['west_east', 'south_north'])
    # dds_locs = dds_time.isel(west_east=unique_pairs[:,0], south_north=unique_pairs[:,1]).mean(['west_east', 'south_north'])
    obs_size.append(len(inds))
    hFWII.append(hds_locs)
    dFWII.append(dds_locs)


hds_fire_final = xr.combine_nested(hFWII, "time")
hds_fire_final = hds_fire_final.groupby("Time").mean(dim="time")

hds_fire_final = hds_fire_final.sel(
    Time=slice(frp_interp.index[0], frp_interp.index[-1])
)
hds_fire_final["FRP"] = (("Time"), frp_interp.values)
hds_fire_final = hds_fire_final.expand_dims(dim={"method": ["hourly"]})
hds_fire_final["Time"] = hds_fire_final["Time"] - np.timedelta64(int(utc_offset), "h")

dds_fire_final = xr.combine_nested(dFWII, "time")
dds_fire_final = dds_fire_final.groupby("Time").mean(dim="time")
# test = dds_fire_final.resample(Time="1H").nearest()
dds_fire_final = dds_fire_final.sel(
    Time=slice(hds_fire_final.Time[0], hds_fire_final.Time[-1])
)
dds_fire_final["FRP"] = (("Time"), frp_interp.values)
dds_fire_final = dds_fire_final.expand_dims(dim={"method": ["daily"]})

interp_grid_ds = xr.combine_nested([dds_fire_final, hds_fire_final], "method")
interp_grid_ds["S"].attrs = {"name": "Fire Weather Index"}
interp_grid_ds["F"].attrs = {"name": "Fine Fuel Moisture Code"}
interp_grid_ds["FRP"].attrs = {"name": "Fire Radiative Power"}
interp_grid_ds.attrs = {"utc_offset": str(utc_offset)}
interp_grid_ds = interp_grid_ds.drop_vars("XTIME")

## save newly created dataset
study_range = hds_fire_final.Time.values
start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
# on_obs_ds.to_netcdf(str(data_dir) + f"/frp/analysis/{domain}/{case_study.replace('_','-')}-on-obs-{start_save}-{stop_save}.nc")
# interp_ds.to_netcdf(str(data_dir) + f"/frp/analysis/{domain}/{case_study.replace('_','-')}-interp-{start_save}-{stop_save}.nc")
interp_grid_ds.to_netcdf(
    str(data_dir)
    + f"/frp/analysis/{domain}/{case_study.replace('_','-')}-interp-grid.nc"
)


############################## End Analyzing datasets  ##############################

# #################### Plot to explore FRP on a zoom able map ####################
# print(f"{len(df)} number of observations")
# fig = px.scatter_mapbox(
#     df,
#     lat="latitude",
#     lon="longitude",
#     color='acq_date',
#     size=f"frp",
#     # color_continuous_scale="Viridis",
#     hover_name="frp",
#   # center={"lat": 58.0, "lon": -110.0},
#     center={"lat": (case_info['max_lat']+case_info['min_lat'])/2, "lon": (case_info['max_lon']+case_info['max_lon'])/2},
#     hover_data=["daynight", "acq_date", "acq_time", "instrument"],
#     mapbox_style="carto-positron",
#     zoom=8,
# )
# # fig.layout.coloraxis.colorbar.title = "2m T Bias"
# fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
# fig.show()

# ################################## END PLOT ###################################

# ######################## Plot Fuel Type ########################
fuels = ds_map["FUELS"].values
lngs = ds_map.XLONG.values
lats = ds_map.XLAT.values
fillarray = fuels

National_FBP_Fueltypes_2014 = fc_df.National_FBP_Fueltypes_2014.values
levels = []
for i in range(0, len(National_FBP_Fueltypes_2014)):
    fillarray[fillarray == National_FBP_Fueltypes_2014[i]] = i
    levels.append(i)

## make fig for make with projection
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1)
divider = make_axes_locatable(ax)
ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)

## add map features
ax.set_xlabel("Longitude", fontsize=18)
ax.set_ylabel("Latitude", fontsize=18)
ax.tick_params(axis="both", which="major", labelsize=14)
ax.tick_params(axis="both", which="minor", labelsize=14)

## give plot a title
if domain == "d02":
    res = "12 km"
elif domain == "d03":
    res = "4 km"
else:
    res = ""
Plot_Title = f"Canadian Forest FBP Fuel Type Grid for WRF Domain {res}"
ax.set_title(Plot_Title, fontsize=16, weight="bold")

## Add color bar with fuels labels
colors = fc_df.Colors.values.tolist()
cmap = matplotlib.colors.ListedColormap(colors)
Cnorm = matplotlib.colors.BoundaryNorm(levels, cmap.N)
contourf = ax.pcolormesh(lngs, lats, fillarray + 0.5, zorder=10, norm=Cnorm, cmap=cmap)
fig.add_axes(ax_cb)
ticks = fc_df.CFFDRS.values

tick_levels = list(np.array(levels) + 0.5)
cbar = plt.colorbar(contourf, cax=ax_cb, ticks=tick_levels)
cbar.ax.set_yticklabels(ticks)  # set ticks of your format
cbar.ax.axes.tick_params(length=0)
if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/fuels.png",
        dpi=250,
        bbox_inches="tight",
    )
# ################################ End Fuel Type plot ##############################


# ################# Plot Hot spots on WRF Grid ###################
## TODO colorize based on time of overpass


############################################
# TASK 1.1
# Read map
import matplotlib.image as mpimg

# Filter rows based on the target datetime
# df_sample = df[df.index.date == doi.date()]
df_sample = df
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1)
XLONG = ds_map["XLONG"].values
XLONG = XLONG[1:, 1:] - np.diff(XLONG).mean()
XLAT = ds_map["XLAT"].values
XLAT = XLAT[1:, 1:] - np.diff(XLAT).mean()
shape = XLAT.shape
for i in range(shape[0]):
    ax.plot(XLONG[i, :], XLAT[i, :], color="k", lw=0.5, zorder=10)
for j in range(shape[1]):
    ax.plot(XLONG[:, j], XLAT[:, j], color="k", lw=0.5, zorder=10)
sc = ax.scatter(
    df_sample["longitude"],
    df_sample["latitude"],
    zorder=9,
    c=mdates.date2num(df_sample.index.values),
    alpha=0.5,
)

cbar = plt.colorbar(sc, ax=ax, pad=0.008, alpha=1)
loc = mdates.AutoDateLocator()
cbar.ax.yaxis.set_major_locator(loc)
cbar.ax.yaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
ax.set_title(f"Fire Hot Spots {case_study.replace('_',' ')}", fontsize=14)
cbar.set_label("Datetime", rotation=270, fontsize=14, labelpad=20)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)
if case_study == "mb_096":
    img = mpimg.imread(str(data_dir) + f"/frp/mb_096_true.jpeg")
    ax.imshow(
        img,
        extent=[
            case_info["min_lon"],
            case_info["max_lon"],
            case_info["min_lat"],
            case_info["max_lat"],
        ],
    )
else:
    pass
if save_fig == True:
    plt.savefig(str(save_dir) + f"/map-frp.png", dpi=250, bbox_inches="tight")

# ############## End hotspot on wrf grid plot ###################


# ################# Plot FRP on WRF Grid ###################

# Filter rows based on the target datetime
doi = expected_range[np.argmax(obs_size)]
df_sample = df[df.index.date == doi.date()]

inds = []
for loc in df_sample.itertuples(index=True, name="Pandas"):
    ## arange wx station lat and long in a formate to query the kdtree
    single_loc = np.array([loc.latitude, loc.longitude]).reshape(1, -1)
    ## query the kdtree retuning the distacne of nearest neighbor and index
    dist, ind = fwf_tree.query(single_loc, k=1)
    ## set condition to pass on fire farther than 0.1 degrees
    if dist > 0.1:
        pass
    else:
        inds.append(int(ind))

static_i = static_ds.stack(locs=["south_north", "west_east"])
static_i = static_i.isel(locs=inds)
XLONG1 = static_i.XLONG.values
XLAT1 = static_i.XLAT.values

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(1, 1, 1)
XLONG = ds_map["XLONG"].values
XLAT = ds_map["XLAT"].values
test = np.isin(XLAT, XLAT1).astype(int)
test = test.astype(float)
ax.pcolormesh(
    XLONG,
    XLAT,
    test,
    zorder=1,
    cmap=matplotlib.colors.ListedColormap(["green", "red"]),
    alpha=0.5,
)
sc = ax.scatter(
    df_sample["longitude"],
    df_sample["latitude"],
    zorder=9,
    c=df_sample["frp"],
    cmap="inferno",
)
cbar = plt.colorbar(sc, ax=ax, pad=0.008)
ax.set_title(
    f"Fire Radiative Power {case_study.replace('_',' ')} \n {doi.strftime('%d %b %Y')}",
    fontsize=14,
)
cbar.set_label("FRP (MW)", rotation=270, fontsize=14, labelpad=20)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)
# if case_study == 'mb_096':
#     img = mpimg.imread(str(data_dir) + f'/frp/mb_096_true.jpeg')
#     ax.imshow(img,extent=[case_info['min_lon'],case_info['max_lon'], case_info['min_lat'],case_info['max_lat']])
# else:
#     pass
if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/map-frp-{doi.strftime('%Y%m%d')}.png",
        dpi=250,
        bbox_inches="tight",
    )


# ############## End FRP on wrf grid plot ###################

hfwi = hds_fire_final["S"].values[0]
hfrp = dds_fire_final["FRP"].values[0]
dfwi = dds_fire_final["S"].values[0]
pearsonr_h_interp_final = stats.pearsonr(hfwi, hfrp)
pearsonr_d_interp_final = stats.pearsonr(dfwi, hfrp)
# ################################ Plot Interp NEW FRP vs FWI ################################
start = pd.to_datetime(study_range[0]).strftime("%B %d")
stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
year = pd.to_datetime(study_range[-1]).strftime("%Y")


fig = plt.figure(figsize=(12, 4))
fig.suptitle(f"Fire Weather Index vs Fire Radiative Power", fontsize=18, y=1.08)
ax = fig.add_subplot(1, 1, 1)

ax.set_title(
    f"{case_study.replace('_', ' ').title()}",
    loc="center",
    fontsize=14,
)
ax.set_title(
    f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI ",
    loc="right",
    fontsize=10,
)
ax2 = ax.twinx()
ax.plot(study_range, hfwi, color="tab:blue", lw=1.2, label="Hourly")
ax.plot(study_range, dfwi, color="tab:blue", ls="--", lw=1.2, label="Daily")
ax.plot(study_range, hfwi, color="tab:red", lw=1, label="FRP", zorder=0)

set_axis_postion(ax, "FWI")

ax2.plot(study_range, hfrp, color="tab:red", lw=1.2, label="FRP")


set_axis_postion(ax2, "FRP (MW)")
tkw = dict(size=4, width=1.5, labelsize=14)
ax.tick_params(
    axis="x",
    **tkw,
)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
ax.legend(
    # loc="upper right",
    bbox_to_anchor=(0.38, 1.18),
    ncol=3,
    fancybox=True,
    shadow=True,
    fontsize=12,
)
fig.autofmt_xdate()

if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/timeseries-interp-final-{start_save}-{stop_save}.png",
        dpi=250,
        bbox_inches="tight",
    )


# ####################### End Plot Interp FRP vs FWI ############################
