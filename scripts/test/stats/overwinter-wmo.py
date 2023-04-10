import context
import json
import salem
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


from context import data_dir, root_dir
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
__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

########################### INPUTS ###########################

config = {"wrf": ["hrdps", "d03"], "eccc": ["rdps", "hrdps"]}
domains = ["hrdps", "d03", "rdps", "hrdps"]

domains = ["era5"]
# domain = 'wrf'
# domain = 'hrdps'
trail_name = "01"
# doi = pd.Timestamp("2021-06-28")
# date_range = pd.date_range("2021-01-01", "2022-10-31")
date_range = pd.date_range("2021-01-01", "2022-12-31")
fwf_dir = f"/Volumes/WFRT-Ext24/fwf-data/"

######################### END INPUTS #########################

#################### Open static datasets ####################

with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

# try:
#     domains_ds = xr.open_dataset(str(data_dir) + f'/intercomp/{trail_name}/provs-20210101-20221231.nc')
# except:
ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/{trail_name}/20210101-20221231.nc",
)  # chunks = 'auto')
ds["time"] = ds["Time"]
# rdps.sel(time =slice("2022-01-11", "2022-12-31")).isel(wmo = 100)['rh'].plot()

# ds = ds.sel(time=slice("2021-04-01", "2022-10-31"))
for var in ["elev", "name", "prov", "id", "domain"]:
    ds[var] = ds[var].astype(str)
# prov_unique, prov_counts = np.unique(ds.prov.values, return_counts=True)

## get wmo stations that are with every domain
idx = np.where(
    (ds.prov == "BC")
    | (ds.prov == "AB")
    | (ds.prov == "SA")
    | (ds.prov == "YT")
    | (ds.prov == "NT")
)[0]
ds = ds.isel(wmo=idx)

# %%
# wmo = 1328
ds_wmo = ds["dc"].mean(dim="wmo")

# %%
# ds_wmo = ds['dc'].isel(wmo=60)
rain_obs = ds_wmo.sel(domain="obs").values
rain_hrdps = ds_wmo.sel(domain="hrdps").values
rain_rdps = ds_wmo.sel(domain="rdps").values
rain_d02 = ds_wmo.sel(domain="d02").values
rain_d03 = ds_wmo.sel(domain="d03").values

Time = ds_wmo["Time"].values
# rain_obs[np.isnan(rain_obs)] = rain_era5[np.isnan(rain_obs)]

rain_hrdps = rain_hrdps[~np.isnan(rain_obs)]
rain_rdps = rain_rdps[~np.isnan(rain_obs)]
rain_d02 = rain_d02[~np.isnan(rain_obs)]
rain_d03 = rain_d03[~np.isnan(rain_obs)]

Time = Time[~np.isnan(rain_obs)]
rain_obs = rain_obs[~np.isnan(rain_obs)]


# def sum_rain(array):
#     r_w_list = []
#     sum_rain = 0
#     # print(ds)
#     for i in range(len(array)):
#         sum_rain +=array[i]
#         r_w_list.append(sum_rain)
#     return np.array(r_w_list)
# rain_obs = sum_rain(rain_obs)
# rain_hrdps = sum_rain(rain_hrdps)
# rain_rdps = sum_rain(rain_rdps)
# rain_d02 = sum_rain(rain_d02)
# rain_d03 = sum_rain(rain_d03)

# def accum_error(obs, fct):
#     error = []
#     sum_rain = 0
#     mae = np.abs(fct - obs)
#     # print(ds)
#     for i in range(len(obs)):
#         sum_rain +=mae[i]
#         error.append(sum_rain)
#     return np.array(error)
# rain_hrdps = accum_error(rain_obs, rain_hrdps)
# rain_rdps = accum_error(rain_obs, rain_rdps)
# rain_d02 = accum_error(rain_obs, rain_d02)
# rain_d03 = accum_error(rain_obs, rain_d03)

# wmo = 71255
var = "precip"
d = {
    "obs": rain_obs,
    "hrdps": rain_hrdps,
    "rdps": rain_rdps,
    "d02": rain_d02,
    "d03": rain_d03,
    "Time": Time,
}
df = pd.DataFrame(d)
title_list = ["prov", "wmo", "lats", "lons"]
# fig = px.line(df, x="time", y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"],title="  ".join([f'{i} = {str(ds_wmo[i].values)}' for i in title_list]),)
fig = px.line(
    df,
    x="Time",
    y=["obs", "hrdps", "d02", "d03"],
)
fig.show()
# %%


# ds_wmo = ds_wmo.sel(time=slice("2021-06-01", "2021-09-01"))
# ds_wmo = ds_wmo.dropna(dim="wmo", how="any")
# ds_wmo = ds_wmo.mean(dim="wmo")
# df = ds_wmo.to_dataframe()
# df = df.reset_index()

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
# ds = ds.set_coords(["lats", "lons", "id", "name", "prov", "elev", ""tz"_correct"])

# ds['prov'] = ds['prov'].astype(str)

# ds = ds.set_index({"prov": "wmo"})

# ds['prov'].sel(prov = 'BC')

# ds = ds.assign_coords(prov= ("wmo",ds['prov'].values ))
# provs = xr.DataArray(np.array(["BC", "AB"]), dims= 'prov')

# ds_wmo2 = ds['fwi'].sel(prov = "BC")

# test = ds.sel("tz"_correct = -7)

# index = np.isin(ds["prov"].values, "AB")

# ds_wmo = ds.isel(wmo=index)
# ds_wmo = ds_wmo.sel(time=slice("2021-06-01", "2021-09-01"))
# ds_wmo = ds_wmo.dropna(dim="wmo", how="any")
# ds_wmo = ds_wmo.mean(dim="wmo")
# df = ds_wmo.to_dataframe()
# df = df.reset_index()

# var = "ffmc"
# title_list = ["prov", "wmo", "lats", "lons"]
# # fig = px.line(df, x="time", y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"],title="  ".join([f'{i} = {str(ds_wmo[i].values)}' for i in title_list]),)
# fig = px.line(
#     df,
#     x="time",
#     y=[var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"],
# )
# fig.show()


# # ds = ds.set_coords(("lats", "lons", "id", "name", "prov", "elev", ""tz"_correct"))
# # ds['prov'] = ds['prov'].astype(str)
# var = "fwi"
# var_list = [var, f"{var}_wrf05", f"{var}_wrf06", f"{var}_wrf07", f"{var}_wrf08"]

# # ds1 = ds.sel(time=slice("2021-06-01", "2021-09-01"))
# # ds1 = ds1.copy()[var_list]


# prov_list, counts = np.unique(ds["prov"], return_counts=True)
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

# %%
