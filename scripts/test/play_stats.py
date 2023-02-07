import context

import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd


import salem

from netCDF4 import Dataset
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.stats import pearsonr

from sklearn.metrics import mean_squared_error, mean_absolute_error


from datetime import datetime
from context import data_dir


startTime = datetime.now()
domain = "d02"
var = "temp"
date = pd.Timestamp(2022, 7, 2)
doi = date.strftime("%Y%m%d")

## TODO Solve stats at every indivivual station location then plot them on map

obs_ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-{domain}-20220730.zarr",
)


var = "fwi"
df = obs_ds.to_dataframe().dropna()
df_final = df[~np.isnan(df[var])]
df_final = df_final[
    np.abs(df_final[var] - df_final[var].mean()) <= (2.5 * df_final[var].std())
]

print(mean_squared_error(df_final[f"{var}"], df_final[f"{var}_day1_interp"]))


# var_list = list(obs_ds)
# var_list = [ x for x in var_list if "_" not in x ]
# var_list = var_list[::-1]


stats_list = []
# for var in var_list:
try:
    stats_ds = xr.open_zarr(str(data_dir) + "/intercomp/" + f"stats-{var}.zarr")
except:

    print(var)
    var_obs_ds = obs_ds[var].dropna(dim="wmo", how="all")
    var_wrf_ds = obs_ds[f"{var}_day1_interp"].sel(wmo=var_obs_ds.wmo)
    var_era5_ds = obs_ds[f"{var}_era5_interp"].sel(wmo=var_obs_ds.wmo)

    def MBE(y_true, y_pred):
        """
        Parameters:
            y_true (array): Array of observed values
            y_pred (array): Array of prediction values

        Returns:
            mbe (float): Biais score
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        y_true = y_true.reshape(len(y_true), 1)
        y_pred = y_pred.reshape(len(y_pred), 1)
        diff = y_true - y_pred
        mbe = diff.mean()
        # print('MBE = ', mbe)
        return mbe

    # test = var_ds[.isel(wmo = 0).values
    xr_list, good_wmo = [], []
    for wmo in var_obs_ds.wmo.values:
        var_obs_da = var_obs_ds.sel(wmo=wmo).dropna(dim="time", how="all")
        var_obs_da = var_obs_da[
            np.abs(var_obs_da - var_obs_da.mean()) <= (2.5 * var_obs_da.std())
        ]
        if len(var_obs_da) < 31:
            print(f"wmo {wmo} has only {len(var_obs_da)} sample points")
        else:

            var_wrf_da = var_wrf_ds.sel(time=var_obs_da.time.values, wmo=wmo)
            var_era5_da = var_era5_ds.sel(time=var_obs_da.time.values, wmo=wmo)

            xr_var = xr.Dataset(
                data_vars=dict(
                    mae_wrf=(["wmo"], [mean_absolute_error(var_obs_da, var_wrf_da)]),
                    rmse_wrf=(["wmo"], [mean_squared_error(var_obs_da, var_wrf_da)]),
                    pr_wrf=(["wmo"], [float(pearsonr(var_obs_da, var_wrf_da)[0])]),
                    mbe_wrf=(["wmo"], [MBE(var_obs_da, var_wrf_da)]),
                    mae_era5=(["wmo"], [mean_absolute_error(var_obs_da, var_era5_da)]),
                    rmse_era5=(["wmo"], [mean_squared_error(var_obs_da, var_era5_da)]),
                    pr_era5=(["wmo"], [float(pearsonr(var_obs_da, var_era5_da)[0])]),
                    mbe_era5=(["wmo"], [MBE(var_obs_da, var_era5_da)]),
                ),
                coords={
                    "wmo": np.atleast_1d(wmo),
                    "lats": ("wmo", [float(var_obs_da.coords["lats"])]),
                    "lons": ("wmo", [float(var_obs_da.coords["lons"])]),
                    "elev": ("wmo", [float(var_obs_da.coords["elev"])]),
                    "name": ("wmo", [str(var_obs_da.coords["name"].values)]),
                    "prov": ("wmo", [str(var_obs_da.coords["prov"].values)]),
                    "id": ("wmo", [str(var_obs_da.coords["id"].values)]),
                    "tz_correct": ("wmo", [float(var_obs_da.coords["tz_correct"])]),
                    "samples": ("wmo", [len(var_obs_da)]),
                },
            )

            xr_list.append(xr_var)
            good_wmo.append(wmo)

    print(f"there are {len(good_wmo)} stations for {var} starts")
    stats_ds = xr.merge(xr_list)
    # stats_list.append(stats_ds)
    stats_ds.to_zarr(str(data_dir) + "/intercomp/" + f"stats-{var}.zarr", mode="w")
    print(f"{var} stats made")


# obs_ds1 = obs_ds.sel(time=doi)
# obs_ds1 = obs_ds.mean(dim = 'time')
# obs_ds = obs_ds.sel(wmo = 71741)

# obs_df = obs_ds.to_dataframe()
# obs_df = obs_df[~np.isnan(obs_df[var])]
# obs_df = obs_df[np.abs(obs_df[var] - obs_df[var].mean()) <= (2.5 * obs_df[var].std())]
# obs_df = obs_df.reset_index()

# obs_df[f"{var}_diff"] = obs_df[var] - obs_df[f"{var}_day1_interp"]
# obs_df[f"{var}_diff_abs"] = np.abs(obs_df[f"{var}_diff"])
# print(f"{len(obs_df)} number of observations")
# obs_df[f"{var}_mae"] = mean_absolute_error(obs_df[var], obs_df[f"{var}_day1_interp"])
# obs_df[f"{var}_rmse"] = mean_squared_error(obs_df[var], obs_df[f"{var}_day1_interp"], squared=False)
# obs_df[f"{var}_pr"] = float(pearsonr(obs_df[var], obs_df[f"{var}_day1_interp"])[0])
# obs_df[f"{var}_mbe"] = MBE(obs_df[var], obs_df[f"{var}_day1_interp"])


# fig = px.scatter_mapbox(
#     obs_df,
#     lat="lats",
#     lon="lons",
#     color=f"{var}_rmse",
#     # size="pr_wrf",
#     color_continuous_scale="jet",
#     hover_name="wmo",
#     center={"lat": 50.0, "lon": -110.0},
#     hover_data=[f"{var}_rmse"],
#     mapbox_style="carto-positron",
#     zoom=1.5,
# )
# fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
# fig.show()


# # fig = px.line(obs_df, x='time', y=f"{var}_diff")
# # fig.show()

stats_df = stats_ds.to_dataframe().reset_index()

metric = "rmse_wrf"
stats_df = stats_df[
    np.abs(stats_df[metric] - stats_df[metric].mean()) <= (2.5 * stats_df[metric].std())
]

fig = px.scatter_mapbox(
    stats_df,
    lat="lats",
    lon="lons",
    color=metric,
    # size="pr_wrf",
    color_continuous_scale="jet",
    hover_name="wmo",
    center={"lat": 50.0, "lon": -110.0},
    hover_data=["pr_wrf", "pr_era5"],
    mapbox_style="carto-positron",
    zoom=1.5,
)
fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
fig.show()
