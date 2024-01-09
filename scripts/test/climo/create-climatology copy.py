#!/Users/crodell/miniconda3/envs/fwx/bin/python
import json
import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime

from utils.compressor import compressor

from context import root_dir

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file

save_dir = Path(str(root_dir) + "/data/ecmwf/era5-land/")
# save_dir.mkdir(parents=True, exist_ok=True)
var = "S"
# var_list = ['S', 'F', 'P', 'D', 'R', 'U', 'DSR', "T", "W", "H", 'r_o']
# var_list = ['S', 'R', 'F']
fwf = True
method = "hourly"
start = "1991-01-01"
stop = "2020-12-31"

## open fwf attributes
with open(str(root_dir) + f"/json/fwf-attrs.json", "r") as fp:
    attrs = json.load(fp)

## open additional fwf attributes
with open(str(root_dir) + f"/json/colormaps-dev.json", "r") as fp:
    attrs_plus = json.load(fp)

# mask = xr.open_dataset("/Volumes/WFRT-Ext25/ecmwf/era5-land/202201/era5-land-2022010100.nc").isel(time =0).notnull().rename({'t2m': 'S'})['S'].values


def get_daily_files(fwf, method, start, stop):
    if fwf == True:
        ## get all fwf data derived from era5-land
        pathlist = sorted(
            Path("/Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04/").glob(
                f"fwf-{method}*"
            )
        )
    else:
        root = Path("/Volumes/WFRT-Ext25/ecmwf/era5-land/")

        # Get all monthly folders in the root path
        monthly_folders = [folder for folder in root.glob("*") if folder.is_dir()]

        # Iterate through each monthly folder
        daily_files = []
        for monthly_folder in monthly_folders:
            # Get all daily files in the current monthly folder
            daily_files.extend(
                list(monthly_folder.glob("**/*.nc"))
            )  # Change the pattern accordingly

        pathlist = sorted(daily_files)

    date_range = pd.date_range(str(pathlist[0])[-13:-5], str(pathlist[-1])[-13:-5])
    pathlist = pathlist[
        int(np.where(date_range == start)[0][0]) : int(
            np.where(date_range == stop)[0][0]
        )
        + 1
    ]

    return pathlist


def hour_qunt(x):
    """
    function groups time to hourly and solves hourly mean

    """
    x = x.chunk({"time": -1})
    return x.groupby("time.hour").quantile(
        [0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0], dim="time"
    )


def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    return ds


pathlist = get_daily_files(fwf, method, start, stop)

# ds = salem.open_xr_dataset(str(pathlist[0]))['S']
# (24, 711, 1551)
# (24, 711/3, 1551/3) = (24, 237, 517)
# (24, 711/9, 1551/11) = (24, dj, di)
# file_names = []
# di, dj = 141, 79
# ds_final = ds.salem.transform(ds.isel(south_north = slice(0*dj, 1*dj), west_east = slice(0*di, 1*di)).isel(time=0))
# for i in range(0,11):
#     ii = i +1
#     for j in range(0,9):
#         jj = j+1
#         ds_slice = ds.isel(south_north = slice(j*dj, jj*dj), west_east = slice(i*di, ii*di))
#         ds_final[j*dj: jj*dj, i*di: ii*di] = ds_slice.isel(time=0)

#         file_names.append(str(save_dir) + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.nc")
# ds_final.salem.quick_map()


def open_ds(path, i, j):
    ii = i + 1
    jj = j + 1
    ds = xr.open_dataset(path)[var].isel(
        south_north=slice(j * dj, jj * dj), west_east=slice(i * di, ii * di)
    )
    ds.drop(["XLAT", "XLONG"])
    return ds.chunk({"time": 12})


def open_ds(path):
    return xr.open_dataset(path, chunks="auto")[var]


# for var in var_list:
## open =, chunk and combine into single dask chunk dataset
pathlist = pathlist[: 365 * 2]
di, dj = 141, 79
for i in range(0, 11):
    for j in range(0, 9):

        file_names.append(
            str(save_dir)
            + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}-i{i}j{j}.nc"
        )
open = datetime.now()
ds = xr.concat(
    [open_ds(path) for path in pathlist], dim="time"
).to_dataset()  # .where(mask)
# ds = xr.concat([xr.open_dataset(path, chunks="auto").sel(west_east = slice(-112, -110), south_north = slice(55,53))[var] for path in pathlist],dim = 'time').to_dataset()
print("Opening Time: ", datetime.now() - open)

# try:
#     ds['time'] = ds['Time']
# except:
#     pass
# rechunk_time = datetime.now()
# ds = rechunk(ds)
# print("rechunk Time: ", datetime.now() - rechunk_time)

# ## NOTE remove this, only using it to play with climo approach
# # ds1 = ds.groupby('time.dayofyear').apply(hour_qunt)
# # ds2 = ds.groupby('time.month').apply(hour_qunt)
# # ds1.isel( dayofyear = 220, hour = 1, quantile = 4)['S'].plot(vmax = 30)
# # ds2.isel( month = 7, hour = 1, quantile = 4)['S'].plot(vmax = 30)

# if method == 'daily':
#     ## group data into dayofyear and solve for quantiles for each day over the 30 years
#     group = datetime.now()
#     ds = ds.groupby("time.dayofyear").quantile([0, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 1.0], dim='time')
#     print("Grouping Time: ", datetime.now() - group)
# elif method == 'hourly':
#     ## group data into hours for each dayofyear adn solve for quantiles for each hour on each day over the 30 years
#     group = datetime.now()
#     ds = ds.groupby('time.dayofyear').apply(hour_qunt)
#     print("Grouping Time: ", datetime.now() - group)
# else:
#     raise ValueError(f'Not a valid method: {method}')

# # Add some dataset attributes
# ds.attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"
# ds.attrs[
#     "description"
# ] = f"30 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"

# # ds[var].attrs = attrs[var]
# # ds[var].attrs['abbr'] = attrs_plus[var]['name']
# ds[var].attrs["pyproj_srs"] = "+proj=longlat +datum=WGS84 +no_defs"


# rechunk_time = datetime.now()
# ds = rechunk(ds)
# print("rechunk Time: ", datetime.now() - rechunk_time)

# ## invoke compute to take dask to numpy (ie lazy objects to numerics)
# computeTime = datetime.now()
# ds = ds.compute()
# print("Compute Time: ", datetime.now() - computeTime)

# # write ds to netcdf
# # ds, encoding = compressor(ds)
# write = datetime.now()
# ds.to_netcdf(
#     str(save_dir) + f"/{attrs_plus[var]['name']}-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}.nc",
#     mode="w",
#     # encoding = encoding
# )
# print("Write Time: ", datetime.now() - write)


# # def hour_mean(x):
# #     """
# #     function groups time to hourly and solves hourly mean

# #     """
# #     return x.groupby("time.hour").mean("time")


# # def day_max(x):
# #     """
# #     function groups time to daily and take daily max

# #     """
# #     return x.groupby('time.day').max('time')


# # # ## group data into months and days solve for mean daily max over the month for the full the 30 years
# # group = datetime.now()
# # ds = ds.groupby("time.month").apply(day_max).mean("day")
# # print("Grouping Time: ", datetime.now() - group)

# # # ## group data into months and solve for monthly average over the 30 years
# # # group = datetime.now()
# # # ds = ds.groupby("time.month").mean("time")
# # # print("Grouping Time: ", datetime.now() - group)

# # # loadTime = datetime.now()
# # # ds = ds.load()
# # # print("Loading Time: ", datetime.now() - loadTime)


# # ## group data into month day hour and solve the hourly means
# # # group = datetime.now()
# # # ds = ds.groupby("time.month").apply(hour_mean)
# # # ds = xr.apply_ufunc(hour_mean, ds, dask='parallelized',output_dtypes=[float], vectorize=True,)
# # # print("Grouping Time: ", datetime.now() - group)

# # # open = datetime.now()
# # # ds = xr.concat([xr.open_dataset(path, chunks="auto") for path in pathlist],dim = 'time')
# # # print("Opening Time: ", datetime.now() - open)


# # # rechunk_time = datetime.now()
# # # ds = rechunk(ds)
# # # print("rechunk Time: ", datetime.now() - rechunk_time)


# # # def hour_mean(x):
# # #     """
# # #     function groups time to hourly and solves hourly mean

# # #     """
# # #     return x.groupby('time.hour').mean('time')

# # # def day_mean(x):
# # #     """
# # #     function groups time to daily and feeds into hourly_mean

# # #     """
# # #     x = x.groupby('time.day').mean('time') #.apply(hour_mean)
# # #     # rechunk_time = datetime.now()
# # #     # x = rechunk(x)
# # #     # print("Rechunk Time: ", datetime.now() - rechunk_time)
# # #     return x
