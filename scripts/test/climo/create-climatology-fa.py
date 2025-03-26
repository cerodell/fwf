#!/home/crodell/miniforge3/envs/fwx/bin/python

import context
import salem
import dask
import zarr
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import flox
import flox.xarray
from dask.distributed import Client

from dask_jobqueue import SLURMCluster

from utils.compressor import compressor
from utils.climatology import get_daily_files # hour_qunt, concat_ds
from context import root_dir, wrf_dir


# Start time logging
runAll = datetime.now()
print("Start running all: ", runAll)


cluster = SLURMCluster(
    cores=6,
    memory="32GB",
    processes=1,
    walltime="02:00:00",
    log_directory="/home/crodell/fwf/log",
    job_name="fwf_dask_cluster"  # Custom job name
)


print(cluster.job_script())


client = Client(cluster)
print(client)


cluster.scale(6)
# client.wait_for_workers(4)

# # %%
# %%
# --- Set Up Paths ---
wrf_dir = Path(f"{wrf_dir}/cffdrs/fwi")
save_dir = Path(f"{wrf_dir}/climo")
save_dir.mkdir(parents=True, exist_ok=True)

# --- Set Variables (No Change) ---
fwf = True
method = "hourly"
start, stop = "2004-08-01", "2024-07-31"
file_name = (
    str(save_dir)
    + f"/fwi-system-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}.zarr"
)

# %%


# --- Functions (Keeping All) ---
def open_ds(path, vars):
    ds = (
        xr.open_dataset(path, chunks='auto')[vars]
        .drop_vars(["XLAT", "XLONG"])
        
    )
    ds["time"] = ds["Time"]
    try:
        ds = ds.drop_vars("XTIME")
    except:
        pass
    return ds

def concat_ds(pathlist, vars):
    return (
        xr.concat(
            [open_ds(path, vars) for path in pathlist],
            dim="time",
        )
        .convert_calendar("noleap")
    )

def hour_qunt(x):
    """
    function groups time to hourly and solves hourly mean
    """
    quantiles = np.array([0, 1, 5, 10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 95, 96, 97, 98, 99, 99.25, 99.50, 99.75, 99.85, 99.90, 99.95, 99.99, 100])
    x = x.chunk({"time": -1})  # Keep chunking strategy
    return x.groupby("time.hour").quantile(
        quantiles / 100,  # Keep all quantiles
        dim="time",
        skipna=False,
    )



# --- Get All Files (No Change) ---
pathlist, x, y = get_daily_files(wrf_dir, method, start, stop)
# pathlist = pathlist[:365]
grid_ds = salem.open_xr_dataset(pathlist[0])
# var_list = list(grid_ds)  # Keep all variables
var_list = ['S']
# Keep your exact quantiles


# %%
# --- Open, Chunk, and Process Data ---
openT = datetime.now()
print("Opening at: ", openT)
ds = xr.open_mfdataset(
    pathlist,
    # data_vars= "minimal",  # Keep this as "minimal" or "different" to avoid merging conflicts
    parallel=True,
    concat_dim="time",
    combine="nested",  # Explicitly tell xarray to concatenate along `time`
)
#  **Minimal change: apply chunking right away**
# ds = concat_ds(pathlist, var_list)#.chunk({"time": 100, "south_north": 500, "west_east": 500})  
# ds = xr.open_mfdataset(pathlist, data_vars = var_list, parallel=True, concat_dim ='time' )#.chunk({"time": 100, "south_north": 500, "west_east": 500})  
print("Opening Time: ", datetime.now() - openT)
# %%


# %%
# --- Compute Hourly Quantiles (No Change) ---
ds['time'] = ds['Time']
group = datetime.now()
print("Grouping at: ", group)
ds = ds.groupby("time.month").apply(hour_qunt)  # Keeping `apply()` since it's intentional
print("Grouping Time: ", datetime.now() - group)
# %%

# --- Write to Zarr (No Major Change) ---
# drop_vars = ["south_north", "west_east"]  # Adjust if necessary
# ds = ds.drop_vars([var for var in drop_vars if var in ds])

write = datetime.now()
print("Writing at: ", write)

ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
for var in list(ds):
    ds[var].attrs = grid_ds[var].attrs

ds.attrs[
    "description"
] = f"20 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"
# ds = ds.chunk("auto")

#  **Minimal change: Avoids memory overload while writing**
# ds.to_netcdf(file_name, mode="w")
ds.to_zarr(file_name, mode="w")
print("Write Time: ", datetime.now() - write)

print("Run Time: ", datetime.now() - runAll)
# %%
# ds['S'].data.visualize(filename="task_graph_final_compute.png", optimize_graph=True)

# %%


test = xr.open_dataset(file_name)

