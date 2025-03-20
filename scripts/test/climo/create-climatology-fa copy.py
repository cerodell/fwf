#!/Users/crodell/miniconda3/envs/fwx/bin/python

import os
import json
import context
import salem
import dask
import zarr
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
from numcodecs.blosc import Blosc
import flox
import flox.xarray
from dask.distributed import LocalCluster, Client
from dask_jobqueue import SLURMCluster

from utils.compressor import compressor
from utils.climatology import get_daily_files, hour_qunt, concat_ds
from context import root_dir, wrf_dir

## https://stackoverflow.com/questions/49620140/get-hourly-average-for-each-month-from-a-netcds-file


runAll = datetime.now()
print("Start running all: ", runAll)

if __name__ == "__main__":
    cluster = SLURMCluster(
        queue="your_partition",  # Change to your SLURM partition name
        cores=4,  # Adjust based on your job request
        memory="16GB",  # Memory per worker
        processes=1,  # One process per worker (avoid thread issues)
        walltime="01:00:00",  # Match your SLURM job time
        job_extra_directives=["--exclusive"],  # Ensures exclusive use of nodes (optional)
    )

    # Request workers from SLURM
    cluster.scale(jobs=2)  # Request 2 SLURM jobs (adjust as needed)

    # Connect the Dask client
    client = Client(cluster)

    print(client)  # Verify cluster is running


    wrf_dir = Path(f"{wrf_dir}/cffdrs/fwi")
    save_dir = Path(f"{wrf_dir}/climo")
    save_dir.mkdir(parents=True, exist_ok=True)


    # var = "S"
    fwf = True
    method = "hourly"
    start = "2004-08-01"
    stop = "2024-07-31"



    file_name = (
        str(save_dir)
        + f"/fwi-system-{method}-climatology-{start.replace('-','')}-{stop.replace('-','')}.zarr"
    )
    ds_climo = xr.open_zarr(file_name)

    # ds_climo['S'].isel(month =7, quantile =-1).plot(vmax = 200)
    # ds_climo['S'].isel(month =7, quantile =-1, hour =22).plot(vmax = 200)


    ## get all files for era5-land of fwf
    pathlist, x, y = get_daily_files(wrf_dir, method, start, stop)

    # pathlist = pathlist[:365*2]
    grid_ds = salem.open_xr_dataset(pathlist[0])
    var_list = list(grid_ds)#[:-2]

    quantiles = np.array([0, 1, 5, 10, 20, 30, 40, 50, 60, 70, 75, 80, 85, 90, 95, 96, 97, 98, 99, 99.25, 99.50, 99.75, 99.85, 99.90, 99.95, 99.99, 100 ])



    def open_ds(path, vars):
        ds = (
            xr.open_dataset(path)[vars]
            .drop_vars(["XLAT", "XLONG"])
            .chunk("auto")
            # .chunk(chunks={y: 237, x: 517})
        )
        # ds["time"] = [ds["Time"].values]
        # try:
        ds["time"] = ds["Time"]
        # except:
        #     ds["time"] = [ds["Time"].values]
        # ds = ds.drop_vars("Time")
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

    # def hour_qunt(x):
    #     """
    #     function groups time to hourly and solves hourly mean

    #     """
    #     # x = rechunk(x)
    #     x = x.chunk({"time": -1})
    #     return x.quantile(
    #         quantiles/100,
    #         dim="time",
    #         skipna=False,
    #     )

    def hour_qunt(x):
        """
        function groups time to hourly and solves hourly mean

        """
        # x = rechunk(x)
        x = x.chunk({"time": -1})
        return x.groupby("time.hour").quantile(
            quantiles/100,
            dim="time",
            skipna=False,
        )


    ## open =, chunk and combine into single dask chunk dataset
    openT = datetime.now()
    print("Opening at: ", openT)
    ds = concat_ds(pathlist, var_list)
    print("Opening Time: ", datetime.now() - openT)

    group = datetime.now()
    print("Grouping at: ", group)
    ds = ds.groupby("time.month").apply(hour_qunt)
    print("Grouping Time: ", datetime.now() - group)

    print(ds)
    # dask.visualize(ds)
    # Add some dataset attributes
    ds.attrs["pyproj_srs"] = grid_ds.attrs["pyproj_srs"]
    for var in list(ds):
        ds[var].attrs = grid_ds[var].attrs
    ds.attrs[
        "description"
    ] = f"20 year ({start.replace('-','')}-{stop.replace('-','')}) climatology"
    ds = ds.chunk("auto")


    # compressor = Blosc(cname="zstd", clevel=3, shuffle=2)
    write = datetime.now()
    print("Writing at: ", write)
    ds.to_zarr(
        file_name,
        mode="w",
        # encoding={x: {"compressor": compressor} for x in ds},
    )
    print("Write Time: ", datetime.now() - write)

    print("Run Time: ", datetime.now() - runAll)
