#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import salem
import json
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

import matplotlib.pyplot as plt
import cartopy.crs as crs
import cartopy.feature as cfeature
import matplotlib.colors
import zarr
import dask

from datetime import datetime, timedelta

from context import data_dir, root_dir
from utils.frp import build_tree
from utils.geoutils import get_pyproj_loc
from utils.open import read_dataset

from utils.diagnostic import solve_RH

from dask.distributed import LocalCluster, Client

plt.rcParams["text.usetex"] = False
runTime = datetime.now()


date_range = pd.date_range("2021-01-07", "2023-11-01")
# date_range = pd.date_range("2023-10-01", "2023-10-05")
# date_range_wrf = pd.date_range(date_range[0]- pd.Timedelta(days=1), date_range[-1])
fwf_grid = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")


### On workstation
### http://137.82.23.185:8787/status
### On personal
###  http://10.0.0.88:8787/status
cluster = LocalCluster(
    n_workers=2,
    #    threads_per_worker=,
    memory_limit="30GB",
    processes=False,
)
client = Client(cluster)
print(client)


config = dict(
    model="ecmwf",
    domain="era5-land",
)
# def open_era5(doi):
#    ds = xr.open_dataset(f"/Volumes/WFRT-Ext25/ecmwf/era5-land/{doi.strftime('%Y%m')}/era5-land-{doi.strftime('%Y%m%d%H')}.nc")[['u10', 'v10']].chunk('auto')
#    wsp = dask.array.sqrt(ds["u10"] ** 2 + ds["v10"] ** 2)
#    ds["W"] = wsp
#    ds = ds["W"].to_dataset()
#    return ds

# def open_era5(doi):
#    ds = xr.open_dataset(f"/Volumes/WFRT-Ext25/ecmwf/era5-land/{doi.strftime('%Y%m')}/era5-land-{doi.strftime('%Y%m%d%H')}.nc")[['t2m', 'd2m']].chunk('auto')
#    ds["T"] = ds["t2m"] - 273.15
#    ds["TD"] = ds["d2m"] - 273.15
#    ds = ds[["T", "TD"]]
#    ds  = solve_RH(ds)['H'].to_dataset()
#    return ds


def open_era5(doi):
    file_yesterday = f"/Volumes/WFRT-Ext25/ecmwf/era5-land/{(doi + pd.Timedelta(days=-1)).strftime('%Y%m')}/era5-land-{(doi + pd.Timedelta(days=-1)).strftime('%Y%m%d00.nc')}"
    file = f"/Volumes/WFRT-Ext25/ecmwf/era5-land/{(doi).strftime('%Y%m')}/era5-land-{(doi).strftime('%Y%m%d00.nc')}"

    ds_yesterday = xr.open_dataset(file_yesterday).isel(time=23).chunk("auto")
    try:
        ds_yesterday = ds_yesterday.isel(expver=0)
    except:
        pass
    ds = xr.open_dataset(file).chunk("auto")
    try:
        ds = ds.isel(expver=0)
    except:
        pass
    ds["tp"][0] = ds["tp"][0] - ds_yesterday["tp"].values
    r_oi = ds["tp"]

    r_o_plus1 = dask.array.dstack((dask.array.zeros_like(ds["tp"][0]).T, r_oi.T)).T
    r_hourly_list = []
    for i in range(len(ds.time)):
        r_hour = r_oi[i] - r_o_plus1[i]
        r_hourly_list.append(r_hour)
    r_hourly = dask.array.stack(r_hourly_list)
    r_hourly = (
        xr.DataArray(
            r_hourly, name="r_o_hourly", dims=("time", "latitude", "longitude")
        )
        * 1000
    )
    ds["r_o_hourly"] = r_hourly
    return ds["r_o_hourly"].to_dataset()


# def open_era5_fwi(doi):
#    return xr.open_dataset(f"/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/fwf-hourly-era5-land-{doi.strftime('%Y%m%d%H')}.nc")['S'].drop(['XLAT', 'XLONG']).to_dataset().chunk('auto')

# def open_fwf(doi):
#    return xr.open_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/d02/04/fwf-hourly-d02-{doi.strftime('%Y%m%d06')}.nc")['T'].drop(['XLAT', 'XLONG']).isel(time=slice(0,24)).to_dataset().chunk('auto')


def open_fwf(doi):
    ds = (
        xr.open_dataset(
            f"/Volumes/WFRT-Ext24/fwf-data/wrf/d02/04/fwf-hourly-d02-{doi.strftime('%Y%m%d06')}.nc"
        )["r_o"]
        .drop(["XLAT", "XLONG"])
        .isel(time=slice(0, 24))
        .to_dataset()
        .chunk("auto")
    )
    r_oi = ds.r_o
    zero_full = dask.array.zeros_like(ds.r_o[0, :, :])
    r_o_plus1 = dask.array.dstack((zero_full.T, r_oi.T)).T
    r_hourly_list = []
    for i in range(len(ds.Time)):
        r_hour = ds.r_o[i] - r_o_plus1[i]
        r_hourly_list.append(r_hour)
    r_hourly = dask.array.stack(r_hourly_list)
    r_hourly = xr.DataArray(
        r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
    )
    ds["r_o_hourly"] = r_hourly
    return ds["r_o_hourly"].to_dataset().chunk("auto")


def hour_stats(x):
    return x.groupby("time.hour").mean(dim="time")


combineTime = datetime.now()
ds = xr.combine_nested([open_era5(doi) for doi in date_range], concat_dim="time")
try:
    ds["time"] = ds["Time"]
except:
    pass
print("Combine time:  ", datetime.now() - combineTime)
# ds = ds[['T', 'H', 'W', 'r_o']]

groupTime = datetime.now()
group_ds = ds.groupby("time.month").apply(hour_stats).chunk("auto")
# group_ds.attrs =  group_ds.attrs
# for var in list(group_ds):
#     group_ds[var].attrs =  fwf_grid.attrs
print("Group time:  ", datetime.now() - groupTime)

writeTime = datetime.now()
# compressor = zarr.Blosc(cname="zstd", clevel=3, shuffle=2)
group_ds.to_zarr(
    "/Volumes/WFRT-Ext22/ecmwf/era5-land/era5-tp-2021-2023.zarr",
    mode="w",
)
#  encoding={x: {"compressor": compressor} for x in group_ds})
print("Write time:  ", datetime.now() - writeTime)
print("Run time:  ", datetime.now() - runTime)

# def open_fwf(doi):
#    return xr.open_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/d02/01/fwf-hourly-d02-{doi.strftime('%Y%m%d06')}.nc").isel(time=slice(0,24)).chunk('auto')
# def open_wrf(doi):
#    return xr.open_dataset(f"/Volumes/WFRT-Ext24/fwf-data/wrf/d02/04/fwf-hourly-d02-{doi.strftime('%Y%m%d06')}.nc").isel(time=slice(0,24)).chunk('auto')
# fwf_ds = xr.combine_nested([open_fwf(doi) for doi in date_range_wrf], concat_dim='time')
# # wrf_ds = xr.combine_nested([open_wrf(doi) for doi in date_range_wrf], concat_dim='time')
# fwf_ds['time'] = fwf_ds['Time']
# fwf_grid = salem.open_xr_dataset(str(data_dir) + "/static/static-vars-wrf-d02.nc")

# # for var in list(fwf_ds):
# #   wrf_ds[var] = fwf_ds[var]
# fwf_ds = fwf_ds.isel(time = slice(24-6, -6))
# fwf_ds = fwf_ds[list(ds)]
# fwf_ds.attrs =  fwf_grid.attrs
# for var in list(ds):
#     fwf_ds[var].attrs = fwf_grid.attrs

# dsT = fwf_ds.salem.transform(ds)


# diff_ds = fwf_ds - dsT

# diff_ds = diff_ds.chunk('auto')

# def meam_hour(x):
#    return x.groupby('time.hour').mean(dim = 'time')
# mean_diff_ds = diff_ds.groupby('time.month').apply(meam_hour)

# mean_diff_ds.attrs = fwf_grid.attrs
# for var in list(mean_diff_ds):
#     mean_diff_ds[var].attrs =  fwf_grid.attrs


# # mean_diff_ds['S'].isel(month = 0, hour = 12).salem.quick_map(vmin = -10, vmax = 10, cmap ='coolwarm', extend='both', oceans = True, prov = True, states =True)
# # mean_diff_ds['T'].salem.quick_map(vmin = -4, vmax = 4, cmap ='coolwarm', extend='both', oceans = True, prov = True, states =True)
# # mean_diff_ds['W'].salem.quick_map(vmin = -20, vmax = 20, cmap ='coolwarm', extend='both', oceans = True, prov = True, states =True)
# # mean_diff_ds['r_o'].salem.quick_map(vmin = -2, vmax = 2, cmap ='coolwarm', extend='both', oceans = True, prov = True, states =True)
# # mean_diff_ds['H'].salem.quick_map(vmin = -20, vmax = 20, cmap ='coolwarm', extend='both', oceans = True, prov = True, states =True)
