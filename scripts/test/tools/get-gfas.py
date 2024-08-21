#!/Users/crodell/miniconda3/envs/fwf/bin/python

import cdsapi

c = cdsapi.Client()

c.retrieve(
    "cams-global-fire-emissions-gfas",
    {
        "format": "netcdf",
        "variable": "wildfire_radiative_power",
        "date": "2024-07-11/2024-07-11",
    },
    "download.nc",
)
