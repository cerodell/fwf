#!/home/crodell/miniforge3/envs/fwx/bin/python
"""
Test the WRF out data from DTN
"""

import math
import numpy as np
import pandas as pd
import xarray as xr
import logging
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib as    
from context import root_dir  

__author__ = "Christopher Rodell"
__email__ = "crodell@tecnosylva.com"

# ===========================
# Set up logging
# ===========================
client = 'ID_DTN_20_YEAR'
wrf_dir = Path(f"/NASPANGEA2/HISTORICAL_WEATHER/{client}/wrf_sfc_files/")
log_file = root_dir / f'log/wrf_data_check_{client}-test.log'

logging.basicConfig(
    filename=log_file,             # Log file name
    filemode='w',                  # 'w' to overwrite, 'a' to append
    level=logging.INFO,            # Log level (INFO, DEBUG, ERROR, etc.)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
)

# Also print logs to console (optional)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# ===========================
# Main Script
# ===========================

# Define the full date range (hourly frequency)
# date_range = pd.date_range(start='2004-08-01 00:00', end='2024-07-31 23:00', freq='h')
date_range = pd.date_range(start='2013-07-31 00:00', end='2013-08-10 00:00', freq='h')

test = xr.open_dataset(f"{wrf_dir}/2013/wrfsfc_d03_20130806_1900.nc")


for var in ['COSALPHA', 'HGT', 'PBLH', 'PREC_ACC_NC', 'RAINNC', 'SINALPHA', 'SNOWNC', 'SWDOWN', 'UST', 'ZNT']:
    fig = plt.
    test[var].plot()


# Loop through the date range
for dt in date_range:
    # Build expected filename based on the datetime
    year = dt.strftime('%Y')
    month = dt.strftime('%m')
    day = dt.strftime('%d')
    hour_min = dt.strftime('%H%M')  # Format as HHMM

    # Construct the expected file path
    # filename = f'wrfsfc_d03_{year}{month}{day}_{hour_min}.nc'
    # expected_file = wrf_dir / year / month / day / filename

    filename = f'wrfsfc_d03_{year}{month}{day}_{hour_min}.nc'
    expected_file = wrf_dir / year / filename

    # Check if the file exists
    if expected_file.exists():
        # logging.info(f"Found: {filename}")
        print(f"Found: {filename}")
        try:
            # Open NetCDF file
            ds = xr.open_dataset(expected_file, engine='netcdf4').drop_vars(['SNOW', 'SNOWH', 'SNOW_ACC_NC'])#[['T2']]#.chunk('auto')

            # Check for NaN values in 'T2'
            var_list = list(ds)
            var_list = [item for item in var_list if item != "Times"]
            for var in var_list:
                # print(var)
                if ds[var].isnull().any():
                    logging.error(f"Corrupted (NaN detected {var}): {filename}")

                # Ensure all values in 'T2' aren't zero or invalid
                elif ds[var].max().values <= .01:
                    logging.error(f"Corrupted (Invalid {var} values): {filename}")

                # Close dataset after checking
                ds.close()

        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

    else:
        logging.warning(f"Missing: {filename}")

# ===========================
# Finished
# ===========================
logging.info("WRF data check completed successfully.")