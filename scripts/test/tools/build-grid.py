import context
import salem
import json

import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt


from context import data_dir


model = "ecmwf"
domain = "era5-land"


if model == "wrf":
    ds = salem.open_xr_dataset(
        str(data_dir) + f"/{model}/wrfout_{domain}_2021-01-14_00:00:00"
    ).isel(Time=0)
    var = "T2"
    var_array = ds[var]
    ds_grid = ds.salem.grid.to_dataset()
elif model == "eccc":
    ds = salem.open_metum_dataset(str(data_dir) + f"/{model}/{domain}/test.nc")
    ds_grib = xr.open_dataset(
        str(data_dir) + f"/{model}/{domain}/test.grib2", engine="cfgrib"
    )
    var = list(ds_grib)[0]
    proj = ds.attrs["pyproj_srs"]

    try:
        ## This works for HRDPS
        lons = ds.lon.values
        lats = ds.lat.values
        nx, ny = ds_grib[var].attrs["GRIB_Nx"], ds_grib[var].attrs["GRIB_Ny"]
        dx, dy = (
            ds_grib[var].attrs["GRIB_iDirectionIncrementInDegrees"],
            ds_grib[var].attrs["GRIB_jDirectionIncrementInDegrees"],
        )
    except:
        ## This works for RDPS
        lons = ds.lon_1.values
        lats = ds.lat_1.values
        nx, ny = lons.shape[1], lons.shape[0]
        dx, dy = (
            0.09,
            0.09,
        )  # solved by a ratio of the hrdps to rdps's GRIB_iDirectionIncrementInDegrees/2.5km = GRIB_iDirectionIncrementInDegrees/10km

    # dx, dy = 0.0225, 0.0225

    x = [lons[0, 0]]
    y = [lats[0, 0]]

    d = {"lats": y, "lons": x}
    df = pd.DataFrame(data=d)

    gdf = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(df["lons"], df["lats"]),
    ).to_crs(proj)
    gdf["Easting"], gdf["Northing"] = gdf.geometry.x, gdf.geometry.y
    gdf.head()

    ds_grid = salem.Grid(
        nxny=(nx, ny),
        dxdy=(dx, dy),
        x0y0=(gdf["Easting"].values[0], gdf["Northing"].values[0]),
        proj=proj,
    ).to_dataset()
    try:
        var_array = ds.TT.isel(time1=1, level=0)
    except:
        var_array = ds.TT.isel(time=0, height1=0)

elif domain == "era5":
    ds = salem.open_xr_dataset(f"/Volumes/WFRT-Ext23/era5/era5-2020010100.nc").isel(
        time=0
    )
    var = "t2m"
    ds["longitude"] = np.arange(-179.75, 180.25, 0.25)
    var_array = ds[var].roll(longitude=int(len(ds["longitude"]) / 2))
    ds_grid = ds.salem.grid.to_dataset()

elif domain == "era5-land":
    ds = salem.open_xr_dataset(
        f"/Volumes/WFRT-Ext22/ecmwf/era5-land/198912/era5-land-1989122800.nc"
    ).isel(time=0)
    var = "t2m"
    # ds["longitude"] = np.arange(-179.75, 180.25, 0.25)
    # var_array = ds[var].roll(longitude=int(len(ds["longitude"]) / 2))
    var_array = ds[var]
    ds_grid = ds.salem.grid.to_dataset()

else:
    pass

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

ds_grid[var] = (("south_north", "west_east"), var_array.values)
ds_grid[var].attrs["pyproj_srs"] = ds_grid.attrs["pyproj_srs"]
ds_grid[var].salem.quick_map(
    cmap="coolwarm",
    extend="both",
)

ds_grid.to_netcdf(str(data_dir) + f"/{model}/{domain}-grid.nc")
# grid_ds = salem.open_xr_dataset(str(data_dir) + f"/wrf/{domain}-grid.nc")
