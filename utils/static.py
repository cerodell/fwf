import os
import context
import salem
import json
import numpy as np
import pandas as pd
import xarray as xr
import pytz

import geopandas as gpd
from pathlib import Path
import matplotlib.pyplot as plt

from datetime import datetime
from utils.wrf_ import grid_wrf
from utils.eccc import grid_eccc
from utils.era5 import grid_ecmwf
from utils.adda import grid_adda


from context import data_dir, root_dir


class build_static:
    def __init__(self, model, domain):
        self.model = model
        self.domain = domain
        # try:
        #   ds = salem.open_xr_dataset(filein)
        #   try:
        #       ds = ds.isel(Time=0)
        #   except:
        #       try:
        #         ds = ds.isel(time=0)
        #       except:
        #           pass
        # except:
        function_mapping = {
            "wrf": grid_wrf,
            "eccc": grid_eccc,
            "ecmwf": grid_ecmwf,
            "adda": grid_adda,
        }
        selected_function = function_mapping.get(model)
        if selected_function is not None:
            ds = selected_function(model, domain)
        else:
            raise ValueError(f"Function from {model} is not found")

        self.ds_grid = ds.salem.grid.to_dataset()

        return

    def build_grid(self):
        if os.path.exists(str(data_dir) + f"/{self.model}/{self.domain}-grid.nc"):
            print(f"Grid file exists for {self.model} - {self.domain}")
        else:
            ds_grid = self.ds_grid
            lon, lat = ds_grid.salem.grid.ll_coordinates
            ds_grid["XLAT"] = (("y", "x"), lat)
            ds_grid["XLONG"] = (("y", "x"), lon)
            ds_grid = ds_grid.set_coords(["XLAT", "XLONG"])
            ds_grid = ds_grid.rename(
                {
                    "x": "west_east",
                    "y": "south_north",
                }
            )
            var = "blank"
            ds_grid[var] = (("south_north", "west_east"), np.zeros_like(lon))
            ds_grid[var].attrs["pyproj_srs"] = ds_grid.attrs["pyproj_srs"]
            ds_grid[var].salem.quick_map(
                cmap="coolwarm",
                extend="both",
            )
            ds_grid.to_netcdf(str(data_dir) + f"/{self.model}/{self.domain}-grid.nc")
            self.ds_grid = ds_grid
        return

    def timezone_mask(self):
        self.season = "ST"
        if os.path.exists(
            str(data_dir) + f"/tzone/tzone-{self.model}-{self.domain}-{self.season}.nc"
        ):
            print(f"Tzone file exists for {self.model} - {self.domain}")
        else:
            tzone_shp = (
                str(data_dir)
                + "/tzone/timezones-with-oceans/combined-shapefile-with-oceans.shp"
            )
            ds = self.ds_grid
            pyproj_srs = ds.attrs["pyproj_srs"]
            df = salem.read_shapefile(tzone_shp)
            # df = df[df["tzid"].str.contains("America")]
            # df = df[~df["tzid"].str.contains("Asia")]
            # df = df[~df["tzid"].str.contains("Australia")]
            # df = df[~df["tzid"].str.contains("Antarctica")]
            # df = df[~df["tzid"].str.contains("Europe")]
            # df = df[~df["tzid"].str.contains("Africa")]
            # df = df[df["min_y"] > 14]
            # df = df[df["min_y"] > 0]
            # df = df[df["min_x"] <-180]

            lats = ds.XLAT.values
            zero_full = np.zeros(lats.shape)

            ds["var"] = (("south_north", "west_east"), zero_full)
            var_array = ds["var"]
            var_array.attrs["pyproj_srs"] = pyproj_srs

            tzid = list(df["tzid"])
            if self.season == "DT":
                for tz in tzid:
                    print(tz)
                    name = df.loc[df["tzid"] == tz]
                    timezone = pytz.timezone(tz)
                    # dt = datetime.utcnow()
                    offset = timezone.utcoffset(dt)
                    seconds = offset.total_seconds()
                    if (
                        tz == "America/Whitehorse"
                        or tz == "America/Dawson"
                        or tz == "America/Regina"
                        or tz == "America/Swift_Current"
                        or tz == "America/Phoenix"
                        or tz == "America/Indiana/Indianapolis"
                        # or tz ==  "America/Indiana/Knox"
                        or tz == "America/Indiana/Marengo"
                        or tz == "America/Indiana/Petersburg"
                        # or tz ==  "America/Indiana/Tell_City"
                        or tz == "America/Indiana/Vevay"
                        or tz == "America/Indiana/Vincennes"
                        or tz == "America/Indiana/Winamac"
                    ):
                        hours = int(seconds // 3600) * -1
                    else:
                        # hours = abs(int(seconds // 3600)) - 1
                        hours = int(seconds // 3600) * -1
                    dsr = var_array.salem.roi(shape=name)
                    index = np.where(dsr == dsr)
                    zero_full[index[0], index[1]] = hours
            elif self.season == "ST":
                for tz in tzid:
                    print(tz)
                    name = df.loc[df["tzid"] == tz]
                    timezone = pytz.timezone(tz)
                    # dt = datetime.utcnow()
                    dt = datetime(
                        2023,
                        3,
                        9,
                        0,
                        53,
                        15,
                    )

                    offset = timezone.utcoffset(dt)
                    seconds = offset.total_seconds()
                    # if (
                    #     tz    == "America/Phoenix"
                    #     or tz ==  "America/Indiana/Indianapolis"
                    #     # or tz ==  "America/Indiana/Knox"
                    #     or tz ==  "America/Indiana/Marengo"
                    #     or tz ==  "America/Indiana/Petersburg"
                    #     # or tz ==  "America/Indiana/Tell_City"
                    #     or tz ==  "America/Indiana/Vevay"
                    #     or tz ==  "America/Indiana/Vincennes"
                    #     or tz ==  "America/Indiana/Winamac"
                    # ):
                    #     hours = abs(int(seconds // 3600)) + 1
                    # else:
                    if tz == "America/Whitehorse" or tz == "America/Dawson":
                        hours = abs(int(seconds // 3600)) + 1
                    else:
                        hours = int(seconds // 3600) * -1
                    # print(hours)
                    dsr = var_array.salem.roi(shape=name)
                    index = np.where(dsr == dsr)
                    zero_full[index[0], index[1]] = hours
            else:
                raise ValueError("ERROR: This is not a valid time of year")
            # zero_full[zero_full<=0] = 10
            # zero_full[zero_full>10] = 10
            ds_zones = xr.DataArray(
                zero_full.astype(int), name="Zone", dims=("south_north", "west_east")
            )

            ds_zones = ds_zones.compute()

            ds["ZoneST"] = (("south_north", "west_east"), ds_zones.values)
            ds["ZoneST"].attrs["pyproj_srs"] = pyproj_srs
            # ds1 = ds.sel(west_east=slice(-170, -20), south_north=slice(88, 20))

            ds["ZoneST"].salem.quick_map(cmap="coolwarm")
            ds = ds.drop("var")
            ds.to_netcdf(
                str(data_dir)
                + f"/tzone/tzone-{self.model}-{self.domain}-{self.season}.nc",
                mode="w",
            )

        return

    def static_ds_maker(self):

        filein = str(data_dir) + f"/static/static-vars-{self.model}-{self.domain}.nc"
        if os.path.exists(filein):
            print(f"Static_ds file exists for {self.model} - {self.domain}")
            static_ds = salem.open_xr_dataset(
                str(data_dir) + f"/static/static-vars-{self.model}-{self.domain}.nc"
            )
            print(static_ds)
        else:
            #   print(f"The file '{filein}' does not exist.")
            tzone_ds = salem.open_xr_dataset(
                str(data_dir)
                + f"/tzone/tzone-{self.model}-{self.domain}-{self.season}.nc"
            )
            try:
                model = self.model
                domain = self.domain
                function_mapping = {
                    "wrf": grid_wrf,
                    "eccc": grid_eccc,
                    "ecmwf": grid_ecmwf,
                    "adda": grid_adda,
                }
                selected_function = function_mapping.get(model)
                if selected_function is not None:
                    ds = selected_function(model, domain)
                else:
                    raise ValueError(f"Function from {model} is not found")
                tzone_ds["HGT"] = ds["HGT"].isel(time=0)
                for var in tzone_ds:
                    tzone_ds[var].attrs = tzone_ds.attrs
            except:
                pass

            tzone_ds.to_netcdf(
                str(data_dir) + f"/static/static-vars-{self.model}-{self.domain}.nc",
                mode="w",
            )

        return
