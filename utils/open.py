#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import os
import json
import numpy as np
import pandas as pd
import xarray as xr


from datetime import datetime
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from utils.era5 import read_era5

from context import data_dir


__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"


def read_dataset(config):
    if config["model"] == "eccc":
        int_ds = read_eccc(config["doi"], config["model"], config["domain"])
    elif config["model"] == "ecmwf":
        int_ds = read_era5(config["doi"], config["model"], config["domain"])
    elif config["model"] == "wrf":
        int_ds = read_wrf(config["doi"], config["model"], config["domain"])
    else:
        raise ValueError(
            f"Invalided config, issue is likely the date, model or domain supplied. \n \n {config}"
        )

    ############ Remove unwanted variables from int_ds ############
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
        "Df",
        "r_w",
        "dFS",
        "FS_days",
        "FS",
        "TMAX",
    ]
    int_ds = int_ds.drop([var for var in list(int_ds) if var not in keep_vars])

    return int_ds
