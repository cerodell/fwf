#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import salem
import numpy as np
import pandas as pd
import xarray as xr


def solve_TD(ds):
    p = ds["P0"]
    qv = ds["QV"]
    qv[qv < 0] = 0
    tdc = qv * p / (0.622 + qv)
    td = (243.5 * np.log(tdc) - 440.8) / (19.48 - np.log(tdc))
    ds["TD"] = (("south_north", "west_east"), td)
    ds["TD"] = td
    return ds


def solve_RH(ds):
    td = ds["TD"]
    t = ds["T"]
    rh = (
        (6.11 * 10 ** (7.5 * (td / (237.7 + td))))
        / (6.11 * 10 ** (7.5 * (t / (237.7 + t))))
        * 100
    )
    rh = xr.where(rh > 100, 100, rh)
    ds["H"] = rh
    if np.min(ds.H) > 90:
        raise ValueError("ERROR: Check TD nonphysical RH values")
    return ds


def solve_W_WD(ds):

    # Define the latitude and longitude arrays in degrees
    lons_rad = np.deg2rad(ds["XLONG"])
    lats_rad = np.deg2rad(ds["XLAT"])

    ## Calculate rotation angle
    theta = np.arctan2(np.cos(lats_rad) * np.sin(lons_rad), np.sin(lats_rad))

    ## Calculate sine and cosine of rotation angle
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    ## Define the u and v wind components in domain coordinates
    u_domain = ds["U10"]
    v_domain = ds["V10"]

    ## Rotate the u and v wind components to Earth coordinates
    u_earth = u_domain * cos_theta - v_domain * sin_theta
    v_earth = u_domain * sin_theta + v_domain * cos_theta

    ## Solve for wind speed
    wsp = np.sqrt(u_earth ** 2 + v_earth ** 2)
    ds["W"] = wsp

    ## Solve for wind direction on Earth coordinates
    wdir = 180 + ((180 / np.pi) * np.arctan2(u_earth, v_earth))
    ds["WD"] = wdir

    return ds
