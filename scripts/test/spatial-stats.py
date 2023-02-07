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

import warnings

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=FutureWarning)


wrf_model = "wrf4"
# models = ["_era5", "_wrf01",  "_wrf02",  "_wrf03",  "_wrf04"]
models = ["_era5", "_wrf01"]
models = ["_wrf05", "_wrf07", "_wrf08"]
# models = ["_wrf08"]

domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2021, 11, 1)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

trail_name = "WRF05060708"


ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/d02/{trail_name}/20210101-20221031.nc"
)


# index = np.where(ds.wmo == 721572)
# ds = ds.copy().drop_isel(wmo = index[0])

ds = ds.set_coords(("lats", "lons", "id", "name", "prov", "elev", "tz_correct"))

provs = ["YT", "BC", "AB", "MB", "NB", "NF", "NS", "NT", "NU", "SA", "PE", "QC", "ON"]
# index = np.isin(ds['prov'].values,provs)
# ds = ds.isel(wmo=index)

## define directory to save figures
save_dir = Path(str(data_dir) + f"/images/stats/{trail_name}/")
save_dir.mkdir(parents=True, exist_ok=True)

# ds = ds.sel(time=slice("2022-05-01", "2022-10-01"))
# ds['prov'] = ds['prov'].astype(str)
# ds = ds.where(ds.prov=='AB', drop=True)


# ds = ds.dropna(dim="wmo")


date_range = pd.date_range(ds.time.values[0], ds.time.values[-1])

# ds = ds.chunk(chunks="auto")
# ds = ds.unify_chunks()
for var in list(ds):
    ds[var].encoding = {}

if domain == "d02":
    res = "12 km"
else:
    res = "4 km"

df = ds.to_dataframe().dropna()
df = df.reset_index()
df = df[df.wmo != 721572]
df = df.loc[df["prov"].isin(provs), :]
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
    diff = y_pred - y_true
    mbe = diff.mean()
    # print('MBE = ', mbe)
    return mbe


##########################################################################
##########################################################################


def plotstats(var_list):
    obs_dfs = []
    length = len(var_list)
    for i in range(length):
        var = var_list[i]

        for j in range(len(models)):
            df_final = df[~np.isnan(df[var])]
            # df_final = df_final[(np.percentile(df_final[var],5) < df_final[var]) & (df_final[var] < np.percentile(df_final[var],90))]

            if var == "precip":
                print(
                    f"number of data points before condtion {len(df_final['precip'])}"
                )
                df_final = df_final[df_final["precip"] > 0.01]
                print(f"number of data points after condtion {len(df_final['precip'])}")
            else:
                pass
            df_final = df_final[
                np.abs(df_final[var] - df_final[var].mean())
                <= (2 * df_final[var].std())
            ]
            model = models[j]
            model_name = model.strip("_").upper()
            if model_name == "ERA5":
                # model_name += " "
                pass
            elif model_name == "WRF01":
                model_name = "WRF "
            else:
                pass
            # print(var + model)
            r2value = round(
                stats.pearsonr(df_final[var].values, df_final[var + model].values)[0], 2
            )

            # mbe = str(round(MBE(df_final[var].values, df_final[var + model].values), 2))
            mbe = str(
                round(np.mean(df_final[var + model].values - df_final[var].values), 2)
            )

            mae = str(
                round(
                    mean_absolute_error(
                        df_final[var].values, df_final[var + model].values
                    ),
                    2,
                )
            )

            stats_text = f"{model_name}  {var.upper()} (r): {r2value} (mbe): {mbe} (mae): {mae} \n"
            # print( f"{model_name}  {var.upper()} (r): {r2value} (mbe): {mbe} (mae): {mae} \n")

            df_wmos = df_final.groupby("wmo")
            wmos, maes, mbes, r2values, lats, lons = [], [], [], [], [], []
            for name, group in df_wmos:
                if len(group) < 30:
                    pass
                else:
                    # print(name)
                    wmos.append(name)
                    maes.append(
                        round(
                            mean_absolute_error(
                                group[var].values, group[var + model].values
                            ),
                            2,
                        )
                    )
                    # mbes.append(round(MBE(group[var].values, group[var + model].values), 2))
                    mbes.append(
                        round(np.mean(group[var + model].values - group[var].values), 2)
                    )
                    r2values.append(
                        round(
                            stats.pearsonr(
                                group[var].values, group[var + model].values
                            )[0],
                            2,
                        )
                    )
                    lats.append(group["lats"].values[0])
                    lons.append(group["lons"].values[0])
            # print(mbes)
            d = {
                "wmos": wmos,
                "lats": lats,
                "lons": lons,
                "maes": maes,
                "mbes": mbes,
                "ambes": np.abs(mbes),
                "r2values": r2values,
            }
            obs_df = pd.DataFrame(data=d)
            # obs_df = obs_df[obs_df['maes'] <= 10]
            fig = px.scatter_mapbox(
                obs_df,
                lat="lats",
                lon="lons",
                color="maes",
                # size="ambes",
                # color_continuous_scale="jet",
                # color_continuous_scale=[(-15,'#5952a4'), (-10, '#8ad1a5'), (0,'#f4fba8'), (2.5,'#9f023f')],
                color_continuous_scale=[
                    "#5952a4",
                    "#8ad1a5",
                    "#f4fba8",
                    "#f67346",
                    "#9f023f",
                ],
                # color_continuous_scale=[(0,(159,2,63,255)), (1, (159,2,63,255)), (2, (159,2,63,255))],
                hover_name="wmos",
                # center={"lat": 55.0, "lon": -110.0},
                center={"lat": 60.0, "lon": -100.0},
                hover_data=["maes", "mbes", "r2values"],
                mapbox_style="carto-positron",
                # zoom=1.8,
                zoom=2.3,
                title=stats_text,
                range_color=[0, 15],
            )
            fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
            fig.write_image(
                str(save_dir)
                + f"/{model_name}-{var}-maes-{date_range[0].strftime('%Y%m%d')}-{date_range[-1].strftime('%Y%m%d')}.png",
                scale=2,
            )
            fig.show()

            fig = px.scatter_mapbox(
                obs_df,
                lat="lats",
                lon="lons",
                color="mbes",
                # size="ambes",
                color_continuous_scale="RdBu_r",
                hover_name="wmos",
                # center={"lat": 55.0, "lon": -110.0},
                center={"lat": 60.0, "lon": -100.0},
                hover_data=["maes", "mbes", "r2values"],
                mapbox_style="carto-positron",
                # zoom=1.8,
                zoom=2.3,
                title=stats_text,
                range_color=[-8, 8],
            )
            fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
            fig.write_image(
                str(save_dir)
                + f"/{model_name}-{var}-mbes-{date_range[0].strftime('%Y%m%d')}-{date_range[-1].strftime('%Y%m%d')}.png",
                scale=2,
            )
            fig.show()

            fig = px.scatter_mapbox(
                obs_df,
                lat="lats",
                lon="lons",
                color="r2values",
                color_continuous_scale=[
                    "#5952a4",
                    "#8ad1a5",
                    "#f4fba8",
                    "#f67346",
                    "#9f023f",
                ],
                hover_name="wmos",
                center={"lat": 60.0, "lon": -100.0},
                hover_data=["maes", "mbes", "r2values"],
                mapbox_style="carto-positron",
                zoom=2.3,
                title=stats_text,
                range_color=[0.65, 1],
            )
            fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
            fig.write_image(
                str(save_dir)
                + f"/{model_name}-{var}-r2values-{date_range[0].strftime('%Y%m%d')}-{date_range[-1].strftime('%Y%m%d')}.png",
                scale=2,
            )

            obs_dfs.append(obs_df)
            fig.show()
            print(
                "======================================================================="
            )

    return obs_dfs


##########################################################################
##########################################################################
fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
fwi_list = ["fwi"]

obs_dfs = plotstats(fwi_list)

# obs_df = obs_dfs[-1] - obs_dfs[0]
# obs_df['wmos'] = obs_dfs[0]['wmos']
# obs_df['lats']= obs_dfs[0]['lats']
# obs_df['lons']= obs_dfs[0]['lons']


# fig = px.scatter_mapbox(
#     obs_df,
#     lat="lats",
#     lon="lons",
#     color="ambes",
#     # size="ambes",
#     color_continuous_scale="RdBu_r",
#     hover_name="wmos",
#     center={"lat": 55.0, "lon": -110.0},
#     hover_data=["maes", "mbes", "r2values"],
#     mapbox_style="carto-positron",
#     zoom=1.8,
#     # title=stats_text,
#     range_color= [-4,4],
# )
# fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))

##########################################################################
##########################################################################
# met_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
# met_list = ["precip"]

# plotstats(met_list)
