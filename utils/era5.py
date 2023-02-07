#!/Users/crodell/miniconda3/envs/fwf/bin/python


import context

import salem
import numpy as npdd
import xarray as xr
import geopandas as gpd
import pandas as pd
from datetime import datetime

from context import data_dir

wrf_model = "wrf4"
domain = "d02"
# date_range = pd.date_range("2021-01-01", "2021-01-01")

# doi = date_range[0]

# filein = f'/Volumes/WFRT-Data02/era5/era5-2021010100.nc'


def config_era5(filein):
    startTime = datetime.now()
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
    try:
        era5_ds = era5_ds.isel(expver=0)
    except:
        pass
    # day2 = pd.to_datetime(str(int_time[0] + np.timedelta64(2, "D")))

    # era5_ds = era5_ds.sel(
    #     time=slice(doi.strftime("%Y%m%dT00"), tomorrow.strftime("%Y%m%dT12"))
    # )

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
    # print(era5_ds)
    krig_ds = salem.open_xr_dataset(str(data_dir) + "/d02-grid.nc")
    fwf_d02_ds = xr.open_dataset(
        f"/Volumes/Scratch/FWF-WAN00CG/d02/202103/fwf-hourly-d02-2021031106.nc"
    )

    # print(era5_ds)
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

    era5_ds["r_o_hourly"] = xr.where(
        era5_ds["r_o_hourly"] < 0, 0, era5_ds["r_o_hourly"]
    )
    r_oi = era5_ds["r_o_hourly"].values
    r_accumulated_list = []
    for i in range(len(era5_ds.time)):
        r_hour = np.sum(r_oi[:i], axis=0)
        r_accumulated_list.append(r_hour)
    r_o = np.stack(r_accumulated_list)
    r_o = xr.DataArray(r_o, name="r_o", dims=("time", "south_north", "west_east"))
    era5_ds["r_o"] = r_o
    era5_ds["r_o"] = era5_ds.r_o - era5_ds.r_o.isel(time=0)
    # print(np.unique((era5_ds["r_o"].values < 0)))

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

    print(f"Time to config era5 to wrf domain {datetime.now() - startTime}")
    # print(f'WIND MIN {float(era5_ds["W"].min())}')
    # print(f'RH MIN {float(era5_ds["H"].min())}')
    # print(f'RH MAX {float(era5_ds["H"].max())}')
    # print(f'WD MIN {float(era5_ds["WD"].min())}')
    # print(f'WD MAX {float(era5_ds["WD"].max())}')
    # print(f'r_o MIN {float(era5_ds["r_o"].min())}')

    return era5_ds


# ## Open gridded static
# static_ds = xr.open_dataset(
#     str(data_dir) + f"/static/static-vars-{wrf_model}-{domain}.nc"
# )

# ### Call on variables
# tzone = static_ds.ZoneDT.values
# shape = np.shape(era5_ds.T[0, :, :])
# ## create I, J for quick indexing
# I, J = np.ogrid[: shape[0], : shape[1]]

# ## determine index for looping based on length of time array and initial time
# time_array = era5_ds.Time.values
# int_time = int(pd.Timestamp(time_array[0]).hour)
# length = len(time_array) + 1
# num_days = [i - 12 for i in range(1, length) if i % 24 == 0]
# index = [
#     i - int_time if 12 - int_time >= 0 else i + 24 - int_time for i in num_days
# ]
# print(f"index of times {index} with initial time {int_time}Z")

# ## loop every 24 hours at noon local
# files_ds = []
# for i in index:
#     print(i)
#     ## loop each variable
#     mean_da = []
#     for var in era5_ds.data_vars:
#         if var == "SNOWC":
#             var_array = era5_ds[var].values
#             noon = var_array[(i + tzone), I, J]
#             day = np.array(era5_ds.Time[i + 1], dtype="datetime64[D]")
#             var_da = xr.DataArray(
#                 noon,
#                 name=var,
#                 dims=("south_north", "west_east"),
#                 coords=era5_ds.isel(time=i).coords,
#             )
#             var_da["Time"] = day
#             mean_da.append(var_da)
#         else:
#             print(var)
#             var_array = era5_ds[var].values
#             noon_minus = var_array[(i + tzone - 1), I, J]
#             noon = var_array[(i + tzone), I, J]
#             noon_pluse = var_array[(i + tzone + 1), I, J]
#             noon_mean = (noon_minus + noon + noon_pluse) / 3
#             day = np.array(era5_ds.Time[i + 1], dtype="datetime64[D]")
#             var_da = xr.DataArray(
#                 noon_mean,
#                 name=var,
#                 dims=("south_north", "west_east"),
#                 coords=era5_ds.isel(time=i).coords,
#             )
#             var_da["Time"] = day
#             mean_da.append(var_da)

#     mean_ds = xr.merge(mean_da)
#     files_ds.append(mean_ds)

# daily_ds = xr.combine_nested(files_ds, "time")

# ## create datarray for carry over rain, this will be added to the next days rain totals
# ## NOTE: this is rain that fell from noon local until 24 hours past the model initial time ie 00Z, 06Z..
# r_o_tomorrow_i = era5_ds.r_o.values[23] - daily_ds.r_o.values[0]
# r_o_tomorrow = [r_o_tomorrow_i for i in range(len(num_days))]
# r_o_tomorrow = np.stack(r_o_tomorrow)
# r_o_tomorrow_da = xr.DataArray(
#     r_o_tomorrow,
#     name="r_o_tomorrow",
#     dims=("time", "south_north", "west_east"),
#     coords=daily_ds.coords,
# )
# r_o_tomorrow_da = xr.where(r_o_tomorrow_da > 1e-4, r_o_tomorrow_da, 0.0)

# daily_ds["r_o_tomorrow"] = r_o_tomorrow_da

# ## create daily 24 accumulated precipitation totals
# x_prev = 0
# for i, x_val in enumerate(daily_ds.r_o):
#     daily_ds.r_o[i] -= x_prev
#     x_prev = x_val

# print("Daily ds done")


# # era5_ds["SNOWC"] = fwf_d02_ds["SNOWC"]
# # # era5_ds["SNW"] = fwf_d02_ds["SNW"]

# # keep_vars = [
# #     "SNOWC",
# #     "SNOWH",
# #     "SNW",
# #     "T",
# #     "TD",
# #     "U10",
# #     "V10",
# #     "W",
# #     "WD",
# #     "r_o",
# #     "H",
# # ]
# # era5_ds = era5_ds.drop([var for var in list(era5_ds) if var not in keep_vars])

# # print(era5_ds)

# # era5_ds = era5_ds.isel(time = 1)
# # # era5_ds["tp"] = era5_ds["tp"]*1000

# # wrfd02_ds = salem.open_wrf_dataset(str(data_dir) + f"/wrf/wrfout_d02_2021-01-14_00:00:00")
# # print(wrfd02_ds)
# # fwf_d02_ds = xr.open_dataset("/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-hourly-d02-2021070106.nc")
# # fwf_d02_ds = salem.open_xr_dataset("/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-daily-d02-2021070106.nc")

# # print(fwf_d02_ds)

# # # fwf_d02_ds = salem.open_wrf_dataset("/Volumes/Scratch/FWF-WAN00CG/d02/202107/fwf-daily-d02-2021070106.nc")
# # import matplotlib.pyplot as plt


# # test = fwf_d02_ds.salem.transform(era5_ds, interp='spline')

# # # test = xr.where(test.isnull(),1000, test )
# # fig = plt.figure(figsize=(12, 6))
# # ax = fig.add_subplot(1, 1, 1)
# # ax.imshow(test.t2m.values[::-1])
# # # fig_name = f'temp_wsp({int(da.W.mean())})_rh({int(da.H.mean())})_precip({int(da.r_o.mean())})'
# # plt.savefig(f"test.png", dpi=250, bbox_inches="tight")


# # # test.t2m.plot()
# # # print(test)

# # print(np.unique(test.t2m.isnull(), return_counts = True))
