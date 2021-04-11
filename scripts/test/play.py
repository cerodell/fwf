import context
import json
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from utils.read_wrfout import readwrf

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta


domain = "d02"
# date = pd.Timestamp("today")
forecast_date = pd.Timestamp(2021, 4, 9).strftime("%Y%m%d06")
# forecast_date = pd.Timestamp("today").strftime("%Y%m%d00")
filein = str(wrf_dir) + f"/{forecast_date}/"

hourly_ds = xr.open_zarr(
    str(fwf_zarr_dir) + str("/fwf-hourly-") + domain + str(f"-{forecast_date}.zarr")
)

file_date = str(np.array(hourly_ds.Time[0], dtype="datetime64[h]"))
file_date = datetime.strptime(str(file_date), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

# # ## Write and save DataArray (.zarr) file
make_dir = Path(
    str(fwf_zarr_dir)
    # + str(f"/{file_date[:-2]}00/fwf-hourly-")
    + str("/fwf-hourly-")
    + domain
    + str(f"-{file_date}-test.zarr")
)
# make_dir.mkdir(parents=True, exist_ok=True)
def rechunk(ds):
    ds = ds.chunk(chunks="auto")
    ds = ds.unify_chunks()
    for var in list(ds):
        ds[var].encoding = {}
    return ds


# comp = dict(zlib=True, complevel=9)
# encoding = {var: comp for var in hourly_ds.data_vars}
hourly_ds = rechunk(hourly_ds)
startTime = datetime.now()
hourly_ds.to_zarr(make_dir, mode="w")
print("Writie Time: ", datetime.now() - startTime)
print(f"wrote working {make_dir}")


#  tar -czvf fwf-hourly-d02-2021040906-test.tgz fwf-hourly-d02-2021040906-test.zarr
# startTime = datetime.now()

# pathlist = sorted(Path(filein).glob(f"wrfout_{domain}_*00"))
# if domain == "d02":
#     pathlist = pathlist[6:61]
# else:
#     pathlist = pathlist[6:]
# wrf_file = Dataset(str(pathlist[0]), "r")


# dict_file = {}
# nc_attrs = wrf_file.ncattrs()
# for nc_attr in nc_attrs:
#     dict_file.update({nc_attr: repr(wrf_file.getncattr(nc_attr))})


# ## write json files :)fwf-var-attrs
# with open(
#     str(data_dir) + f"/json/fwf-attrs.json", "w"
# ) as f:
#     json.dump(
#         dict_file,
#         f,
#         indent=4
#     )

# wrf_ds = readwrf(filein, domain, wright=False)
# print(list(wrf_ds))


# def create_daily_ds(wrf_ds):
#     """
#     Creates a dataset of forecast variables averaged from
#     (1100-1300) local to act as the noon local conditions for daily index/codes
#     calculations

#     Parameters
#     ----------
#         wrf_ds: DataSet
#             WRF dataset at 4-km spatial resolution and one hour tempolar resolution
#                 - tzdict:  dictionary
#                     - Dictionary of all times zones in North America and their respective offsets to UTC
#                 - zone_id: in
#                     - ID of model domain with hours off set from UTC
#                 - noon: int
#                     - 1200 local index based on ID
#                 - plus: int
#                     - 1300 local index based on ID
#                 - minus: int
#                     - 1100 local index based on ID
#                 - tzone_ds: dataset
#                     - Gridded 2D array of zone_id

#     Returns
#     -------
#         daily_ds: DataSet
#             Dataset of daily variables at noon local averaged from (1100-1300)
#             local the averageing was done as a buffer for any frontal passage.
#     """

#     print("Create Daily ds")

#     ### Call on variables
#     tzone = self.tzone

#     ## create I, J for quick indexing
#     I, J = np.ogrid[: self.shape[0], : self.shape[1]]

#     ## determine index for looping based on length of time array and initial time
#     time_array = wrf_ds.Time.values
#     int_time = int(pd.Timestamp(time_array[0]).hour)
#     length = len(time_array) + 1
#     num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
#     index = [
#         i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
#     ]
#     print(f"index of times {index} with initial time {int_time}Z")

#     ## loop every 24 hours at noon local
#     files_ds = []
#     for i in index:
#         # print(i)
#         ## loop each variable
#         mean_da = []
#         for var in wrf_ds.data_vars:
#             if var == "SNOWC":
#                 var_array = wrf_ds[var].values
#                 noon = var_array[(i + tzone), I, J]
#                 day = np.array(wrf_ds.Time[i + 1], dtype="datetime64[D]")
#                 var_da = xr.DataArray(
#                     noon,
#                     name=var,
#                     dims=("south_north", "west_east"),
#                     coords=wrf_ds.isel(time=i).coords,
#                 )
#                 var_da["Day"] = day
#                 mean_da.append(var_da)
#             else:
#                 var_array = wrf_ds[var].values
#                 noon_minus = var_array[(i + tzone - 1), I, J]
#                 noon = var_array[(i + tzone), I, J]
#                 noon_pluse = var_array[(i + tzone + 1), I, J]
#                 noon_mean = (noon_minus + noon + noon_pluse) / 3
#                 day = np.array(wrf_ds.Time[i + 1], dtype="datetime64[D]")
#                 var_da = xr.DataArray(
#                     noon_mean,
#                     name=var,
#                     dims=("south_north", "west_east"),
#                     coords=wrf_ds.isel(time=i).coords,
#                 )
#                 var_da["Day"] = day
#                 mean_da.append(var_da)

#         mean_ds = xr.merge(mean_da)
#         files_ds.append(mean_ds)

#     daily_ds = xr.combine_nested(files_ds, "Day")

#     ## create datarray for carry over rain, this will be added to the next days rain totals
#     ## NOTE: this is rain that fell from noon local until 24 hours past the model initial time ie 00Z, 06Z..
#     r_o_tomorrow_i = wrf_ds.r_o.values[23] - daily_ds.r_o.values[0]
#     r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
#     r_o_tomorrow = np.stack(r_o_tomorrow)
#     r_o_tomorrow_da = xr.DataArray(
#         r_o_tomorrow,
#         name="r_o_tomorrow",
#         dims=("time", "south_north", "west_east"),
#         coords=daily_ds.coords,
#     )
#     r_o_tomorrow_da = xr.where(r_o_tomorrow_da > 1e-4, r_o_tomorrow_da, 0.0)

#     daily_ds["r_o_tomorrow"] = r_o_tomorrow_da

#     ## create daily 24 accumulated precipitation totals
#     x_prev = 0
#     for i, x_val in enumerate(daily_ds.r_o):
#         daily_ds.r_o[i] -= x_prev
#         x_prev = x_val

#     print("Daily ds done")

#     return daily_ds
