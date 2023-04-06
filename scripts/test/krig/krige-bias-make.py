#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import salem
import json
import gc

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd

from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging

from pathlib import Path
from datetime import datetime
from context import data_dir, root_dir

# import time
# time.sleep(60*70)

startTime = datetime.now()
print(f"Start Time: {startTime}")

##################################################################
##################### Define Inputs   ###########################
domain = "d02"
var_list = ["T", "TD"]
krig_type = "uk"  ## uk or ok
var_range = [-6, 6]
date_range = pd.date_range("2021-04-04", "2022-10-31")
# date_range = pd.date_range("2022-09-17", "2022-10-31")
# date_range = pd.date_range("2021-01-01", "2021-01-01")
# date_range = pd.date_range("2021-06-23", "2021-06-23")


trail_name = "WRF04"

nlags = 23
variogram_model = "spherical"

save_dir = Path(f"/Volumes/WFRT-Ext24/fwf-data/wrf/{domain}/krig-bias-{krig_type}/")
save_dir.mkdir(parents=True, exist_ok=True)
##TODO make uk 2022-02-17
##################################################################
##################### Open Data Files  ###########################

grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/{domain}-grid.nc")

static_ds = xr.open_dataset((str(data_dir) + f"/static/static-vars-wrf-{domain}.nc"))
static_ds["west_east"], static_ds["south_north"] = (
    grid_ds["west_east"],
    grid_ds["south_north"],
)
elev_array = static_ds.HGT.values

ds = xr.open_dataset(
    str(data_dir) + f"/intercomp/{domain}/{trail_name}/20210101-20221031.nc",
    # chunks = 'auto'
)
for cord in ["elev", "name", "prov", "id"]:
    ds[cord] = ds[cord].astype(str)
ds["elev"] = ds["elev"].astype(float)
ds["elev"] = xr.where(ds["elev"] < 0, 0, ds["elev"])


ds = ds.chunk("auto")

## open model config file with variable names and attributes
with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Open Data Attributes for writing
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    var_dict = json.load(fp)

##################################################################
#####################  Krig Data Range ###########################

ds_list = []
for date in date_range:
    ## make copy of grid_ds to save kriged felids
    krig_ds = grid_ds.copy()
    for var in var_list:
        var_lower = cmaps[var]["name"].lower()

        ## make copy of original dataset and drop irrelevant variables
        ds_tm = ds.copy()[[var_lower, f"{var_lower}_wrf04"]]

        ## slice dataset into seven day segments
        valid_data = date.strftime("%Y-%m-%d")
        if valid_data == "2022-02-17":
            past_date = pd.to_datetime(str(date - np.timedelta64(7, "D"))).strftime(
                "%Y-%m-%d"
            )
        else:
            past_date = pd.to_datetime(str(date - np.timedelta64(6, "D"))).strftime(
                "%Y-%m-%d"
            )
        ds_tm[f"{var_lower}_bias"] = (
            (ds_tm[f"{var_lower}_wrf04"] - ds_tm[var_lower])
            .sel(time=slice(past_date, valid_data))
            .mean(dim="time")
        )

        ## drop all wxstation that are nulled values
        var_bias_tm = ds_tm[f"{var_lower}_bias"].dropna(dim="wmo")

        ## convert dataset to dataframe, ensure no null values exist and solve for mean bias
        var_bias_tm_df = var_bias_tm.to_dataframe()
        var_bias_tm_df = var_bias_tm_df[~np.isnan(var_bias_tm_df[f"{var_lower}_bias"])]
        var_bias_tm_df = var_bias_tm_df[
            np.abs(
                var_bias_tm_df[f"{var_lower}_bias"]
                - var_bias_tm_df[f"{var_lower}_bias"].mean()
            )
            <= (2 * var_bias_tm_df[f"{var_lower}_bias"].std())
        ]
        var_bias_tm_df = var_bias_tm_df.reset_index()

        ## reproject lat long of wxstation to wrf/fwf model projection (polar stereographic)
        obs_gdf = gpd.GeoDataFrame(
            var_bias_tm_df,
            crs="EPSG:4326",
            geometry=gpd.points_from_xy(var_bias_tm_df["lons"], var_bias_tm_df["lats"]),
        ).to_crs(
            "+proj=stere +lat_0=90 +lat_ts=53.25 +lon_0=-110 +x_0=0 +y_0=0 +R=6370000 +units=m +no_defs"
        )
        obs_gdf["Easting"], obs_gdf["Northing"] = obs_gdf.geometry.x, obs_gdf.geometry.y

        gridx = krig_ds.west_east.values
        gridy = krig_ds.south_north.values

        if krig_type == "ok":
            # krig = None
            # while krig is None:
            #     nlags += 1
            #     print("nlags ", nlags)
            try:
                ok_time = datetime.now()
                pseudo_inv = False
                krig = OrdinaryKriging(
                    x=obs_gdf["Easting"],
                    y=obs_gdf["Northing"],
                    z=obs_gdf[f"{var_lower}_bias"],
                    variogram_model=variogram_model,
                    nlags=nlags,
                    pseudo_inv=pseudo_inv,
                )
                ok_time = datetime.now()
                z, ss = krig.execute("grid", gridx, gridy)
                print(f"OK execution time {datetime.now() - ok_time}")
            except:
                ok_time = datetime.now()
                pseudo_inv = True
                krig = OrdinaryKriging(
                    x=obs_gdf["Easting"],
                    y=obs_gdf["Northing"],
                    z=obs_gdf[f"{var_lower}_bias"],
                    variogram_model=variogram_model,
                    nlags=nlags,
                    pseudo_inv=pseudo_inv,
                )
                print(f"OK build time {datetime.now() - ok_time}")
                ok_time = datetime.now()
                z, ss = krig.execute("grid", gridx, gridy)
                print(f"OK execution time {datetime.now() - ok_time}")
        elif krig_type == "uk":
            uk_time = datetime.now()
            y = xr.DataArray(
                np.array(obs_gdf["Northing"]),
                dims="ids",
                coords=dict(ids=obs_gdf.id.values),
            )
            x = xr.DataArray(
                np.array(obs_gdf["Easting"]),
                dims="ids",
                coords=dict(ids=obs_gdf.id.values),
            )

            var_points = static_ds["HGT"].interp(
                west_east=x, south_north=y, method="nearest"
            )
            # print(var_points)
            if len(obs_gdf.index) == len(var_points.values):
                var_points = var_points.values
            else:
                raise ValueError("Lengths dont match")
            try:
                krig = UniversalKriging(
                    x=obs_gdf["Easting"],
                    y=obs_gdf["Northing"],
                    z=obs_gdf[f"{var_lower}_bias"],
                    drift_terms=["specified"],
                    variogram_model=variogram_model,
                    specified_drift=[var_points],
                    nlags=nlags,
                    # pseudo_inv=True,
                )
                print(f"UK build time {datetime.now() - uk_time}")
                uk_time = datetime.now()
                z, ss = krig.execute(
                    "grid", gridx, gridy, specified_drift_arrays=[elev_array]
                )
                print(f"UK execution time {datetime.now() - uk_time}")
            except:
                krig = UniversalKriging(
                    x=obs_gdf["Easting"],
                    y=obs_gdf["Northing"],
                    z=obs_gdf[f"{var_lower}_bias"],
                    drift_terms=["specified"],
                    variogram_model=variogram_model,
                    specified_drift=[var_points],
                    nlags=26,
                    pseudo_inv=True,
                )
                print(f"UK build time {datetime.now() - uk_time}")
                uk_time = datetime.now()
                z, ss = krig.execute(
                    "grid", gridx, gridy, specified_drift_arrays=[elev_array]
                )
                print(f"UK execution time {datetime.now() - uk_time}")
        else:
            raise ValueError("Invalid Kriging Method")

        krig_ds[f"{var}_bias"] = (("south_north", "west_east"), z)
        krig_ds[f"{var}_kv"] = (("south_north", "west_east"), ss)

        print(str(len(var_bias_tm.wmo)))
        var_dict[f"{var}_bias"]["wmo_count"] = str(len(var_bias_tm.wmo))
        krig_ds[f"{var}_bias"].attrs = var_dict[f"{var}_bias"]
        krig_ds[f"{var}_kv"].attrs = var_dict[f"{var}_kv"]
        ## clear garbage to keep memory free
        del ds_tm
        del var_bias_tm_df
        del obs_gdf
        del krig
        del z
        del ss
        gc.collect()

    write_time = datetime.now()
    krig_ds = krig_ds.assign_coords(time=np.array(date).astype("datetime64[D]"))
    # print(krig_ds[f"T_bias"].values)
    krig_ds.to_netcdf(
        str(save_dir) + f'/fwf-krig-{domain}-{date.strftime("%Y%m%d")}.nc'
    )
    print(f"Write time {date.strftime('%Y%m%d')}:  {datetime.now() - write_time}")
    ## clear garbage to keep memory free
    del krig_ds
    gc.collect()


print(f"Total Run Time {datetime.now() - startTime}")