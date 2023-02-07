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
from scipy.ndimage import gaussian_filter
from pylab import *

import plotly.express as px


from context import data_dir, xr_dir, wrf_dir, tzone_dir
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


domain = "d02"
test_case = "WRF05060708"
date = pd.Timestamp(2022, 10, 31)


intercomp_today_dir = date.strftime("%Y%m%d")


# ds = xr.open_zarr(
#     str(data_dir)
#     + "/intercomp/"
#     + f"final-intercomp-{domain}-{intercomp_today_dir}.zarr",
# )

ds = xr.open_dataset(str(data_dir) + f"/intercomp/d02/{test_case}/20210101-20221031.nc")
# ds = ds.sel(time=slice("2022-01-01", "2022-10-01"))
# tmax = ds.tmax.sortby(ds.wmo)


wmo = 71255
# wmo = 71163
# wmo = 3258
# wmo = 71354
# wmo = 71741

# wmo = 7244
# wmo = 7416
# wmo = 721572
# ds_wmo = ds.sel(wmo =wmo, time = slice('2021-11-02', '2022-04-08'))
# ds_wmo = ds.sel(wmo =wmo, time = slice('2021-09-01', '2022-10-01'))\
# ds = ds.reset_coords()
# ds = ds.set_coords(["lats", "lons", "id", "name", "prov", "elev", "tz_correct"])

# ds['prov'] = ds['prov'].astype(str)

# ds = ds.set_index({"prov": "wmo"})

# ds['prov'].sel(prov = 'BC')

# ds = ds.assign_coords(prov= ("wmo",ds['prov'].values ))
# provs = xr.DataArray(np.array(["BC", "AB"]), dims= 'prov')

# ds_wmo2 = ds['fwi'].sel(prov = "BC")

# test = ds.sel(tz_correct = -7)

provs = [
    "YT",
    "BC",
    "AB",
    "MB",
    "NB",
    "NE",
    "NF",
    "NS",
    "NT",
    "NU",
    "SK",
    "PE",
    "QC",
    "ON",
]
index = np.isin(ds["prov"].values, provs)

ds_wmo = ds.isel(wmo=index)
ds_wmo = ds_wmo.sel(time=slice("2021-06-01", "2021-09-01"))
ds_wmo = ds_wmo.dropna(dim="wmo", how="any")
ds_wmo = ds_wmo.mean(dim="wmo")
df = ds_wmo.to_dataframe()
df = df.reset_index()


var = "ffmc"
title_list = ["prov", "wmo", "lats", "lons"]
# fig = px.line(df, x="time", y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"],title="  ".join([f'{i} = {str(ds_wmo[i].values)}' for i in title_list]),)
fig = px.line(
    df,
    x="time",
    y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"],
)
fig.show()


# ds = ds.set_coords(("lats", "lons", "id", "name", "prov", "elev", "tz_correct"))
# ds['prov'] = ds['prov'].astype(str)
var = "fwi"
var_list = [var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"]

# ds1 = ds.sel(time=slice("2021-06-01", "2021-09-01"))
# ds1 = ds1.copy()[var_list]


prov_list, counts = np.unique(ds["prov"], return_counts=True)
# prov_list = prov_list[counts>2]
# counts = counts[counts>2]

# for prov, count in zip(prov_list, counts):
#     ds_wmo2 = ds1.isel(wmo=np.where(ds['prov'] == prov)[0])
#     ds_wmo1 = ds_wmo2.dropna(dim = 'wmo', how = 'any')
#     ds_wmo = ds_wmo1.mean(dim = 'wmo')

#     df = ds_wmo.to_dataframe()
#     df = df.reset_index()

#     var = 'fwi'
#     fig = px.line(df, x="time", y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"], title= f"{prov}: {count}")
#     fig.show()


# r_w_list = []
# sum_rain = 0
# for i in range(len(ds_wmo.time)):
#     sum_rain += ds_wmo.precip.isel(time=i).values
#     r_w_list.append(sum_rain)

# r_w = xr.DataArray(np.array(r_w_list), name="r_w_obs", dims="time")

# ds_wmo["r_w_obs"] = r_w
# ds_wmo.r_w.plot()
# ds_wmo.r_w_obs.plot()


# var = 'fwi'
# title_list = ['prov', 'wmo', 'lats', 'lons']
# fig = px.line(df, x="time", y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"],title="  ".join([f'{i} = {str(ds_wmo[i].values)}' for i in title_list]),)
# fig.show()

# fig = px.line(df, x="time", y=["dfs"])
# fig.show()

# fig = px.line(df, x="time", y=["r_w"])
# fig.show()

# fig = px.line(df, x="time", y=["fs"])
# fig.show()

# # %%
# ds_mow1 = ds_wmo.sel(time = slice('2021-04-14', '2022-11-01'))
# # ds_mow1.dc.values
# ds_mow1.dc.plot()

# 564

# 175


# # ds_mow1.tmax.plot()

# # %%
# var = 'dc'
# fig = plt.figure(figsize=[8, 4])
# ax = fig.add_subplot(1, 1,1)

# title_list = ['prov', 'wmo', 'lats', 'lons']
# ax.set_title("  ".join([f'{i} = {str(ds_mow1[i].values)}' for i in title_list]), fontsize=14)
# ax.tick_params(axis="x", rotation=45)
# ax.plot(
#     ds_mow1.time,
#     ds_mow1.dc,
#     label="Observation",
#     zorder=2,
#     lw=2,
# )
# ax.plot(
#     ds_mow1.time,
#     ds_mow1.dc_wrf05,
#     label="WRF Overwinter",
#     zorder=2,
#     lw=2,
# )
# ax.plot(
#     ds_mow1.time,
#     ds_mow1.dc_wrf06,
#     label="WRF No Overwinter",
#     zorder=2,
#     lw=2,
# )
# ax.legend(
#     loc="upper center",
#     bbox_to_anchor=(0.5, 1.3),
#     ncol=4,
#     fancybox=True,
#     shadow=True,
# )
# ax.set_ylabel("Drought Code")
# ax.set_xlabel("Time")
# ax.yaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
# ax.xaxis.grid(linewidth=0.4, linestyle="--", zorder=1)
# # %%
# # ds_mow1.dc.plot(label="WRF No Overwinter",add_legend=True)
# # ds_mow1.dc_wrf05.plot()
# # ds_mow1.dc_wrf06.plot()

# # ds.plot.scatter('ws', 'ws_wrf05')
# ds_wmo = ds_mow1
# ds_time = xr.Dataset(
#     {
#         "F": (["time"], ds_wmo["ffmc"].values),
#         "P": (["time"], ds_wmo["dmc"].values),
#         "D": (["time"], ds_wmo[f"{var}"].values),
#         "W": (["time"], ds_wmo["ws"].values),
#         "WD": (["time"], ds_wmo["wdir"].values),
#         "T": (["time"], ds_wmo["temp"].values),
#         "H": (["time"], ds_wmo["rh"].values),
#         "r_o": (["time"], ds_wmo["precip"].values),

#     }
# )
# ds_time = ds_time.assign_coords({"time": ("time", ds_wmo.time.values)})
# date_range = ds_time.time.values[1:]


# F, P, D = ds_time.F.isel(time = 0), ds_time.P.isel(time = 0), ds_time.D.isel(time = 0)
# ## loop and solve fwi system for specified range of days
# datasets = []
# for i in range(len(date_range)):
#     ts = pd.to_datetime(str(date_range[i]))
#     ds = ds_time.sel(time=ts.strftime("%Y-%m-%d"))
#     month = int(ts.strftime("%m"))
#     ## Daylength factor in Duff Moisture Code
#     L_e = [6.5, 7.5, 9.0, 12.8, 13.9, 13.9, 12.4, 10.9, 9.4, 8.0, 7.0, 6.0]
#     L_e = L_e[month - 1]

#     ## Daylength adjustment in Drought Code
#     L_f = [-1.6, -1.6, -1.6, 0.9, 3.8, 5.8, 6.4, 5.0, 2.4, 0.4, -1.6, -1.6]
#     L_f = L_f[month - 1]
#     ds = solve_ffmc(ds, F)

#     ds = solve_dmc(ds, P, L_e)
#     ds = solve_dc(ds, D, L_f)
#     ds = solve_isi(ds)
#     ds = solve_bui(ds)
#     ds = solve_fwi(ds)
#     datasets.append(ds)
#     # redefine moisture codes then drop for interation
#     F = ds.F
#     P = ds.P
#     D = ds.D
#     ds = ds.drop_vars(["F", "P", "D"])

# ## concat all times on a new dimension time
# ds_concat = xr.concat(datasets, dim="time")
# # ds_all.append(ds_concat)

# # ds_time = ds_time.isel(time = slice(1,))
# ds_time.D.plot()
# ds_concat.D.plot()
# ds_mow1.dc_wrf06.plot()
# ds_mow1.dc_wrf05.plot()

# # %%

# ds_time.r_o.plot()
# ds_mow1.precip_wrf06.plot()

# plt.scatter(ds_concat.D, ds_mow1.dc_wrf06[:-1])

# plt.scatter(ds_concat.T, ds_mow1.temp_wrf06[:-1])
