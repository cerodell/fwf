#!/Users/crodell/miniconda3/envs/fwf/bin/python

"""
Defines Projection of ECCC Data and matches the variable naming convention used in the FWF class
"""

import context
import salem
import json

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
import geopandas as gpd

from context import data_dir, root_dir


## open domain config file with variable names and attributes
with open(str(root_dir) + "/json/config.json") as f:
    config = json.load(f)


def read_eccc(domain, doi, write=False):

    filein = f"/Volumes/WFRT-Ext24/ECCC/{domain}/{doi.strftime('%Y%m')}/"
    pathlist = sorted(Path(filein).glob(doi.strftime("%Y%m%d00*")))
    fwf_ds = units_eccc(
        xr.concat([open_eccc(path, domain) for path in pathlist], dim="time")
    )

    return fwf_ds


def solve_TD(ds):
    p = ds["P0"].values  # *.01
    qv = ds["QV"].values
    qv[qv < 0] = 0
    tdc = qv * p / (0.622 + qv)
    td = (243.5 * np.log(tdc) - 440.8) / (19.48 - np.log(tdc))
    ds["TD"] = (("south_north", "west_east"), td)
    return ds


def solve_RH(ds):
    TD = ds["TD"].values
    T = ds["T"].values
    RH = (
        (6.11 * 10 ** (7.5 * (TD / (237.7 + TD))))
        / (6.11 * 10 ** (7.5 * (T / (237.7 + T))))
        * 100
    )
    RH = xr.where(RH > 100, 100, RH)
    ds["H"] = (("south_north", "west_east"), RH)
    if np.min(ds.H) > 90:
        raise ValueError("ERROR: Check TD unphysical RH values")
    return ds


def rename_vars(ds, domain):
    var_dict = config[domain]
    var_list = list(ds)
    for key in list(var_dict.keys()):
        # Check if the key is not in the list of valid keys
        if key not in var_list:
            # Remove the key from the dictionary
            del var_dict[key]
    ds = ds.rename(var_dict)
    ds = ds.rename(
        {
            "rlon": "west_east",
            "rlat": "south_north",
        }
    )
    var_list = list(ds)
    if "TD" not in var_list:
        ds = solve_TD(ds)
    if "H" not in var_list:
        ds = solve_RH(ds)
    if "SNOWH" not in var_list:
        ds["SNOWH"] = (("south_north", "west_east"), np.zeros_like(ds["T"].values))
    ds = ds.chunk("auto")
    return ds


def open_eccc(path, domain):
    if domain == "rdps":
        ds = xr.open_dataset(path, chunks="auto").isel(height1=0, height2=0, sfctype=0)
        ds = ds.rename(config[domain])
    elif domain == "hrdps":
        ds = xr.open_dataset(path, chunks="auto")
        dim_list = list(ds.dims)
        dim_dict = {
            "time": -1,
            "level": 0,
            "height1": 0,
            "height2": 0,
            "sfctype": 0,
            "time1": -1,
            "time2": -1,
            "height": 0,
        }
        for key in list(dim_dict.keys()):
            # Check if the key is not in the list of valid keys
            if key not in dim_list:
                # Remove the key from the dictionary
                del dim_dict[key]
        ds = rename_vars(ds.isel(dim_dict), domain)
        if "time" in list(dim_dict):
            ds = ds.assign_coords(time=ds.time.values)
        elif "time2" in list(dim_dict):
            ds = ds.assign_coords(time=ds.time2.values)
        ds = ds.expand_dims(dim="time")
    else:
        raise ValueError(f"Invalid domain option: {domain} \n Try rdps or hrdps")

    keep_vars = ["SNOWH", "r_o", "T", "TD", "U10", "V10", "H", "QV"]
    ds = ds.drop([var for var in list(ds) if var not in keep_vars])
    ds = config_eccc(ds, domain, keep_vars)
    return ds


def config_eccc(ds, domain, keep_vars):
    if domain == "rdps":
        domain_grid1 = salem.open_xr_dataset(str(data_dir) + f"/eccc/{domain}-grid1.nc")
        domain_grid2 = salem.open_xr_dataset(str(data_dir) + f"/eccc/{domain}-grid2.nc")
    elif domain == "hrdps":
        domain_grid = salem.open_xr_dataset(str(data_dir) + f"/eccc/{domain}-grid.nc")
    else:
        raise ValueError(f"Invalid domain option: {domain} \n Try rdps or hrdps")

    if domain == "rdps":
        domain_grid2["r_o"] = (("time", "south_north", "west_east"), ds["r_o"].values)
        domain_grid2["r_o"].attrs["pyproj_srs"] = domain_grid2.attrs["pyproj_srs"]

        domain_grid2["SNOWH"] = (
            ("time", "south_north", "west_east"),
            ds["SNOWH"].values,
        )
        domain_grid2["SNOWH"].attrs["pyproj_srs"] = domain_grid2.attrs["pyproj_srs"]

        fwf_ds = domain_grid1.salem.transform(domain_grid2)

        fwf_ds["XLAT"] = (("south_north", "west_east"), domain_grid1["XLAT"].values)
        fwf_ds["XLONG"] = (("south_north", "west_east"), domain_grid1["XLONG"].values)

        for var in keep_vars[2:]:
            fwf_ds[var] = (("time", "south_north", "west_east"), ds[var].values)
            fwf_ds[var].attrs["pyproj_srs"] = fwf_ds.attrs["pyproj_srs"]

    elif domain == "hrdps":
        fwf_ds = domain_grid
        for var in keep_vars:
            fwf_ds[var] = (("time", "south_north", "west_east"), ds[var].values)
            fwf_ds[var].attrs["pyproj_srs"] = fwf_ds.attrs["pyproj_srs"]
    else:
        raise ValueError(f"Invalid domain option: {domain} \n Try rdps or hrdps")

    fwf_ds = fwf_ds.assign_coords({"Time": ("time", ds.time.values)})
    fwf_ds = fwf_ds.set_coords(["XLAT", "XLONG"])
    print(ds.time.values)
    return fwf_ds


def units_eccc(ds):

    ## Convert from m to mm
    ds["r_o"] = ds["r_o"] * 1000

    ## Convert from knots to km hr^-1
    ds["U10"] = ds["U10"] * 1.852
    ds["U10"] = ds["U10"] * 1.852

    # Define the latitude and longitude arrays in degrees
    lons_rad = np.deg2rad(ds["XLONG"].values)
    lats_rad = np.deg2rad(ds["XLAT"].values)

    ## Calculate rotation angle
    theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

    ## Calculate sine and cosine of rotation angle
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    ## Define the u and v wind components in domain coordinates
    u_domain = ds["U10"].values
    v_domain = ds["V10"].values

    ## Rotate the u and v wind components to Earth coordinates
    u_earth = u_domain * cos_theta - v_domain * sin_theta
    v_earth = u_domain * sin_theta + v_domain * cos_theta

    ## Solve for wind speed
    wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
    ds["W"] = (("time", "south_north", "west_east"), wsp)

    ## Solve for wind direction on Earth coordinates
    wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
    ds["WD"] = (("time", "south_north", "west_east"), wdir)

    for var in ["r_o", "U10", "V10", "W", "WD"]:
        ds[var].attrs["pyproj_srs"] = ds.attrs["pyproj_srs"]

    return ds


def grid_eccc(domain):
    ## open with salem's metum, which defines the py projection
    ds = salem.open_metum_dataset(str(data_dir) + f"/eccc/{domain}/test.nc")
    ds_grib = xr.open_dataset(
        str(data_dir) + f"/eccc/{domain}/test.grib2", engine="cfgrib"
    )
    var = list(ds_grib)[0]

    ## get py projection as str
    proj = ds.attrs["pyproj_srs"]

    ## get domains rotated lat and lon and attributes
    try:
        lons = ds.lon.values
        lats = ds.lat.values
        nx, ny = ds_grib[var].attrs["GRIB_Nx"], ds_grib[var].attrs["GRIB_Ny"]
        dx, dy = (
            ds_grib[var].attrs["GRIB_iDirectionIncrementInDegrees"],
            ds_grib[var].attrs["GRIB_jDirectionIncrementInDegrees"],
        )
    except:
        lons = ds.lon_1.values
        lats = ds.lat_1.values
        nx, ny = lons.shape[1], lons.shape[0]
        dx, dy = (
            0.09,
            0.09,
        )  # solved by a ratio of the hrdps to rdps's GRIB_iDirectionIncrementInDegrees/2.5km = GRIB_iDirectionIncrementInDegrees/10km

    ## get domain lower left corner as lat and lon
    x = [lons[0, 0]]
    y = [lats[0, 0]]

    ## make a dataframe of domain's lower left corner as lat and lon
    d = {"lats": y, "lons": x}
    df = pd.DataFrame(data=d)

    ## transform lat and lon cords from a lat-lon grid to eccc grid
    gdf = gpd.GeoDataFrame(
        df,
        crs="EPSG:4326",
        geometry=gpd.points_from_xy(df["lons"], df["lats"]),
    ).to_crs(proj)
    gdf["Easting"], gdf["Northing"] = gdf.geometry.x, gdf.geometry.y
    # gdf.head()

    ## make grid with associated py projection
    domain_grid = salem.Grid(
        nxny=(nx, ny),
        dxdy=(dx, dy),
        x0y0=(gdf["Easting"].values[0], gdf["Northing"].values[0]),
        proj=proj,
    ).to_dataset()

    lon, lat = domain_grid.salem.grid.ll_coordinates

    domain_grid["XLAT"] = (("south_north", "west_east"), lon)
    domain_grid["XLONG"] = (("south_north", "west_east"), lat)
    domain_grid = domain_grid.set_coords(["XLAT", "XLONG"])
    domain_grid = domain_grid.rename_dims(
        {
            "x": "west_east",
            "y": "south_north",
        }
    )
    domain_grid = domain_grid.rename(
        {
            "x": "west_east",
            "y": "south_north",
        }
    )
    domain_grid.to_netcdf(str(data_dir) + f"/eccc/{domain}-grid.nc", mode="w")

    return domain_grid
