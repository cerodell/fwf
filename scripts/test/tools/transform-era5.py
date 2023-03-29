import context

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
from context import data_dir

# era5_ds = salem.open_xr_dataset("/Volumes/WFRT-Data02/era5/era5-2022080500.nc")
# era5_ds = era5_ds.isel(time=1)
# era5_ds["tp"] = era5_ds["tp"]*1000

filein = "/Volumes/WFRT-Ext24/era5/era5-2020123100.nc"
wrf_model = "wrf4"
domain = "d02"
doi = pd.Timestamp(f"{filein[-13:-9]}-{filein[-9:-7]}-{filein[-7:-5]}")

era5_ds = salem.open_xr_dataset(filein)


int_time = era5_ds.time.values
tomorrow = pd.to_datetime(str(int_time[0] + np.timedelta64(1, "D")))
era5_ds_tomorrow = salem.open_xr_dataset(
    f'/Volumes/WFRT-Data02/era5/era5-{tomorrow.strftime("%Y%m%d%H")}.nc'
)
era5_ds = xr.merge([era5_ds, era5_ds_tomorrow])

era5_ds = era5_ds.sel(
    time=slice(doi.strftime("%Y%m%dT06"), tomorrow.strftime("%Y%m%dT05"))
)

era5_ds["T"] = era5_ds.t2m - 273.15
era5_ds["TD"] = era5_ds.d2m - 273.15
era5_ds["r_o_hourly"] = era5_ds.tp * 1000
# era5_ds['r_o_hourly'] = xr.where(era5_ds['r_o_hourly'] < 0, 0, era5_ds['r_o_hourly'])

# era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["u10"], era5_ds["v10"]))
era5_ds["SNOWH"] = era5_ds["sd"]
era5_ds["U10"] = era5_ds["u10"]
era5_ds["V10"] = era5_ds["v10"]

keep_vars = [
    "r_o_hourly",
    "SNOWC",
    "SNOWH",
    "SNW",
    "T",
    "TD",
    "U10",
    "V10",
    "W",
    "WD",
    "r_o",
    "H",
]
era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])

krig_ds = salem.open_xr_dataset(str(data_dir) + "/d02-grid.nc")
fwf_d02_ds = xr.open_dataset(
    f'/Volumes/Scratch/FWF-WAN00CG/d02/{doi.strftime("%Y%m")}/fwf-hourly-d02-{doi.strftime("%Y%m%d06")}.nc'
)
fwf_d02_ds["time"] = ("time", fwf_d02_ds.Time.values)
fwf_d02_ds = fwf_d02_ds.sel(
    time=slice(doi.strftime("%Y%m%dT06"), tomorrow.strftime("%Y%m%dT05"))
)

# krig_ds = fwf_d02_ds.salem.grid.to_dataset()
# krig_ds = krig_ds.rename({'x': 'west_east','y': 'south_north'})
# krig_ds = krig_ds.assign_coords({"XLONG": fwf_d02_ds.XLONG})
# krig_ds = krig_ds.assign_coords({"XLAT": fwf_d02_ds.XLAT})
# print(krig_ds)
# krig_ds.to_netcdf(str(data_dir) +"/d02-grid.nc", mode="w")

era5_ds = krig_ds.salem.transform(era5_ds, interp="spline")
era5_ds = era5_ds.assign_coords(
    {"XLONG": (("south_north", "west_east"), fwf_d02_ds.XLONG.values)}
)
era5_ds = era5_ds.assign_coords(
    {"XLAT": (("south_north", "west_east"), fwf_d02_ds.XLAT.values)}
)

time_array = era5_ds.time.values
era5_ds["time"] = np.arange(0, len(era5_ds.time.values))
era5_ds = era5_ds.assign_coords({"Time": ("time", time_array)})
era5_ds["SNOWC"] = (
    ("time", "south_north", "west_east"),
    fwf_d02_ds["SNOWC"].values,
)
era5_ds["SNOWH"] = (
    ("time", "south_north", "west_east"),
    fwf_d02_ds["SNOWH"].values,
)
era5_ds["SNW"] = (("time", "south_north", "west_east"), fwf_d02_ds["SNW"].values)

era5_ds["r_o_hourly"] = xr.where(era5_ds["r_o_hourly"] < 0, 0, era5_ds["r_o_hourly"])
r_oi = era5_ds["r_o_hourly"].values
r_accumulated_list = []
for i in range(len(era5_ds.time)):
    r_hour = np.sum(r_oi[:i], axis=0)
    r_accumulated_list.append(r_hour)
r_o = np.stack(r_accumulated_list)
r_o = xr.DataArray(r_o, name="r_o", dims=("time", "south_north", "west_east"))
era5_ds["r_o"] = r_o

RH = (
    (6.11 * 10 ** (7.5 * (era5_ds.TD / (237.7 + era5_ds.TD))))
    / (6.11 * 10 ** (7.5 * (era5_ds.T / (237.7 + era5_ds.T))))
    * 100
)
RH = xr.where(RH > 100, 100, RH)
RH = xr.DataArray(RH, name="H", dims=("time", "south_north", "west_east"))
era5_ds["H"] = RH
if np.min(era5_ds.H) > 90:
    raise ValueError("ERROR: Check TD nonphysical RH values")

W = np.sqrt(era5_ds["U10"].values ** 2 + era5_ds["V10"].values ** 2) * 3.6
W = xr.DataArray(W, name="W", dims=("time", "south_north", "west_east"))
era5_ds["W"] = W
era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["U10"], era5_ds["V10"]))

era5_ds.attrs = fwf_d02_ds.attrs
keep_vars = [
    "SNOWC",
    "SNOWH",
    "SNW",
    "T",
    "TD",
    "U10",
    "V10",
    "W",
    "WD",
    "r_o",
    "H",
]
era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])
