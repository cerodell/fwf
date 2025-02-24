#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import json
import salem
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib

from utils.ml_data import MLDATA
import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from scipy import stats
from utils.stats import MBE, RMSE
from sklearn.metrics import r2_score
from datetime import datetime
from context import data_dir
from utils.firep import FIREP

from netCDF4 import Dataset
from wrf import to_np, getvar, get_cartopy, latlon_coords, g_uvmet, ll_to_xy, xy_to_ll
from sklearn.preprocessing import (
    StandardScaler,
    RobustScaler,
    MinMaxScaler,
    PowerTransformer,
)
from sklearn.utils import shuffle


config = dict(model="wrf", trail_name="01", method="hourly", year="2021", domain="d02")
## Initialize RAVE, FWX and VIIRS data with the configuration
firep = FIREP(config=config)
firep_df = firep.open_firep()
fire_i = firep_df[firep_df["id"] == int(24360611)]

test = xr.open_dataset("/Volumes/ThunderBay/CRodell/fires/d02/2021-24360611.nc")
test1 = xr.open_dataset("/Volumes/ThunderBay/CRodell/fires/2021-24360611.nc")


test1["FRP"].mean(("x", "y")).plot()
test["FRP"].mean(("south_north", "west_east")).plot()


# Create a gridspec layout
# The first row (for maps) is twice the height of the second row (for line plots)
g = salem.GoogleVisibleMap(
    x=[fire_i.min_x, fire_i.max_x],
    y=[fire_i.min_y, fire_i.max_y],
    scale=2,  # scale is for more details
    maptype="satellite",
)  # try out also: 'terrain'


ds_time_avg = test1.mean(dim="time")
ds_time_avg["FRP"].attrs = test1["FRP"].attrs
# First map on the top left
fig = plt.figure(figsize=(6, 6))
ax = fig.add_subplot(1, 1, 1)
ax.set_title("FRP (MW)")
sm = salem.Map(g.grid, factor=1, countries=False, cmap="YlOrRd", vmax=1400)
sm.set_shapefile(fire_i, lw=1.5, color="tab:red")
sm.set_data(ds_time_avg["FRP"], overplot=True)
# sm.set_data(fwx_roi.sel(time = doi), overplot=True)
sm.set_scale_bar(
    location=(0.88, 0.94),
)
sm.visualize(ax=ax)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
