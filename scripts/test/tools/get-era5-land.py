#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import cdsapi
import pandas as pd
from datetime import datetime
from pathlib import Path


c = cdsapi.Client()
save_dir = "/Volumes/WFRT-Ext25/ecmwf/era5-land/"
# date_range = pd.date_range("2013-02-12", "2019-12-27")
# date_range = pd.date_range("2017-02-18", "2020-01-01")
date_range = pd.date_range("2023-01-01", "2024-01-01")
for date in date_range:
    startTime = datetime.now()
    make_dir = Path(str(save_dir) + f"/{date.strftime('%Y%m')}")
    make_dir.mkdir(parents=True, exist_ok=True)
    c.retrieve(
        "reanalysis-era5-land",
        {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": [
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "2m_dewpoint_temperature",
                "2m_temperature",
                "snow_depth",
                "total_precipitation",
                "potential_evaporation",
            ],
            "area": [
                86,
                -180,
                15,
                -25,
            ],
            "year": date.strftime("%Y"),
            "month": date.strftime("%m"),
            "day": date.strftime("%d"),
            "time": [
                "00:00",
                "01:00",
                "02:00",
                "03:00",
                "04:00",
                "05:00",
                "06:00",
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
                "19:00",
                "20:00",
                "21:00",
                "22:00",
                "23:00",
            ],
        },
        str(make_dir) + f'/era5-land-{date.strftime("%Y%m%d00")}.nc',
    )

    print(
        f'downloaded era5-land-{date.strftime("%Y%m%d00")}.nc in {datetime.now() - startTime}'
    )
