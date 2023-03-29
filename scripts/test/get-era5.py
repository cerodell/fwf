#!/Users/crodell/miniconda3/envs/fwf/bin/python

import context
import cdsapi
import pandas as pd
from datetime import datetime


c = cdsapi.Client()
save_dir = "/Volumes/WFRT-Ext23/era5/"
date_range = pd.date_range("2019-12-27", "2021-01-01")

for date in date_range:
    startTime = datetime.now()
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": [
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "2m_dewpoint_temperature",
                "2m_temperature",
                "mean_sea_level_pressure",
                "snow_depth",
                "total_precipitation",
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
        save_dir + f'era5-{date.strftime("%Y%m%d00")}.nc',
    )

    print(
        f'downloaded era5-{date.strftime("%Y%m%d00")}.nc in {datetime.now() - startTime}'
    )
