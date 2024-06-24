import os
import context
import salem
import dask
import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir


""" ####################################################################### """
""" ######################### Grab WRF Variables ########################## """


def read_adda(config):

    doi, model, domain = config["doi"], config["model"], config["domain"]

    filein = f'/Volumes/WFRT-Ext21/fwf-data/{model}/{domain}/trial/fwf-hourly-{domain}-{doi.strftime("%Y%m%d00")}.nc'
    # adda_dir_all = "/Volumes/ThunderBay/CRodell/ADDA_V2/"
    adda_dir_all = "/Volumes/WFRT-Ext20/ADDA_V2/"
    adda_dir_TD2 = "/Volumes/WFRT-Ext20/ADDA_V2/TD2/"

    if os.path.isfile(filein) == True:
        grid_ds = salem.open_xr_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")
        fwf_ds = xr.open_dataset(filein)
        try:
            del fwf_ds["south_north"]
            del fwf_ds["west_east"]
        except:
            pass
        fwf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
        fwf_ds = fwf_ds.transpose("time", "south_north", "west_east")

    else:
        grid_ds = salem.open_xr_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")
        date_range = pd.date_range(
            (doi - pd.Timedelta(hours=1)).strftime("%Y%m%dT%H"),
            (doi + pd.Timedelta(hours=23)).strftime("%Y%m%dT%H"),
            freq="h",
        )

        def get_timestamp_vars(file_name):
            return str(file_name).split("/")[-1][9:-9]

        def get_files_vars(date_of_int):
            return sorted(
                Path(str(adda_dir_all) + f'/{date_of_int.strftime("%Y")}/').glob(
                    f"cstm_d01*"
                ),
                key=get_timestamp_vars,
            )

        if date_range[0].strftime("%Y") != date_range[-1].strftime("%Y"):
            adda_files = get_files_vars(date_range[-1])

        else:
            adda_files = get_files_vars(date_range[0])
        adda_scan = pd.to_datetime(
            [
                str(adda_files[i]).split("/")[-1][9:-12]
                + "T"
                + str(adda_files[i]).split("/")[-1][-11:-9]
                for i in range(len(adda_files))
            ]
        )
        try:
            i = np.where(adda_scan == date_range[0])[0][0]
            j = np.where(adda_scan == date_range[-1])[0][0]
            last_year = False
        except:
            i = np.where(adda_scan == date_range[1])[0][0]
            j = np.where(adda_scan == date_range[-1])[0][0]
            last_year = True

        adda_files = adda_files[i : j + 1]
        adda_files = [str(file) for file in adda_files]

        def get_timestamp_td2(file_name):
            return str(file_name).split("/")[-1][4:-3]

        def get_files_td2(date_of_int):
            return sorted(
                Path(str(adda_dir_TD2) + f'/{date_of_int.strftime("%Y")}/').glob(
                    f"TD2_*"
                ),
                key=get_timestamp_td2,
            )

        if date_range[0].strftime("%Y") != date_range[-1].strftime("%Y"):
            td2_files = get_files_td2(date_range[-1])

        else:
            td2_files = get_files_td2(date_range[0])
        td2_scan = pd.to_datetime(
            [
                str(td2_files[i]).split("/")[-1][4:-3].replace("_", "T")
                for i in range(len(td2_files))
            ]
        )
        try:
            i = np.where(td2_scan == date_range[0])[0][0]
            j = np.where(td2_scan == date_range[-1])[0][0]

        except:
            i = np.where(td2_scan == date_range[1])[0][0]
            j = np.where(td2_scan == date_range[-1])[0][0]

        td2_files = td2_files[i : j + 1]
        td2_files = [str(file) for file in td2_files]

        def open_adda(i):
            ds_adda = (
                xr.open_dataset(adda_files[i])[
                    [
                        "temperature_2m",
                        "precipitation_0m",
                        "windspeed_10m",
                        "winddirection_10m",
                    ]
                ]
                .rename_vars(
                    {
                        "temperature_2m": "T",
                        "precipitation_0m": "r_o",
                        "windspeed_10m": "W",
                        "winddirection_10m": "WD",
                    }
                )
                .chunk("auto")
            )
            ds_td2 = (
                xr.open_dataset(td2_files[i])[["TD2"]]
                .rename_vars({"TD2": "TD"})
                .rename_dims({"Time": "time"})
                .chunk("auto")
            )
            ds = xr.combine_by_coords([ds_adda, ds_td2])
            ds = ds.assign_coords(
                Time=(
                    "time",
                    [pd.Timestamp(get_timestamp_vars(adda_files[i]).replace("_", "T"))],
                )
            )
            return ds

        fwf_ds = xr.combine_nested(
            [open_adda(i) for i in range(len(adda_files))], concat_dim="time"
        ).chunk("auto")

        fwf_ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
        fwf_ds = fwf_ds.assign_coords(
            {
                "south_north": grid_ds["south_north"].values,
                "west_east": grid_ds["west_east"].values,
            }
        )
        fwf_ds = fwf_ds.assign_coords(
            XLAT=(("south_north", "west_east"), grid_ds["XLAT"].values)
        )
        fwf_ds = fwf_ds.assign_coords(
            XLONG=(("south_north", "west_east"), grid_ds["XLONG"].values)
        )

        fwf_ds["T"] = fwf_ds["T"] - 273.15
        fwf_ds["W"] = fwf_ds["W"] * 3.6

        RH = (
            (6.11 * 10 ** (7.5 * (fwf_ds.TD / (237.7 + fwf_ds.TD))))
            / (6.11 * 10 ** (7.5 * (fwf_ds.T / (237.7 + fwf_ds.T))))
            * 100
        )
        RH = xr.where(RH > 100, 100, RH)
        RH = xr.DataArray(RH, name="H", dims=("time", "south_north", "west_east"))
        fwf_ds["H"] = RH
        if np.min(fwf_ds.H) > 90:
            raise ValueError("ERROR: Check TD unphysical RH values")

        fwf_ds["r_o"] = fwf_ds.r_o - fwf_ds.r_o.isel(time=0)
        if last_year == False:
            fwf_ds = fwf_ds.isel(time=slice(1, 25))

        r_oi = fwf_ds["r_o"]
        r_o_plus1 = dask.array.dstack(
            (dask.array.zeros_like(fwf_ds["r_o"][0]).T, r_oi.T)
        ).T
        r_hourly_list = []
        for i in range(len(fwf_ds.time)):
            r_hour = r_oi[i] - r_o_plus1[i]
            r_hourly_list.append(r_hour)
        r_hourly = dask.array.stack(r_hourly_list)
        r_hourly = xr.DataArray(
            r_hourly, name="r_o_hourly", dims=("time", "south_north", "west_east")
        )
        r_hourly = xr.where(r_hourly < 0, 0, r_hourly)
        fwf_ds["r_o_hourly"] = r_hourly

        for var in fwf_ds:
            fwf_ds[var].attrs = grid_ds.attrs

    return fwf_ds.unify_chunks()


def grid_adda(model, domain):
    ds = salem.open_wrf_dataset(str(data_dir) + f"/adda/wrfout_d01_2001-06-30_21_00_00")
    return ds
