#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import salem
import numpy as np
import pandas as pd
import xarray as xr
import dask


def solve_TD(ds):
    """
    Function to calculate dew point temperature (TD) from pressure (p) and specific humidity (qv)
    """
    ## Extract pressure data and specific humidity  from input dataset
    p = ds["P0"]
    qv = ds["QV"]
    ## Set any negative specific humidity values to 0
    qv[qv < 0] = 0
    ## Calculate dew point temperature
    tdc = qv * p / (0.622 + qv)
    td = (243.5 * np.log(tdc) - 440.8) / (19.48 - np.log(tdc))
    ## Assign calculated dew point temperature to new dataset variable
    ds["TD"] = td
    return ds


def solve_RH(ds):
    """
    Function to calculate relative humidity (RH) from dew point temperature (C) and temperature (C)
    """
    ## Extract temperature and dew point temperature data from input dataset
    td = ds["TD"]
    t = ds["T"]
    ## Calculate relative humidity as a percentage using inverted clausius clapeyron
    rh = (
        (6.11 * 10 ** (7.5 * (td / (237.7 + td))))
        / (6.11 * 10 ** (7.5 * (t / (237.7 + t))))
        * 100
    )
    ## Set any RH values above 100 to 100
    rh = xr.where(rh > 100, 100, rh)
    ## Create a new dataset variable for relative humidity and assign calculated values to it
    ds["H"] = rh
    # if (
    #     ds.H.min() > 90
    # ):  # check if any RH values are nonphysical (i.e., less than 0 or greater than 100)
    #     raise ValueError(
    #         "ERROR: Check TD nonphysical RH values"
    #     )  # if so, raise a value error with a warning message
    return ds


def solve_W_WD(ds):
    ## Define the latitude and longitude arrays in degrees
    lons_rad = dask.array.deg2rad(ds["XLONG"])
    lats_rad = dask.array.deg2rad(ds["XLAT"])

    ## Calculate rotation angle
    theta = dask.array.arctan2(
        dask.array.cos(lats_rad) * dask.array.sin(lons_rad), dask.array.sin(lats_rad)
    )

    ## Calculate sine and cosine of rotation angle
    sin_theta = dask.array.sin(theta)
    cos_theta = dask.array.cos(theta)

    ## Define the u and v wind components in domain coordinates
    u_domain = ds["U10"]
    v_domain = ds["V10"]

    ## Rotate the u and v wind components to Earth coordinates
    u_earth = u_domain * cos_theta - v_domain * sin_theta
    v_earth = u_domain * sin_theta + v_domain * cos_theta

    ## Solve for wind speed
    wsp = dask.array.sqrt(u_earth ** 2 + v_earth ** 2)
    ds["W"] = wsp

    ## Solve for wind direction on Earth coordinates
    wdir = 180 + ((180 / np.pi) * dask.array.arctan2(u_earth, v_earth))
    ds["WD"] = wdir

    # ## Define the latitude and longitude arrays in degrees
    # lons_rad = np.deg2rad(ds["XLONG"])
    # lats_rad = np.deg2rad(ds["XLAT"])

    # ## Calculate rotation angle
    # theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

    # ## Calculate sine and cosine of rotation angle
    # sin_theta = np.sin(theta)
    # cos_theta = np.cos(theta)

    # ## Define the u and v wind components in domain coordinates
    # u_domain = ds["U10"]
    # v_domain = ds["V10"]

    # ## Rotate the u and v wind components to Earth coordinates
    # u_earth = u_domain * cos_theta - v_domain * sin_theta
    # v_earth = u_domain * sin_theta + v_domain * cos_theta

    # ## Solve for wind speed
    # wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
    # ds["W"] = wsp

    # ## Solve for wind direction on Earth coordinates
    # wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
    # ds["WD"] = wdir

    return ds


def solve_r_o(ds):
    try:
        ds["r_o_hourly"] = xr.where(ds["r_o_hourly"] < 0, 0, ds["r_o_hourly"])
        r_oi = ds["r_o_hourly"].values
        r_accumulated_list = []
        for i in range(len(ds.time)):
            r_hour = np.sum(r_oi[:i], axis=0)
            r_accumulated_list.append(r_hour)
        r_o = np.stack(r_accumulated_list)
        r_o = xr.DataArray(r_o, name="r_o", dims=("time", "south_north", "west_east"))
        ds["r_o"] = r_o
        ds["r_o"] = ds.r_o - ds.r_o.isel(time=0)
        ds = ds.chunk("auto")
    except:
        pass
    return ds
