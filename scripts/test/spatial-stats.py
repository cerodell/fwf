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

domain = "d02"
# date = pd.Timestamp("today")
date = pd.Timestamp(2021, 11, 1)

intercomp_today_dir = date.strftime("%Y%m%d")

with open(str(data_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/" + f"era5wrf02-intercomp-{domain}-{intercomp_today_dir}.zarr",
# )
ds = xr.open_zarr(
    str(data_dir) + "/intercomp/" + f"intercomp-d02-20211101.zarr",
)
ds = ds.sel(time=slice("2021-05-01", "2021-10-01"))
ds = ds.load()
ds = ds.dropna(dim="wmo")


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


##########################################################################
##########################################################################


def plotstats(var_list):
    length = len(var_list)
    for i in range(length):
        var = var_list[i]

        for j in range(len(models)):
            df_final = df[~np.isnan(df[var])]
            if var == "precip":
                print(
                    f"number of data points before condtion {len(df_final['precip'])}"
                )
                df_final = df_final[df_final["precip"] > 0.01]
                print(f"number of data points after condtion {len(df_final['precip'])}")
            else:
                pass
            df_final = df_final[
                np.abs(df[var] - df_final[var].mean()) <= (2 * df_final[var].std())
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

            mbe = str(round(MBE(df_final[var].values, df_final[var + model].values), 2))
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
            wmos, maes, lats, lons = [], [], [], []
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
                    lats.append(group["lats"].values[0])
                    lons.append(group["lons"].values[0])

            d = {"wmos": wmos, "lats": lats, "lons": lons, "maes": maes}
            obs_df = pd.DataFrame(data=d)

            fig = px.scatter_mapbox(
                obs_df,
                lat="lats",
                lon="lons",
                color=f"maes",
                # size="pr_wrf",
                color_continuous_scale="jet",
                hover_name="wmos",
                center={"lat": 55.0, "lon": -110.0},
                hover_data=[f"maes"],
                mapbox_style="carto-positron",
                zoom=1.8,
                title=stats_text,
            )
            fig.update_layout(margin=dict(l=0, r=100, t=30, b=10))
            fig.show()
            print(
                "======================================================================="
            )

    return


##########################################################################
##########################################################################
fwi_list = ["ffmc", "dmc", "dc", "bui", "isi", "fwi"]
plotstats(fwi_list)


##########################################################################
##########################################################################
# met_list = ["temp", "td", "rh", "ws", "wdir", "precip"]
# met_list = ["precip"]

# plotstats(met_list)
