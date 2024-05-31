#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import string
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from wrf import ll_to_xy, xy_to_ll

from context import data_dir


#################### INPUTS ####################
## define date range
date_range = pd.date_range("2020-01-01", "2024-01-01")
# date_range = pd.date_range("2023-01-01", "2023-01-01")
domain = "d03"

################## END INPUTS ##################


# ds = xr.open_zarr(
#     str(data_dir) + "/intercomp/" + f"intercomp-{domain}-20230604.zarr"
# ).load()


### Open nested grid json
with open(str(data_dir) + "/json/nested-index.json") as f:
    nested_index = json.load(f)

### Open color map json
with open(str(data_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)

## Get All Stations CSV
url = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_allstn2019.csv"
stations_df_og = pd.read_csv(url, sep=",")
stations_df_og = stations_df_og.drop_duplicates(subset="wmo", keep="last")
stations_df = stations_df_og.drop(
    columns=["tmm", "ua", "the_geom", "h_bul", "s_bul", "hly", "syn"]
)


wrf_filein = "/wrf/"
wrf_file_dir = str(data_dir) + wrf_filein
wrf_file_dir = sorted(Path(wrf_file_dir).glob(f"wrfout_{domain}_*"))
wrf_file = Dataset(wrf_file_dir[0], "r")
shape = np.shape(xr.open_dataset(wrf_file_dir[0]).XLAT[0, :, :])


## get index to remove boundary conditions
n, y1, y2, x1, x2 = (
    nested_index["n"],
    nested_index["y1_" + domain],
    nested_index["y2_" + domain],
    nested_index["x1_" + domain],
    nested_index["x2_" + domain],
)

### Drop stations out sie of model domain
xy_np = ll_to_xy(wrf_file, stations_df["lat"], stations_df["lon"])
stations_df["x"] = xy_np[0]
stations_df["y"] = xy_np[1]
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["x"] > (shape[1] - x2 - 1))]
)
stations_df = stations_df.drop(
    stations_df.index[np.where(stations_df["y"] > (shape[0] - y2 - 1))]
)
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["x"] < x1 - 1)])
stations_df = stations_df.drop(stations_df.index[np.where(stations_df["y"] < y1 - 1)])


filein_obs = "/bluesky/fireweather/fwf/data/obs/cwfis_canusfwi2020s.csv"
filein_obs = "/bluesky/fireweather/fwf/data/obs/cwfis_fwi2020sopEC.csv"
# filein_obs = "https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/cwfis_canusfwi2020s.csv"
obs_df_master = pd.read_csv(filein_obs, sep=",", skiprows=0)

## define list of varibles wanted
var_list = [
    "wmo",
    "time",
    "temp",
    "rh",
    "td",
    "ws",
    "wdir",
    "precip",
    "ffmc",
    "dmc",
    "dc",
    "isi",
    "bui",
    "fwi",
]
## remove wmo from list for building datasets
final_var_list = var_list[2:]

## open the alphabet
# alpha = list(string.ascii_uppercase)

## create empyty list of datasets
ds_list = []
## loop dates of interest
for date in date_range:
    ## convert datetime to needed formate for file dirs
    forecast_date = date.strftime("%Y%m%d00")
    obs_date = pd.to_datetime(str(date - np.timedelta64(1, "D"))).strftime("%Y%m%d")
    ## set contion to try and get data, fill with -99 if file dir doesnt excist
    # print(obs_date)
    try:
        ## create dictionary and fill with empy arry for each varible
        obs_dict = {}
        for var in var_list:
            obs_dict.update({var: []})

        ## loop each time zone of weather station datate
        for i in range(4, 10):
            filein = f"/bluesky/archive/fireweather/forecasts/{forecast_date}/data/wx-zone-{i}-{obs_date}.json"
            ## open the wxstation json data
            with open(filein, "r") as j:
                contents = json.loads(j.read())
                ## loop all the varibles with special condtion for time and wmo
                ## data will be appeded to our dictionary
                for var in var_list:
                    if var == "wmo":
                        obs_dict[var].append(np.array(json.loads(contents[var])))
                    # elif var == 'name':
                    #     name = str(contents[var]).replace("'",'"') #.replace('"',"'")
                    #     for a in alpha:
                    #         for b in alpha:
                    #             name = name.replace(f'{a}"{b}','S')
                    #             # name = name.replace(f'{a}"L','S')
                    #             # name = name.replace(f'{a}"A','S')
                    #             # name = name.replace(f'{a}"E','S')
                    #     name = name.replace(f'""','"')
                    # obs_dict[var].append(np.array(json.loads(name)))
                    elif var == "time":
                        obs_dict[var].append(np.array(contents["time_obs"])[-1])
                    else:
                        obs_dict[var].append(
                            np.array(json.loads(contents[var + "_obs"]))[-1, :]
                        )

        ## flatten each varible list
        for var in obs_dict:
            if var == "time":
                pass
            else:
                obs_dict[var] = [item for sublist in obs_dict[var] for item in sublist]
            # print(f"{var}: {len(obs_dict[var])}")

        ## get station ids and day of observation
        wmo_obs = np.array(obs_dict["wmo"])
        day = np.array(obs_dict["time"][0][:-3], dtype="datetime64[D]")

        ## create empty list of dataarrays
        da_list = []
        ## loop and make dataarrays for each varible
        for var in final_var_list:
            var_array = np.array(obs_dict[var], dtype="float32")
            x = np.stack((var_array, var_array))
            da_var = xr.DataArray(
                x,
                name=f"{var}",
                coords={
                    "wmo_obs": wmo_obs,
                    "time": [day, day],
                },
                dims=("time", "wmo_obs"),
            )

            da_list.append(da_var)
        ## merge the dataarrays to a dataset
        ds_i = xr.merge(da_list)
        ds_i = ds_i.isel(time=0)
        ## reindex dataset to match orginal formate
        ds_i = ds_i.sel(wmo_obs=ds.wmo)
        ds_i = ds_i.drop_vars("wmo_obs")
        if len(np.unique(ds_i.temp.values)) < 2:
            # print('bad internal data')
            ds_i = ds_i["bad_var"]
        else:
            pass
        ds_list.append(ds_i)
        print(f"Found internal data on obs_date {obs_date}!")


    except:
        print(f"No internal data on obs_date {obs_date} getting data from NRCAN")
        try:
            ## Get Daily observations CSV
            url2 = f"https://cwfis.cfs.nrcan.gc.ca/downloads/fwi_obs/current/cwfis_fwi_{obs_date}.csv"
            headers = list(pd.read_csv(url2, nrows=0))
            obs_df = pd.read_csv(url2, sep=",", names=headers)
            obs_df = obs_df.drop_duplicates()
            obs_df = obs_df.drop(obs_df.index[[0]])
            del obs_df["NAME"]
            obs_df["wmo"] = obs_df["WMO"].astype(str).astype(int)
            del obs_df["WMO"]
            obs_df.columns = obs_df.columns.str.lower()
        except:
            print("using master")
            filein_obs = "/bluesky/fireweather/fwf/data/obs/cwfis_canusfwi2020s.csv.csv"
            # obs_df = pd.read_csv(filein_obs, sep=",", skiprows=0)
            # index obs dateframe to get date of interest
            obs_df = obs_df_master[
                obs_df_master["rep_date"] == date.strftime("%Y-%m-%d 12:00:00")
            ]

        # merge with stations data information
        wmo_df = stations_df
        final_df = wmo_df.merge(obs_df, on="wmo", how="left")
        final_df = final_df.replace("NULL", np.nan)
        final_df = final_df.replace(" NULL", np.nan)
        final_df = final_df.replace("  NULL", np.nan)
        final_df = final_df.drop_duplicates(subset=["wmo"], keep="last")
        ## convert to float 32 for smaller storage
        final_df = final_df.astype(
            {
                "temp": "float32",
                "td": "float32",
                "rh": "float32",
                "ws": "float32",
                "wdir": "float32",
                "precip": "float32",
                "ffmc": "float32",
                "dmc": "float32",
                "dc": "float32",
                "bui": "float32",
                "isi": "float32",
                "fwi": "float32",
                "dsr": "float32",
            }
        )

        wmos = final_df["wmo"].values
        _, index, count = np.unique(wmos, return_index=True, return_counts=True)
        ids = final_df["id"].values.astype(str)
        names = final_df["name"].values.astype(str)
        provs = final_df["prov"].values.astype(str)
        lons = final_df["lon"].values.astype("float32")
        lats = final_df["lat"].values.astype("float32")
        elevs = final_df["elev"].values.astype("float32")
        tz_correct = final_df["tz_correct"].values.astype(int)

        day = np.array(
            pd.to_datetime(str(date - np.timedelta64(1, "D"))).strftime("%Y-%m-%d"),
            dtype="datetime64[D]",
        )

        xr_list = []
        for var in final_var_list:
            var = var.lower()
            var_array = np.array(final_df[var], dtype="float32")
            x = np.stack((final_df[var].values, final_df[var].values))
            xr_var = xr.DataArray(
                x,
                name=f"{var}",
                coords={
                    "wmo": wmos,
                    "time": [day, day],
                    "lats": ("wmo", lats),
                    "lons": ("wmo", lons),
                    "elev": ("wmo", elevs),
                    "name": ("wmo", names),
                    "prov": ("wmo", provs),
                    "id": ("wmo", ids),
                    "tz_correct": ("wmo", tz_correct),
                },
                dims=("time", "wmo"),
            )

            xr_list.append(xr_var)

        ds_i = xr.merge(xr_list)
        ds_i = ds_i.isel(time=0)
        ds_list.append(ds_i)

        # unique, counts = np.unique(np.isnan(ds_i.ffmc.values), return_counts = True)

        # intercomp_today_ds.attrs["TITLE"] = str(
        #     "wrfout/fwf/era5 model versus wmo weather station observations"
        # ).upper()
        # for var in var_list:
        #     name_lower = cmaps[var]["name"].lower()
        #     attrs = wrf05_ds[var].attrs
        #     intercomp_today_ds[name_lower].attrs["description"] = attrs
        #     intercomp_today_ds[name_lower].attrs["description"] = (
        #         "OBSERVED " + attrs["description"]
        #     )


###############################################################################################
## combine the datasets for each observation day to make a continuous time series dataset
final_ds = xr.combine_nested(ds_list, "time")

## change -99 to nan values to be consistant
for var in final_var_list:
    final_ds[var] = xr.where(final_ds[var] < -90.0, np.nan, final_ds[var])
# unique, counts = np.unique(np.isnan(final_ds['temp'].values), return_counts = True )

file_date_start = pd.to_datetime(str(date_range[0] - np.timedelta64(1, "D"))).strftime(
    "%Y%m%d"
)
file_date_end = pd.to_datetime(str(date_range[-1] - np.timedelta64(1, "D"))).strftime(
    "%Y%m%d"
)
# write combined dataset as nc file
final_ds.to_netcdf(
    str(data_dir)
    + "/obs/"
    + f"observations-{domain}-{file_date_start}-{file_date_end}.nc",
    mode="w",
)
