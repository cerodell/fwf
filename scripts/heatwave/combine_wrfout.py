import context
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import cartopy.crs as crs
from cartopy.feature import NaturalEarthFeature
from datetime import datetime

from context import wrf_dir, root_dir

import wrf
from wrf import (
    getvar,
    interplevel,
    to_np,
    latlon_coords,
    get_cartopy,
    cartopy_xlim,
    cartopy_ylim,
    omp_set_num_threads,
)

# Open the NetCDF file
domain = "d03"
pathlist = np.array(
    [
        sorted(Path(str(wrf_dir) + f"/2106{i}00/").glob(f"wrfout_{domain}_*00"))[6:30]
        for i in range(25, 31)
    ]
).ravel()


def read_netcdfs(paths, dim):
    omp_set_num_threads(4)

    def process_one_path(path):
        print(path)
        ncfile = Dataset(path)
        slp = getvar(ncfile, "slp", units="hPa")
        p = getvar(ncfile, "pressure")
        z = getvar(ncfile, "z", units="dm")
        T2 = getvar(ncfile, "T2")
        td2 = getvar(ncfile, "td2", units="K")
        temp = getvar(ncfile, "temp", units="K")
        td = getvar(ncfile, "td", units="K")
        ter = getvar(ncfile, "ter", units="m")
        th = getvar(ncfile, "th", units="K")
        ua = getvar(ncfile, "ua", units="m s-1")
        va = getvar(ncfile, "va", units="m s-1")
        uvmet10 = getvar(ncfile, "uvmet10", units="m s-1")
        del uvmet10["u_v"]
        wspd = getvar(ncfile, "wspd_wdir", units="m s-1")[0, :]
        del wspd["wspd_wdir"]
        wspd10 = getvar(ncfile, "wspd_wdir10", units="m s-1")[0, :]
        del wspd10["wspd_wdir"]

        ds = xr.merge(
            [slp, p, z, T2, td2, temp, td, ter, th, ua, va, uvmet10, wspd, wspd10]
        )
        ds.load()
        return ds

    datasets = [process_one_path(p) for p in paths]
    combined = xr.concat(datasets, dim)
    return combined


ds = read_netcdfs(pathlist[0::6], dim="Time")


## Interpolate geopotential height, u, and v winds to 500 hPa


def interplevel_rename(ds, level):
    ht_interp = interplevel(ds.height, ds.pressure, level)
    ds[str(ht_interp.name) + f"_{level}"] = ht_interp

    u_interp = interplevel(ds.ua, ds.pressure, level)
    ds[str(u_interp.name) + f"_{level}"] = u_interp

    v_interp = interplevel(ds.va, ds.pressure, level)
    ds[str(v_interp.name) + f"_{level}"] = v_interp

    wspd_interp = interplevel(ds.wspd_wdir, ds.pressure, level)
    ds[str(wspd_interp.name) + f"_{level}"] = wspd_interp

    return ds


for level in [925, 850, 700, 500, 250]:
    ds = interplevel_rename(ds, level)

times = np.array(ds.Time.dt.strftime("%Y-%m-%dT%H"))
int_time = datetime.strptime(str(times[0]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")
end_time = datetime.strptime(str(times[-1]), "%Y-%m-%dT%H").strftime("%Y%m%d%H")

for var in list(ds):
    ds[var].encoding = {}
    ds[var].attrs["projection"] = str(ds[var].attrs["projection"])


ds.to_netcdf(
    str(root_dir) + f"/data/heatwave/wrfout_{domain}_{int_time}_{end_time}.nc", mode="w"
)
