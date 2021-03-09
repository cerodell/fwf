import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from wrf import ll_to_xy, xy_to_ll

from pylab import *
import matplotlib.pyplot as plt

from context import data_dir, xr_dir, wrf_dir, tzone_dir, fwf_zarr_dir
from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

domain = "d02"
wrf_model = "wrf3"
date = pd.Timestamp(2018, 7, 18)

## Open MISR dataframe
df = pd.read_csv(str(data_dir) + "/test/samples_for_chris.csv")
df["Datetime"] = pd.to_datetime(df["Datetime"])

## Open static dataset (contains elevation, fuels type, and time zone mask)
static_ds = xr.open_zarr(
    str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.zarr"
)

## Open FBP dataset
forecast_date = date.strftime("%Y%m%d06")
filein = str(data_dir) + f"/test/fpb-{domain}-{forecast_date}.zarr"
fbp_ds = xr.open_zarr(filein)
fbp_ds = fbp_ds.drop_vars("FMC")
fbp_ds["W"].attrs["units"] = "km hr^-1"

### Get a wrf file
if wrf_model == "wrf3":
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CP-04/18072000/wrfout_{domain}_2018-07-20_11:00:00"
else:
    wrf_filein = f"/Users/rodell/Google Drive/Shared drives/WAN00CG-01/21022000/wrfout_{domain}_2021-02-20_11:00:00"
wrf_file = Dataset(wrf_filein, "r")

## get idex form lat and lon locations of fires
xy_np = ll_to_xy(wrf_file, df["Lat"], df["Lon"])
x = xy_np[0]
y = xy_np[1]

## define coordinates for bundled dataset
coords = {"fire": df["Fire_MSL"].values, "time": fbp_ds.Time.values}
for var in list(df):
    coords.update({var: ("fire", df[var].values)})


def make_fire_ds(var, x, y):
    """
    Bundels MISR and FBP data into one dataset
    """
    var_array = fbp_ds[var].values[:, y, x]
    var_da = xr.DataArray(var_array, name=var, dims=("time", "fire"), coords=coords)
    var_da.attrs = fbp_ds[var].attrs
    return var_da


## new dataset with point forecasts of wrf/fwi/fbp at each fire in the misr dataframe
fire_ds = xr.merge([make_fire_ds(var, x, y) for var in list(fbp_ds)])


########### Set up ploting stuff  #############
## Choose Variabels to plot
var_list = ["F", "HFI", "ROS", "W"]
length = len(var_list)

## get list of default matplotlib colors
colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

## Define fire...could loop and plot everyone if you wish
case_ds = fire_ds.isel(fire=3)

## Make Fig title
fig_title = f"Fire: {case_ds.coords['fire'].values} \n Lat, Long: [{case_ds.coords['Lat'].values}, {case_ds.coords['Lon'].values}]"
## Make fig adding subplots based on var list length
fig = plt.figure(figsize=[12, 12])
fig.suptitle(fig_title, fontsize=12)
for i in range(length):
    ax = fig.add_subplot(length + 1, 1, i + 1)
    var = var_list[i]
    var_array = case_ds[var].values
    try:
        ax.set_ylabel(
            f"{case_ds[var].attrs['description']} \n ({case_ds[var].attrs['units']})"
        )
    except:
        ax.set_ylabel(f"{case_ds[var].attrs['description']}")
    ax.yaxis.grid(linewidth=0.4, linestyle="--")
    ax.xaxis.grid(linewidth=0.4, linestyle="--")
    ax.plot(case_ds.time, var_array, color=colors[i])
    ax.axvline(
        case_ds.coords["Datetime"].values,
        color="k",
        linestyle="--",
        label="MISR OverPass",
    )
ax.legend()

fig.savefig(str(data_dir) + f"/images/MISR-FBP-{domain}-{forecast_date}.png")

print("Total Run Time: ", datetime.now() - startTime)
