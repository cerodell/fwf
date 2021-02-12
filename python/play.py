import numpy as np
import xarray as xr


filein = "/bluesky/fireweather/fwf/data/FWF-WAN00CG-01/fwf-hourly-d03-2021021106.zarr"

ds = xr.open_zarr(filein)
