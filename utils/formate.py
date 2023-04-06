#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import json
import salem
import numpy as np
import pandas as pd
import xarray as xr

from utils.diagnostic import solve_RH, solve_TD, solve_W_WD, solve_r_o
from context import data_dir, root_dir


def formate(ds, model, domain):
    with open(str(root_dir) + "/json/rename.json") as f:
        rename = json.load(f)
    var_dict = rename[domain]
    ds = ds.rename(var_dict["dims"])

    domain_grid = salem.open_xr_dataset(str(data_dir) + f"/{model}/{domain}-grid.nc")
    ds["south_north"] = domain_grid["south_north"]
    ds["west_east"] = domain_grid["west_east"]
    ds["XLAT"] = (("south_north", "west_east"), domain_grid["XLAT"].values)
    ds["XLONG"] = (("south_north", "west_east"), domain_grid["XLONG"].values)
    ds = ds.assign_coords({"Time": ("time", ds.time.values)})
    ds = ds.set_coords(["XLAT", "XLONG"])
    ds["time"] = np.arange(0, len(ds.time.values))

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
    if "r_o" not in var_list:
        ds = solve_r_o(ds)

    keep_vars = ["SNOWH", "r_o", "T", "TD", "U10", "V10", "H", "QV", "W", "WD"]
    ds = ds.drop([var for var in list(ds) if var not in keep_vars])
    ds.attrs["pyproj_srs"] = domain_grid.attrs["pyproj_srs"]

    return ds
