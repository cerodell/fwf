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
domain = "d03"
filein = f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/02/"

# # define case study name and bounding box of fire
case_study = "sparks_lake"
min_lat = 50.9
max_lat = 51.2
min_lon = -121.0
max_lon = -120.7
date_range = pd.date_range("2021-06-29", "2021-07-29", freq="H")
doi = pd.to_datetime("2021-07-01")

# case_study = 'double_creek'
# min_lat = 45.2
# max_lat = 45.8
# min_lon = -117.00
# max_lon = -116.33
# date_range = pd.date_range("2022-08-29", "2022-09-15", freq='H')
# # date_range = pd.date_range("2021-06-29", "2021-07-01", freq='H')
# doi = pd.to_datetime('2022-09-09')
## https://inciweb.nwcg.gov/incident-information/orwwf-double-creek-fire

# case_study = 'kimiwan_complex'
# min_lat = 55.655
# max_lat = 56.33
# min_lon = -117.22
# max_lon = -116.05
# date_range = pd.date_range("2023-05-05", "2023-05-25", freq='H')
# doi = pd.to_datetime('2023-05-18')

# case_study = 'wildcat'
# min_lat = 53.01
# max_lat = 53.46
# min_lon = -102.83
# max_lon = -102.13
# date_range = pd.date_range("2021-07-25", "2021-08-04", freq='H')
# doi = pd.to_datetime('2021-08-01')


# case_study = 'munson_creek'
# min_lat = 64.864
# max_lat = 65.195
# min_lon = -146.266
# max_lon = -145.513
# date_range = pd.date_range("2021-06-30", "2021-07-30", freq='H')
# doi = pd.to_datetime('2021-07-13')

# case_study = 'six_rivers'
# min_lat = 40.75
# max_lat = 41.04
# min_lon = -123.76
# max_lon = -123.46
# date_range = pd.date_range("2022-08-06", "2022-08-16", freq='H')
# doi = pd.to_datetime('2022-08-14')
### https://inciweb.nwcg.gov/incident-information/casrf-six-rivers-lightning-complex


# case_study = 'cutoff_creek'
# min_lat = 53.45
# max_lat = 53.83
# min_lon = -124.94
# max_lon = -124.41
# date_range = pd.date_range("2021-07-04", "2021-07-15", freq='H')
# doi = pd.to_datetime('2021-07-14')
### https://web.archive.org/web/20210706223626/http://bcfireinfo.for.gov.bc.ca/hprScripts/WildfireNews/OneFire.asp?ID=827


# define case study name and bounding box of fire
# case_study = 'mb_096'
# min_lat = 52.21
# max_lat = 52.76
# min_lon = -96.57
# max_lon = -95.81
# date_range = pd.date_range("2021-07-02", "2021-07-16")
# doi = pd.to_datetime('2021-07-10')
### https://www.gov.mb.ca/conservation_fire/Fire-Status/2021/EA-096-firestatus.html

################## END INPUTS ####################

#################### OPEN FILES ####################
## open FRP data
df = pd.read_csv(
    str(data_dir) + f"/frp/DL_FIRE_SV-C2_361604/fire_archive_SV-C2_361604.csv"
)
## drop low confidences satellite detections, keep ing only nominal and high detects
df = df[df["confidence"].isin(["n", "h"])]

## open static data of wrf/FWF model
static_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"
)
pyproj_srs = static_ds.attrs["pyproj_srs"]

##
ncfile = Dataset(str(data_dir) + f"/wrf/wrfout_{domain}_2021-01-14_00:00:00")

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
        "latitude": [np.mean([min_lat, min_lat])],
        "longitude": [np.mean([min_lon, min_lon])],
    }
)
center_x, center_y = get_locs(pyproj_srs, df_center)
utc_offset = static_ds["ZoneDT"].interp(
    west_east=center_x, south_north=center_y, method="nearest"
)


buff = 5000
if domain == "d02":
    buff = buff * 2
hds_fire = hds.sel(
    south_north=slice(yy.min() - buff, yy.max() + buff),
    west_east=slice(xx.min() - buff, xx.max() + buff),
).mean(dim=["south_north", "west_east"])
hds_fire = hds_fire.sel(time=slice(frp_interp.index[0], frp_interp.index[-1]))
# hds_fire = hds_fire.expand_dims(dim={"method": ['hourly']})

dds_fire = dds.sel(
    south_north=slice(yy.min() - buff, yy.max() + buff),
    west_east=slice(xx.min() - buff, xx.max() + buff),
).mean(dim=["south_north", "west_east"])
dds_fire = dds_fire.resample(time="1H").nearest()
dds_fire = dds_fire.sel(time=slice(frp_interp.index[0], frp_interp.index[-1]))
# dds_fire = dds_fire.expand_dims(dim={"method": ['daily']})

interp_ds = xr.combine_nested([dds_fire, hds_fire], "method")
interp_ds = interp_ds.drop_vars(["XTIME", "Time"])
interp_ds["FRP"] = (("time"), frp_interp.values)
interp_ds["S"].attrs = {"name": "Fire Weather Index"}
interp_ds["F"].attrs = {"name": "Fine Fuel Moisture Code"}
interp_ds["FRP"].attrs = {"name": "Fire Radiative Power"}
interp_ds.attrs = {"utc_offset": str(utc_offset)}
interp_ds = interp_ds.rename({"time": "Time"})


##################################### END MODS ####################################


############################## Analyzing datasets  ##############################

## find unique times of the VIIRS overpasses
frp = df.groupby(pd.to_datetime(df.index).strftime("%Y-%m-%d"))["frp"]

times = list(frp.groups)
expected_range = pd.date_range(times[0], times[-1])

hFWII, dFWII = [], []
## loop time for each over pass
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
    ## find the the nearest mode grid(s) for each hot spot and store the frp data for those grids
    ## when the interp funtion is applied, the x and y dataarrays have the frp data stored as coordinates.
    x, y = get_locs(pyproj_srs, df_day)
    hds_locs = hds_time.interp(west_east=x, south_north=y, method="nearest").mean("loc")
    dds_locs = dds_time.interp(west_east=x, south_north=y, method="nearest").mean("loc")

    # x, y = ll_to_xy(ncfile, lat, lon)
    # array_tuple = np.stack([x, y], axis=1)
    # unique_pairs = np.unique(array_tuple, axis=0)
    # hds_locs = hds_time.isel(west_east=unique_pairs[:,0], south_north=unique_pairs[:,1]).mean(['west_east', 'south_north'])
    # dds_locs = dds_time.isel(west_east=unique_pairs[:,0], south_north=unique_pairs[:,1]).mean(['west_east', 'south_north'])

    hFWII.append(hds_locs)
    dFWII.append(dds_locs)


# ## find unique times of the VIIRS overpasses
# frp = df.groupby('DateTime')['frp']
# times = list(frp.groups)
# hFWI, hIFWI, dFWI, dIFWI  = [], [], [], []
# ## loop time for each over pass
# for j in range(len(times)):
#     time = times[j]
#     print(time)
#     ## index on unique time
#     df_time =df.loc[time]
#     if str(type(df_time)) == "<class 'pandas.core.series.Series'>":
#         df_time = pd.DataFrame([df_time])
#     ## get fwf model data at nearst hour of VIRRS overpass
#     hds_time = hds.sel(time = time.round('H').strftime('%Y%m%dT%H'))
#     dds_time = dds.sel(time = time.strftime('%Y%m%dT'))

#     if j == 0:
#         hds_fire_i = hds.sel(time = time.round('H').strftime('%Y%m%dT%H'))
#         dds_fire_i = dds_resampled.sel(time = time.round('H').strftime('%Y%m%dT%H'))
#     else:
#         hds_fire_i = hds.sel(time =slice(times[j-1].round('H').strftime('%Y%m%dT%H'), times[j].round('H').strftime('%Y%m%dT%H')))
#         dds_fire_i = dds_resampled.sel(time =slice(times[j-1].round('H').strftime('%Y%m%dT%H'), times[j].round('H').strftime('%Y%m%dT%H')))


#     ## find the the nearest mode grid(s) for each hot spot and store the frp data for those grids
#     ## when the interp funtion is applied, the x and y dataarrays have the frp data stored as coordinates.
#     x, y = get_locs(pyproj_srs, df_time)
#     hds_locs = hds_time.interp(west_east=x, south_north=y, method="nearest")
#     dds_locs = dds_time.interp(west_east=x, south_north=y, method="nearest")

#     hds_fire_i = hds_fire_i.sel(south_north = slice(y.min()-buff, y.max()+buff), west_east = slice(x.min()-buff, x.max()+buff)).mean(dim =['south_north', 'west_east'])
#     x, y = get_locs(pyproj_srs, df[df.index.date == time.date()])
#     dds_fire_i = dds_fire_i.sel(south_north = slice(y.min()-buff, y.max()+buff), west_east = slice(x.min()-buff, x.max()+buff)).mean(dim =['south_north', 'west_east'])

#     # Create a tuple of the lat lon of the wrf grids hotpsot are located
#     array_tuple = np.stack([hds_locs['XLAT'], hds_locs['XLONG']], axis=1)
#     darray_tuple = np.stack([dds_locs['XLAT'], dds_locs['XLONG']], axis=1)

#     # Find the unique pairs so we dont duplicate the process
#     unique_pairs = np.unique(array_tuple, axis=0)
#     h_grid_cell, d_grid_cell = [], []
#     ## loop unique wrf grids and average the FRP values that land within one grid
#     ## store this in a new list to merge after all locations sampled
#     for i in range(len(unique_pairs)):
#         index = np.where(array_tuple == unique_pairs[i])
#         hds_loc_cell = hds_locs.isel(loc = index[0])
#         hds_loc_cell = hds_loc_cell.assign(FRP=hds_loc_cell['frp'])
#         hds_loc_cell = hds_loc_cell.mean(dim = 'loc')
#         h_grid_cell.append(hds_loc_cell)

#         dds_loc_cell = dds_locs.isel(loc = index[0])
#         dds_loc_cell = dds_loc_cell.assign(FRP=dds_loc_cell['frp'])
#         dds_loc_cell = dds_loc_cell.mean(dim = 'loc')
#         dds_loc_cell['Time'] = hds_loc_cell['Time']
#         dds_loc_cell['time'] = dds_loc_cell['Time']
#         d_grid_cell.append(dds_loc_cell)

#     ## combine all FWI/FRP from a single sat overpass (one time) into a dataset
#     hds_cell = xr.combine_nested(h_grid_cell, "time")
#     dds_cell = xr.combine_nested(d_grid_cell, "time")
#     hFWI.append(hds_cell.mean())
#     dFWI.append(dds_cell.mean())

#     hIFWI.append(hds_fire_i)
#     dIFWI.append(dds_fire_i)

## combine all FWI/FRP from a fire into a single dataset
# hourly_ds = xr.combine_nested(hFWI, "time")
# hourly_ds = hourly_ds.groupby('Time').mean(dim='time')
# hourly_ds = hourly_ds.expand_dims(dim={"method": ['hourly']})

# daily_ds = xr.combine_nested(dFWI, "time")
# daily_ds = daily_ds.groupby('Time').mean(dim='time')
# daily_ds = daily_ds.expand_dims(dim={"method": ['daily']})
# on_obs_ds = xr.combine_nested([daily_ds, hourly_ds], "method")

# on_obs_ds['S'].attrs = {'name': 'Fire Weather Index'}
# on_obs_ds['F'].attrs = {'name': 'Fine Fuel Moisture Code'}
# on_obs_ds['FRP'].attrs = {'name': 'Fire Radiative Power'}
# on_obs_ds.attrs = {'utc_offset': str(utc_offset)}
# on_obs_ds = on_obs_ds.drop_vars('XTIME')


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
# interp_grid_ds.to_netcdf(str(data_dir) + f"/frp/analysis/{domain}/{case_study.replace('_','-')}-interp-grid-{start_save}-{stop_save}.nc")


############################## End Analyzing datasets  ##############################

# #################### Plot to explore FRP on a zoom able map ####################
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
    hover_data=["daynight", "acq_date", "acq_time", "instrument"],
    mapbox_style="carto-positron",
    zoom=8,
)
# fig.layout.coloraxis.colorbar.title = "2m T Bias"
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()

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
)
cbar = plt.colorbar(sc, ax=ax, pad=0.008)
loc = mdates.AutoDateLocator()
cbar.ax.yaxis.set_major_locator(loc)
cbar.ax.yaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
ax.set_title(f"Fire Radiative Power {case_study.replace('_',' ')}", fontsize=14)
cbar.set_label("Datetime", rotation=270, fontsize=14, labelpad=20)
ax.set_xlabel("Longitude", fontsize=16)
ax.set_ylabel("Latitude", fontsize=16)
if save_fig == True:
    plt.savefig(str(save_dir) + f"/map-frp.png", dpi=250, bbox_inches="tight")
# ############## End hotspot on wrf grid plot ###################

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
fig.suptitle(f"FWI vs FRP", fontsize=20)
ax = fig.add_subplot(1, 1, 1)
ax.set_title(
    f"{start} - {stop}, {year} \n",
    loc="right",
    fontsize=14,
)
ax.set_title(
    f"r: {round(pearsonr_h_interp_final[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp_final[0],2)}   Daily FWI ",
    loc="right",
    fontsize=10,
)
ax2 = ax.twinx()
ax.plot(hds_fire_final.Time, hfwi, color="tab:blue", lw=1.2, label="Hourly")
ax.plot(dds_fire_final.Time, dfwi, color="tab:blue", ls="--", lw=1.2, label="Daily")
ax.plot(hds_fire_final.Time, hfwi, color="tab:red", lw=1, label="FRP", zorder=0)

set_axis_postion(ax, "FWI")

ax2.plot(hds_fire_final.Time, hfrp, color="tab:red", lw=1.2, label="FRP")
# ax.plot(hds_fire.Time, hfrp, color='tab:red', label = 'FRP', lw =-.1)
# ax.scatter(daily_ds.Time, hfwi, color='tab:red',  label = 'FRP',zorder =0, s =46)

set_axis_postion(ax2, "FRP")
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
if save_fig == True:
    plt.savefig(
        str(save_dir) + f"/timeseries-interp-final-{start_save}-{stop_save}-test2.png",
        dpi=250,
        bbox_inches="tight",
    )


# ####################### End Plot Interp FRP vs FWI ############################


# ################################ Plot Interp FRP vs FWI ################################
# start = pd.to_datetime(study_range[0]).strftime("%B %d")
# stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
# start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
# stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
# year = pd.to_datetime(study_range[-1]).strftime("%Y")
# hfwi = hds_fire['S'].values
# hfrp = frp_interp.values
# dfwi = dds_fire['S'].values
# fig = plt.figure(figsize=(12, 4))
# fig.suptitle(f"FWI vs FRP", fontsize=20)
# ax = fig.add_subplot(1, 1, 1)
# ax.set_title(
#     f"{start} - {stop}, {year} \n",
#     loc="right",
#     fontsize=14,
# )
# ax.set_title(f"r: {round(pearsonr_h_interp[0],2)} Hourly FWI \nr: {round(pearsonr_d_interp[0],2)}   Daily FWI ", loc="right", fontsize=10)
# ax2 = ax.twinx()
# ax.plot(hds_fire.Time, hfwi, color='tab:blue', lw = 1.2, label = 'Hourly')
# ax.plot(dds_fire.Time, dfwi, color='tab:blue', ls = '--', lw = 1.2, label = 'Daily')
# ax.plot(dds_fire.Time, hfwi, color='tab:red', lw = 1, label = 'FRP', zorder = 0)

# set_axis_postion(ax, "FWI")

# ax2.plot(frp_interp.index, hfrp, color='tab:red', lw = 1.2, label = 'FRP')
# # ax.plot(hds_fire.Time, hfrp, color='tab:red', label = 'FRP', lw =-.1)
# # ax.scatter(daily_ds.Time, hfwi, color='tab:red',  label = 'FRP',zorder =0, s =46)

# set_axis_postion(ax2, "FRP")
# tkw = dict(size=4, width=1.5, labelsize=14)
# ax.tick_params(
#     axis="x",
#     **tkw,
# )
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
# ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
# ax.legend(
#     # loc="upper right",
#     bbox_to_anchor=(0.38, 1.18),
#     ncol=3,
#     fancybox=True,
#     shadow=True,
#     fontsize=12,
# )
# if save_fig == True:
#     plt.savefig(
#         str(save_dir) + f"/timeseries-interp-{start_save}-{stop_save}.png",
#         dpi=250,
#         bbox_inches="tight",
#     )


# ####################### End Plot Interp FRP vs FWI ############################


# ################################ Plot FRP vs FWI ############################
# start = pd.to_datetime(study_range[0]).strftime("%B %d")
# stop = pd.to_datetime(study_range[-1]).strftime("%B %d")
# start_save = pd.to_datetime(study_range[0]).strftime("%Y%m%d")
# stop_save = pd.to_datetime(study_range[-1]).strftime("%Y%m%d")
# year = pd.to_datetime(study_range[-1]).strftime("%Y")
# hfwi = hourly_ds['S'].values
# hfrp = hourly_ds['FRP'].values
# dfwi = daily_ds['S'].values
# fig = plt.figure(figsize=(12, 4))
# fig.suptitle(f"FWI vs FRP", fontsize=20)
# ax = fig.add_subplot(1, 1, 1)
# ax.set_title(
#     f"{start} - {stop}, {year} \n",
#     loc="right",
#     fontsize=14,
# )
# ax.set_title(f"r: {round(pearsonr_h[0],2)} Hourly FWI \nr: {round(pearsonr_d[0],2)}   Daily FWI ", loc="right", fontsize=10)
# ax2 = ax.twinx()
# ax.plot(hourly_ds.Time, hfwi, color='tab:blue', label = 'Hourly', lw = 1.2)
# ax.scatter(hourly_ds.Time, hfwi, color='tab:blue',  s = 10)
# ax.plot(daily_ds.Time, dfwi, color='tab:blue', ls = '--', label = 'Daily',lw = 1.2)
# ax.scatter(hourly_ds.Time, dfwi, color='tab:blue',  s = 10)
# ax.plot(daily_ds.Time, hfwi, color='tab:red',  label = 'FRP',zorder =0, lw = 1.)

# set_axis_postion(ax, "FWI")

# ax2.plot(hourly_ds.Time, hfrp, color='tab:red', lw = 1.2)
# ax2.scatter(hourly_ds.Time, hfrp, color='tab:red',  s = 10)

# set_axis_postion(ax2, "FRP")
# tkw = dict(size=4, width=1.5, labelsize=14)
# ax.tick_params(
#     axis="x",
#     **tkw,
# )
# plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
# ax.set_xlabel("Local DateTime (MM-DD)", fontsize=16)
# ax.legend(
#     # loc="upper right",
#     bbox_to_anchor=(0.38, 1.18),
#     ncol=3,
#     fancybox=True,
#     shadow=True,
#     fontsize=12,
# )
# if save_fig == True:
#     plt.savefig(
#         str(save_dir) + f"/timeseries-{start_save}-{stop_save}.png",
#         dpi=250,
#         bbox_inches="tight",
#     )

# print(f"hourly pearsonr: {pearsonr_h[0]}")
# print(f"daily pearsonr: {pearsonr_d[0]}")

# print(f"hourly interp pearsonr: {pearsonr_h_interp[0]}")
# print(f"daily interp pearsonr: {pearsonr_d_interp[0]}")
# ################### End Plot FRP vs FWI ###################


# # # Create subplots with two y-axes
# # fig = make_subplots(specs=[[{"secondary_y": True}]])

# # # Add traces to the first y-axis
# # fig.add_trace(go.Scatter(x=hourly_ds.Time, y=hfwi, name="FWI"), secondary_y=False)

# # # Add traces to the second y-axis
# # fig.add_trace(go.Scatter(x=hourly_ds.Time, y=hfrp, name="FRP"), secondary_y=True)

# # # Set y-axis labels
# # fig.update_yaxes(title_text="FWI", secondary_y=False)
# # fig.update_yaxes(title_text="FRP", secondary_y=True)

# # # Set x-axis label
# # fig.update_xaxes(title_text="Local Time")

# # # Show the plot
# # fig.show()


# # # Create subplots with two y-axes
# # fig = make_subplots(specs=[[{"secondary_y": True}]])

# # # Add traces to the first y-axis
# # fig.add_trace(go.Scatter(x=hds_fire.Time, y=hds_fire['S'], name="FWI"), secondary_y=False)

# # # Add traces to the second y-axis
# # fig.add_trace(go.Scatter(x=hds_fire.Time, y=frp_interp, name="FRP"), secondary_y=True)

# # # Set y-axis labels
# # fig.update_yaxes(title_text="FWI", secondary_y=False)
# # fig.update_yaxes(title_text="FRP", secondary_y=True)

# # # Set x-axis label
# # fig.update_xaxes(title_text="Local Time")

# # # Show the plot
# # fig.show()
