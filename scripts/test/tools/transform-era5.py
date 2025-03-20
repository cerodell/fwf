import context
import json

import salem
import numpy as np
import xarray as xr
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import matplotlib.colors


from context import data_dir, root_dir

with open(str(root_dir) + "/json/colormaps-dev.json") as f:
    cmaps = json.load(f)


wrf_daily_d03 = salem.open_xr_dataset("/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-daily-d03-2004091000.nc")
wrf_hourly_d03 = salem.open_xr_dataset("/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-hourly-d03-2004091000.nc")



for doi in pd.date_range("2004-08-01", "2004-09-01"):
    wrf_daily_d03 = salem.open_xr_dataset(f"/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-daily-d03-{doi.strftime('%Y%m%d00')}.nc").rename_vars({'r_o_tomorrow': 'r_o'})

    for var in ['P', 'r_o']:
        try:
            fig = plt.figure()
            ax= fig.add_subplot(1,1,1)

            vmin, vmax = cmaps[var]["vmin"], cmaps[var]["vmax"]
            title, colors = str(cmaps[var]["title"]), cmaps[var]["colors18"]
            custom_cmap = LinearSegmentedColormap.from_list(
                "custom_cmap", [matplotlib.colors.hex2color(color) for color in colors]
            )
            norm = BoundaryNorm(cmaps[var]["levels"], custom_cmap.N)

            wrf_daily_d03[var].isel(time =0).salem.quick_map(cmap=custom_cmap, ax=ax, norm=norm,)
        except:
            plt.close()

# for var in wrf_hourly_d03:
#     fig = plt.figure()
#     ax= fig.add_subplot(1,1,1)
#     wrf_hourly_d03[var].isel(time =18).salem.quick_map(ax = ax)

wrf_daily_d03['r_o_tomorrow'].isel(time =0).salem.quick_map()



wrf_hourly_d03['F'].isel(time =18).salem.quick_map()


era5_ds = salem.open_xr_dataset(f"{data_dir}/ecmwf/ecmwf-fwi-20040731.nc").isel(valid_time = 0)

# Shift longitude from [0, 360] to [-180, 180]
era5_ds = era5_ds.assign_coords(longitude=(((era5_ds.longitude + 180) % 360) - 180)).sortby("longitude")

grid_ds = salem.open_xr_dataset(f"{data_dir}/wrf/fa/d03-grid.nc")

era5_ds_AB = grid_ds.salem.transform(era5_ds, interp='linear').rename_vars()
era5_ds_AB = era5_ds_AB.rename_vars({'fwinx': 'S', 'drtcode': 'D', 'dufmcode': 'P', 'ffmcode': 'F', 'infsinx': 'R', 'fbupinx': 'U', 'fdsrte': 'DSR' })
era5_ds_AB = era5_ds_AB.expand_dims('time').drop_vars(['valid_time', 'surface'])
era5_ds_AB = era5_ds_AB.transpose('time', 'south_north', 'west_east')
era5_ds_AB['r_o_tomorrow'] = xr.DataArray(np.zeros_like(era5_ds_AB['F'].values), name="r_o_tomorrow", dims=("time", "south_north", "west_east"))
era5_ds_AB = era5_ds_AB.assign_coords({"Time": ("time", [pd.Timestamp("2004-07-31T00")])})

era5_ds_AB = era5_ds_AB.assign_coords(
    {"XLONG": (("south_north", "west_east"), grid_ds.XLONG.values)}
)
era5_ds_AB = era5_ds_AB.assign_coords(
    {"XLAT": (("south_north", "west_east"), grid_ds.XLAT.values)}
)

era5_ds_AB.to_netcdf("/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-daily-d03-2004073100.nc")
era5_ds_hourly_AB = era5_ds_AB.assign_coords({"Time": ("time", [pd.Timestamp("2004-07-31T23")])})
era5_ds_hourly_AB.to_netcdf("/NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi/fwf-hourly-d03-2004073100.nc")

wrf_daily_d03['U'].isel(time =0).salem.quick_map()


time_array = era5_ds.time.values
era5_ds["time"] = np.arange(0, len(era5_ds.time.values))
era5_ds = era5_ds.assign_coords({"Time": ("time", time_array)})
era5_ds["SNOWC"] = (
    ("time", "south_north", "west_east"),
    grid_ds["SNOWC"].values,
)
era5_ds["SNOWH"] = (
    ("time", "south_north", "west_east"),
    grid_ds["SNOWH"].values,
)
era5_ds["SNW"] = (("time", "south_north", "west_east"), grid_ds["SNW"].values)

era5_ds["r_o_hourly"] = xr.where(era5_ds["r_o_hourly"] < 0, 0, era5_ds["r_o_hourly"])
r_oi = era5_ds["r_o_hourly"].values
r_accumulated_list = []
for i in range(len(era5_ds.time)):
    r_hour = np.sum(r_oi[:i], axis=0)
    r_accumulated_list.append(r_hour)
r_o = np.stack(r_accumulated_list)
r_o = xr.DataArray(r_o, name="r_o", dims=("time", "south_north", "west_east"))
era5_ds["r_o"] = r_o



# # era5_ds = era5_ds.isel(time=1)
# # era5_ds["tp"] = era5_ds["tp"]*1000

# filein = "/Volumes/WFRT-Ext24/era5/era5-2020123100.nc"
# filein = "/Volumes/WFRT-Ext22/ecmwf/era5-land/198912/era5-land-1989122800.nc"
# wrf_model = "wrf4"
# domain = "d02"
# doi = pd.Timestamp(f"{filein[-13:-9]}-{filein[-9:-7]}-{filein[-7:-5]}")

# era5_ds = salem.open_xr_dataset(filein)


# int_time = era5_ds.time.values
# tomorrow = pd.to_datetime(str(int_time[0] + np.timedelta64(1, "D")))
# era5_ds_tomorrow = salem.open_xr_dataset(
#     f'/Volumes/WFRT-Ext22/ecmwf/era5-land/198912/era5-land-{tomorrow.strftime("%Y%m%d%H")}.nc'
# )
# era5_ds = xr.merge([era5_ds, era5_ds_tomorrow])

# era5_ds = era5_ds.sel(
#     time=slice(doi.strftime("%Y%m%dT06"), tomorrow.strftime("%Y%m%dT05"))
# )

# era5_ds["T"] = era5_ds.t2m - 273.15
# era5_ds["TD"] = era5_ds.d2m - 273.15
# era5_ds["r_o_hourly"] = era5_ds.tp * 1000
# # era5_ds['r_o_hourly'] = xr.where(era5_ds['r_o_hourly'] < 0, 0, era5_ds['r_o_hourly'])

# # era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["u10"], era5_ds["v10"]))
# era5_ds["SNOWH"] = era5_ds["sde"]
# era5_ds["U10"] = era5_ds["u10"]
# era5_ds["V10"] = era5_ds["v10"]

# keep_vars = [
#     "r_o_hourly",
#     "SNOWC",
#     "SNOWH",
#     "SNW",
#     "T",
#     "TD",
#     "U10",
#     "V10",
#     "W",
#     "WD",
#     "r_o",
#     "H",
# ]
# era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])

# # krig_ds = salem.open_xr_dataset(str(data_dir) + "/d02-grid.nc")
# fwf_d02_ds = xr.open_dataset(
#     f'/Volumes/Scratch/FWF-WAN00CG/d02/{doi.strftime("%Y%m")}/fwf-hourly-d02-{doi.strftime("%Y%m%d06")}.nc'
# )
# fwf_d02_ds["time"] = ("time", fwf_d02_ds.Time.values)
# fwf_d02_ds = fwf_d02_ds.sel(
#     time=slice(doi.strftime("%Y%m%dT06"), tomorrow.strftime("%Y%m%dT05"))
# )

# # krig_ds = fwf_d02_ds.salem.grid.to_dataset()
# # krig_ds = krig_ds.rename({'x': 'west_east','y': 'south_north'})
# # krig_ds = krig_ds.assign_coords({"XLONG": fwf_d02_ds.XLONG})
# # krig_ds = krig_ds.assign_coords({"XLAT": fwf_d02_ds.XLAT})
# # print(krig_ds)
# # krig_ds.to_netcdf(str(data_dir) +"/d02-grid.nc", mode="w")

# era5_ds = krig_ds.salem.transform(era5_ds, interp="spline")
# era5_ds = era5_ds.assign_coords(
#     {"XLONG": (("south_north", "west_east"), fwf_d02_ds.XLONG.values)}
# )
# era5_ds = era5_ds.assign_coords(
#     {"XLAT": (("south_north", "west_east"), fwf_d02_ds.XLAT.values)}
# )

# time_array = era5_ds.time.values
# era5_ds["time"] = np.arange(0, len(era5_ds.time.values))
# era5_ds = era5_ds.assign_coords({"Time": ("time", time_array)})
# era5_ds["SNOWC"] = (
#     ("time", "south_north", "west_east"),
#     fwf_d02_ds["SNOWC"].values,
# )
# era5_ds["SNOWH"] = (
#     ("time", "south_north", "west_east"),
#     fwf_d02_ds["SNOWH"].values,
# )
# era5_ds["SNW"] = (("time", "south_north", "west_east"), fwf_d02_ds["SNW"].values)

# era5_ds["r_o_hourly"] = xr.where(era5_ds["r_o_hourly"] < 0, 0, era5_ds["r_o_hourly"])
# r_oi = era5_ds["r_o_hourly"].values
# r_accumulated_list = []
# for i in range(len(era5_ds.time)):
#     r_hour = np.sum(r_oi[:i], axis=0)
#     r_accumulated_list.append(r_hour)
# r_o = np.stack(r_accumulated_list)
# r_o = xr.DataArray(r_o, name="r_o", dims=("time", "south_north", "west_east"))
# era5_ds["r_o"] = r_o

# RH = (
#     (6.11 * 10 ** (7.5 * (era5_ds.TD / (237.7 + era5_ds.TD))))
#     / (6.11 * 10 ** (7.5 * (era5_ds.T / (237.7 + era5_ds.T))))
#     * 100
# )
# RH = xr.where(RH > 100, 100, RH)
# RH = xr.DataArray(RH, name="H", dims=("time", "south_north", "west_east"))
# era5_ds["H"] = RH
# if np.min(era5_ds.H) > 90:
#     raise ValueError("ERROR: Check TD nonphysical RH values")

# W = np.sqrt(era5_ds["U10"].values ** 2 + era5_ds["V10"].values ** 2) * 3.6
# W = xr.DataArray(W, name="W", dims=("time", "south_north", "west_east"))
# era5_ds["W"] = W
# era5_ds["WD"] = 180 + ((180 / np.pi) * np.arctan2(era5_ds["U10"], era5_ds["V10"]))

# era5_ds.attrs = fwf_d02_ds.attrs
# keep_vars = [
#     "SNOWC",
#     "SNOWH",
#     "SNW",
#     "T",
#     "TD",
#     "U10",
#     "V10",
#     "W",
#     "WD",
#     "r_o",
#     "H",
# ]
# era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])
