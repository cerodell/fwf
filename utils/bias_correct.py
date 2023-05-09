#!/Users/crodell/miniconda3/envs/fwf/bin/python


import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
from datetime import datetime
from context import data_dir


""" ####################################################################### """
""" #########################  Bias Correct WRF  ########################## """


def bias_correct(ds, domain, config):
    """

    Parameters
    ----------

    ds: Dataset
        - Xarray dataset of WRF Forecast
    domain: str
        - Domain tag of wrf model

    Returns
    -------

    """
    try:
        doi = pd.to_datetime(str(ds.Time.values[0] - np.timedelta64(1, "D"))).strftime(
            "%Y%m%d"
        )
    except:
        doi = pd.to_datetime(str(ds.Time.values - np.timedelta64(1, "D"))).strftime(
            "%Y%m%d"
        )

    print(f"Bias correcting forecast from kriged observations on {doi}")

    if (config == "WRF07") or (config == "WRF03"):
        krig_type = "ok"
        print(f"Bias correcting with kring method {krig_type}")
    elif config == "WRF08":
        krig_type = "uk"
        print(f"Bias correcting with kring method {krig_type}")
    else:
        raise ValueError("Invlid confg to test kriging")

    bias_ds = xr.open_dataset(
        f"/Volumes/WFRT-Data02/FWF-WAN00CG/{domain}/krig-bias-{krig_type}/fwf-krig-d02-{doi}.nc"
    )

    # print(ds['T'].max())
    print("Max T Bias ", float(bias_ds["T_bias"].max()))
    print("Min T Bias ", float(bias_ds["T_bias"].min()))
    print("Max TD Bias ", float(bias_ds["TD_bias"].max()))
    print("Min TD Bias ", float(bias_ds["TD_bias"].min()))
    ## bias correct forecast
    ds["T"] = ds["T"] - bias_ds["T_bias"].values
    ds["TD"] = ds["TD"] - bias_ds["TD_bias"].values

    print(float(ds["T"].max()))

    RH = (
        (6.11 * 10 ** (7.5 * (ds.TD / (237.7 + ds.TD))))
        / (6.11 * 10 ** (7.5 * (ds.T / (237.7 + ds.T))))
        * 100
    )
    RH = xr.where(RH > 100, 100, RH)
    RH = xr.DataArray(RH, name="H", dims=("time", "south_north", "west_east"))
    ds["H"] = RH
    if np.min(ds.H) > 90:
        raise ValueError("ERROR: nonphysical RH values")

    if np.min(ds.T) > 90:
        raise ValueError("ERROR: nonphysical T values")

    if (np.max(ds.T) > 100) | (np.min(ds.T) < -100):
        raise ValueError("ERROR: nonphysical T values")

    if (np.max(ds.TD) > 100) | (np.min(ds.TD) < -100):
        raise ValueError("ERROR: nonphysical TD values")

    return ds
