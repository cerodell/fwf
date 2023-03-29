import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
from utils.era5 import read_era5

from datetime import datetime, date, timedelta
from context import data_dir

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


model = "ecmwf"
domain = "era5"

# %%
### Call on variables
tzone_ds = salem.open_xr_dataset(
    str(data_dir) + f"/static/static-vars-{model}-{domain}.nc"
)
tzone = tzone_ds["ZoneST"]
tzone_array = tzone.values
tzone_array[tzone_array <= -12] *= -1

tzone = xr.where(tzone > -12, tzone, tzone * -1)


int_ds = read_era5(pd.Timestamp("2019-12-31"), model, domain)
int_ds = int_ds.load()
shape = int_ds["XLONG"].shape
# chuc_size = int_ds['T'].chunks()


# test = int_ds.isel(time = tzone+index[0])
# test2 = test.sel(west_east=slice(-180, -160), south_north=slice(20, -20))
# test2['time'].salem.quick_map()

# %%
## create I, J for quick indexing
I, J = np.ogrid[: shape[0], : shape[1]]

## determine index for looping based on length of time array and initial time
time_array = int_ds.Time.values
print(time_array[0])
int_time = int(pd.Timestamp(time_array[0]).hour)
length = len(time_array) + 1
num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
index = [i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days]
print(f"index of 12Z times {index} with initial time {int_time}Z")


xr_startTime = datetime.now()
xr_list = []
for i in index:
    ds_i = int_ds.isel(time=tzone + i)
    ds_i = ds_i.drop(["Time", "time"])
    ds_i = ds_i.expand_dims({"time": i})
    xr_list.append(ds_i)
    # ds_i = ds_i.assign_coords({"Time": ("time", np.array(int_ds.Time[i + 1], dtype="datetime64[D]"))})
daily_xr = xr.combine_nested(xr_list, "time")
print("xarray indexing time: ", datetime.now() - xr_startTime)


np_startTime = datetime.now()
## loop every 24 hours at noon local
files_ds = []
for i in index:
    mean_da = []
    for var in int_ds.data_vars:
        var_array = int_ds[var].values
        noon = var_array[(i + tzone_array), I, J]
        day = np.array(int_ds.Time[i + 1], dtype="datetime64[D]")
        var_da = xr.DataArray(
            noon,
            name=var,
            dims=("south_north", "west_east"),
            coords=int_ds.isel(time=i).coords,
        )
        var_da["Time"] = day
        mean_da.append(var_da)
    mean_ds = xr.merge(mean_da)
    files_ds.append(mean_ds)

daily_ds = xr.combine_nested(files_ds, "time")
print("numpy indexing time: ", datetime.now() - np_startTime)


## create datarray for carry over rain, this will be added to the next days rain totals
## NOTE: this is rain that fell from noon local until 23 hours past the model initial time ie 00Z, 06Z..
r_o_tomorrow_i = int_ds.r_o.values[23] - daily_ds.r_o.values[0]
r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
r_o_tomorrow = np.stack(r_o_tomorrow)
r_o_tomorrow_da = xr.DataArray(
    r_o_tomorrow,
    name="r_o_tomorrow",
    dims=("time", "south_north", "west_east"),
    coords=daily_ds.coords,
)
r_o_tomorrow_da = xr.where(r_o_tomorrow_da > 1e-4, r_o_tomorrow_da, 0.0)

daily_ds["r_o_tomorrow"] = r_o_tomorrow_da

## create daily 24 accumulated precipitation totals
x_prev = 0
for i, x_val in enumerate(daily_ds.r_o):
    daily_ds.r_o[i] -= x_prev
    x_prev = x_val

print("Daily ds done")


# %%
