#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr

from utils.diagnostic import solve_RH, solve_TD, solve_W_WD
from context import data_dir, root_dir


## open domain config file with variable names and attributes
with open(str(root_dir) + "/json/config.json") as f:
    config = json.load(f)


def formate(ds, domain):
    var_dict = config[domain]
    ds = ds.rename(var_dict["dims"])
    var_list = list(ds)
    for key in list(var_dict.keys()):
        # Check if the key is not in the list of valid keys
        if key not in var_list:
            # Remove the key from the dictionary
            del var_dict[key]
    ds = ds.rename(var_dict)
    var_list = list(ds)
    if "TD" not in var_list:
        ds = solve_TD(ds)
    if "H" not in var_list:
        ds = solve_RH(ds)
    if "WD" not in var_list:
        ds = solve_W_WD(ds)
    if "SNOWH" not in var_list:
        ds["SNOWH"] = ds["T"] * 0
    return ds
