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

from context import data_dir, xr_dir, wrf_dir, tzone_dir
from datetime import datetime, date, timedelta
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
from scipy import stats
from matplotlib.offsetbox import AnchoredText

import warnings

warnings.filterwarnings("ignore")

warnings.filterwarnings("ignore", category=FutureWarning)

wrf_model = "wrf4"
# models = ["_era5", "_wrf01",  "_wrf02",  "_wrf03",  "_wrf04"]
models = ["_era5", "_wrf01"]

domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2021, 11, 1)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
)

ds = ds.sel(time=slice("2021-04-01", "2021-11-01"))

date_range = pd.date_range(ds.time.values[0], ds.time.values[-1])
ds = ds.chunk(chunks="auto")
ds = ds.unify_chunks()
for var in list(ds):
    ds[var].encoding = {}

if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

df = ds.to_dataframe().dropna()
df = df.reset_index()
# df = df[~np.isnan(df.bui)]
# df = df[~np.isnan(df[f"bui_day1_{method}"])]

unique, counts = np.unique(df.wmo.values, return_counts=True)
# wmo_of_int = unique[counts > 170]
# df = df[df.wmo.isin(wmo_of_int)]
# unique, counts = np.unique(df.wmo.values, return_counts=True)


var_list = list(ds)[::3]
time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


##########################################################################
##########################################################################

var_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
#
length = len(var_list)
for i in range(length):
    # plt.subplot(i+1, 1, 1)
    var = var_list[i]
    df_final = df[~np.isnan(df[var])]
    df_final = df[np.abs(df[var] - df[var].mean()) <= (2.5 * df[var].std())]
    stats_text = ""
    for j in range(len(models)):
        model = models[j]
        model_name = model.strip("_").upper()
        if model_name == "ERA5":
            # model_name += " "
            pass
        elif model_name == "WRF01":
            model_name = "WRF "
        else:
            pass
        r2value = round(
            stats.pearsonr(df_final[var].values, df_final[var + model].values)[0], 2
        )
        rmse = str(
            round(
                mean_squared_error(
                    df_final[var].values, df_final[var + model].values, squared=False
                ),
                2,
            )
        )
        mae = str(
            round(
                mean_absolute_error(df_final[var].values, df_final[var + model].values),
                2,
            )
        )
        print(
            f"{model_name}  {var.upper()} (r): {r2value} (rmse): {rmse} (mae): {mae} \n"
        )
        # df_final = df_final.groupby("time").mean()


# import context
# import json
# import numpy as np
# import pandas as pd
# import xarray as xr
# from pathlib import Path
# from netCDF4 import Dataset
# import scipy.stats
# import cartopy.crs as ccrs
# import cartopy.feature as cfeature
# import matplotlib.colors
# import matplotlib.pyplot as plt
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# import scipy.ndimage as ndimage
# from scipy.ndimage.filters import gaussian_filter
# from pylab import *
# import plotly.express as px

# from context import data_dir, xr_dir, wrf_dir, tzone_dir
# from datetime import datetime, date, timedelta
# from sklearn.metrics import mean_squared_error, mean_absolute_error
# from sklearn.metrics import r2_score
# from scipy import stats
# from matplotlib.offsetbox import AnchoredText

# import warnings
# warnings.filterwarnings("ignore")


# wrf_model = "wrf4"
# # models = ["_era5", "_wrf01",  "_wrf02",  "_wrf03",  "_wrf04"]
# models = ["_era5", "_wrf01"]

# domain = "d02"
# # date = pd.Timestamp("today")
# date = pd.Timestamp(2021, 11, 1)

# intercomp_today_dir = date.strftime("%Y%m%d")

# with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
#     var_dict = json.load(fp)

# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-{intercomp_today_dir}.zarr",
# )

# ds = ds.sel(time=slice("2021-04-01", "2021-11-01"))

# date_range = pd.date_range(ds.time.values[0], ds.time.values[-1])
# ds = ds.chunk(chunks="auto")
# ds = ds.unify_chunks()
# for var in list(ds):
#     ds[var].encoding = {}

# if domain == "d02":
#     res = "12 km"
# else:
#     res = "4 km"

# df = ds.to_dataframe().dropna()
# df = df.reset_index()


# unique, counts = np.unique(df.wmo.values, return_counts=True)


# var_list = list(ds)[::3]
# time = np.array(ds.time.dt.strftime("%Y-%m-%d"), dtype="<U10")
# start_time = datetime.strptime(str(time[0]), "%Y-%m-%d").strftime("%Y%m%d")
# end_time = datetime.strptime(str(time[-1]), "%Y-%m-%d").strftime("%Y%m%d")
# colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]


# ##########################################################################
# ##########################################################################

# var_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]

# length = len(var_list)
# for i in range(length):
#     var = var_list[i]
#     df_final = df[~np.isnan(df[var])]
#     df_final = df[np.abs(df[var] - df[var].mean()) <= (2.5 * df[var].std())]

#     for j in range(len(models)):
#         model = models[j]
#         model_name = model.strip('_').upper()
#         if model_name == 'ERA5':
#             # model_name += " "
#             pass
#         elif model_name == 'WRF01':
#             model_name = 'WRF '
#         else:
#             pass
#         # print(var + model)
#         r2value = round(
#             stats.pearsonr(df_final[var].values, df_final[var + model].values)[0], 2
#         )
#         rmse = str(
#             round(
#                 mean_squared_error(
#                     df_final[var].values, df_final[var + model].values, squared=False
#                 ),
#                 2,
#             )
#         )
#         mae = str(round(mean_absolute_error(df_final[var].values, df_final[var + model].values),2))


#         stats_text =  f"{model_name}  {var.upper()} (r): {r2value} (rmse): {rmse} (mae): {mae} \n"
#         print( f"{model_name}  {var.upper()} (r): {r2value} (rmse): {rmse} (mae): {mae} \n")
