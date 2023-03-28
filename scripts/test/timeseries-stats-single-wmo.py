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
import plotly.express as px
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.ndimage as ndimage
from scipy.ndimage.filters import gaussian_filter
from pylab import *

from context import data_dir, xr_dir, wrf_dir, tzone_dir, root_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText
import matplotlib
from pathlib import Path
from utils.fwi import (
    solve_ffmc,
    solve_dmc,
    solve_dc,
    solve_isi,
    solve_bui,
    solve_fwi,
)

matplotlib.rcParams.update({"font.size": 14})

import warnings

warnings.filterwarnings("ignore")

warnings.filterwarnings("ignore", category=FutureWarning)

wrf_model = "wrf4"
# models = ["_era5", "_wrf05",  "_wrf02",  "_wrf03",  "_wrf04"]
models = ["_wrf05", "_wrf06"]


## test case
test_case = "WRF050607"
## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{test_case}/")
save_dir.mkdir(parents=True, exist_ok=True)


domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2022, 10, 31)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)


ds = xr.open_dataset(str(data_dir) + f"/intercomp/d02/{test_case}/20210101-20221031.nc")
# ds = ds.sel(time=slice("2022-04-01", "2022-10-01"))
# ds = ds.load()


time = ds.time.values

# ds1 = ds.sel(wmo = 72677)
ds1 = ds.isel(wmo=500)

var = "fwi"
var_list = [var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07"]
ds1 = ds1.copy()[var_list]
df = ds1.to_dataframe()
df = df.reset_index()

title_list = ["prov", "wmo", "lats", "lons"]
fig = px.line(
    df,
    x="time",
    y=var_list,
    title="  ".join([f"{i} = {str(ds1[i].values)}" for i in title_list]),
)
fig.show()


# var = 'dc'
# fig = plt.figure(figsize=[10, 4])
# ax = fig.add_subplot(1, 1,1)
# ax.plot(time,ds1[var], label = 'OBS')
# ax.plot(time,ds1[f"{var}_wrf05"],  label = 'WRF05')
# ax.plot(time,ds1[f"{var}_wrf06"],  label = 'WRF06')
# ax.plot(time,ds1[f"{var}_wrf07"],  label = 'WRF07')
# ax.tick_params(axis="x", rotation=45)
# ax.legend()
# fig.suptitle(var.upper(), fontsize=16)

# var = 'fwi'
# fig = plt.figure(figsize=[10, 4])
# ax = fig.add_subplot(1, 1,1)
# ax.plot(time,ds1[var], label = 'OBS')
# ax.plot(time,ds1[f"{var}_wrf05"],  label = 'WRF05')
# ax.plot(time,ds1[f"{var}_wrf06"],  label = 'WRF06')
# ax.plot(time,ds1[f"{var}_wrf07"],  label = 'WRF07')
# ax.tick_params(axis="x", rotation=45)
# ax.legend()
# fig.suptitle(var.upper(), fontsize=16)
