#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import io
import json
import requests
import salem

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
from glob import glob
from pathlib import Path
from netCDF4 import Dataset
import matplotlib.pyplot as plt
from wrf import ll_to_xy, xy_to_ll
from datetime import datetime, date, timedelta
from utils.compressor import compressor, file_size

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

from context import data_dir, root_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

#################### INPUTS ####################

# config = {"ecmwf": ["era5"]}
# config = {"wrf": ["d02", "d03"]}
config = {"eccc": ["hrdps", "rdps"], "wrf": ["d02", "d03"]}


trail_name = "02"
# model_save = list(config.keys())[0]
# domain_save = config[model_save][0]
model_save = "nwp"
domain_save = "all"
lead_time = 2

# date_range = pd.date_range("2021-01-01", "2021-01-10")
date_range = pd.date_range("2021-01-01", "2022-12-31")
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

# make a file directory based on user inputs to save dataset
save_dir = Path(str(data_dir) + f"/intercomp/{trail_name}/{model_save}/")
save_dir.mkdir(parents=True, exist_ok=True)

################## END INPUTS ##################

var_list = [
    "TD",
    "S",
    "T",
    "WD",
    "W",
    "P",
    "F",
    "r_o",
    "R",
    "H",
    "D",
    "U",
    # "FS",
    # "r_w",
    # "Df",
    # "TMAX",
    # "FS_days",
    # "dFS",
    "mF",
    "mR",
    "mS",
    "hF",
    "hR",
    "hS",
    "mT",
    "mW",
    "mH",
    "mFt",
    "mRt",
    "mSt",
    "mTt",
    "mWt",
    "mHt",
]
drop_vars = ["DSR", "SNOWC", "r_o_hourly", "r_o_tomorrow", "SNOWH"]
drop_cords = ["XLAT", "XLONG", "west_east", "south_north", "XTIME", "time"]
#################### Open static datasets ####################

## open modle config file with varible names and attibutes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Open Data Attributes for writing
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

## open master obs file and slice along date range of interest
ds_obs = xr.open_dataset(str(data_dir) + f"/obs/observations-d02-20191231-20221231.nc")
ds_obs = ds_obs.sel(
    time=slice(date_range[0].strftime("%Y-%m-%d"), date_range[-1].strftime("%Y-%m-%d"))
)

## drop stations right on domain boundaries, also station with bad data.
bad_wx = [2275, 3153, 3167, 3266, 3289, 71977, 71948, 71985, 721571]
for wx in bad_wx:
    ds_obs = ds_obs.drop_sel(wmo=wx)


## convert lat lon coordinate in master obs to meter base x y as define by wrf polar stere projection
df = pd.DataFrame(
    data={
        "lons": ds_obs.lons.values,
        "lats": ds_obs.lats.values,
        "wmo": ds_obs.wmo.values,
        "tz_correct": ds_obs.tz_correct.values * -1,
    }
)


############################### Functions #############################


def get_locs(pyproj_srs):
    # get_locs_time = datetime.now()
    gpm25 = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        #  crs="+init=epsg:4326",
        geometry=gpd.points_from_xy(df["lons"], df["lats"]),
    ).to_crs(pyproj_srs)

    x = xr.DataArray(
        np.array(gpm25.geometry.x),
        dims="wmo",
        coords=dict(wmo=gpm25.wmo.values),
    )
    y = xr.DataArray(
        np.array(gpm25.geometry.y),
        dims="wmo",
        coords=dict(wmo=gpm25.wmo.values),
    )
    # print("Locs Time: ", datetime.now() - get_locs_time)

    return x, y


ds_d02 = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d02.nc")
ds_d03 = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-wrf-d03.nc")
ds_rdps = salem.open_xr_dataset("/Users/crodell/fwf/data/tzone/tzone-eccc-rdps-ST.nc")
ds_hrdps = salem.open_xr_dataset(str(data_dir) + f"/tzone/tzone-eccc-hrdps-ST.nc")

# ds_hrdps = salem.open_xr_dataset(str(data_dir) + f"/static/static-vars-eccc-hrdps.nc")

# ds_d03_new = salem.open_xr_dataset(str(data_dir) + f"/tzone/tzone-wrf-d03-ST.nc")


x_d02, y_d02 = get_locs(ds_d02.attrs["pyproj_srs"])
x_d03, y_d03 = get_locs(ds_d03.attrs["pyproj_srs"])
x_rdps, y_rdps = get_locs(ds_rdps.attrs["pyproj_srs"])
x_hrdps, y_hrdps = get_locs(ds_hrdps.attrs["pyproj_srs"])


locs_dict = {
    "d02": [x_d02, y_d02],
    "d03": [x_d03, y_d03],
    "rdps": [x_rdps, y_rdps],
    "hrdps": [x_hrdps, y_hrdps],
}


# domain = 'd02'
def interp(ds, domain):
    x, y = locs_dict[domain]
    ds = ds.interp(west_east=x, south_north=y, method="nearest")
    ds = ds.drop([var for var in list(ds.coords) if var in drop_cords])
    ds = ds.expand_dims(dim={"domain": [domain]})
    return ds


zone = interp(ds_d03["ZoneST"], "d03")

# plt.scatter(zone_d02.values[0], ds_obs['tz_correct'].values *-1)

ds_d03["ZoneST"].salem.quick_map(vmin=0, vmax=10, prov=True, states=True)

# ds_rdps['ZoneST'].salem.quick_map(vmin = 0, vmax = 10, prov = True, states = True)
# ds_hrdps['ZoneST'].salem.quick_map(vmin = 0, vmax = 10, prov = True, states = True)


df["model"] = zone.values[0]
df["diff"] = zone.values[0] - ds_obs["tz_correct"].values * -1

fig = px.scatter_mapbox(
    df,
    lat="lats",
    lon="lons",
    color="diff",
    # size=f"{var_lower}_bias_abs",
    color_continuous_scale="RdBu_r",
    hover_name="wmo",
    center={"lat": 58.0, "lon": -110.0},
    hover_data=["tz_correct", "model"],
    mapbox_style="carto-positron",
    zoom=1.5,
    # labels={"colorbar": '2m Temperature Bias'}
    range_color=[-2, 2],
)
fig.layout.coloraxis.colorbar.title = "Hour offset from noon"
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()


# ds_d03['ZoneST'] = ds_d03_new['ZoneST']
# ds_d03.to_netcdf(str(data_dir) + f"/static/static-vars-wrf-d03-new.nc")
