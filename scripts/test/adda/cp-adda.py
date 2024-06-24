#!/Users/crodell/miniconda3/envs/fwx/bin/python

import context
import os
import json
import joblib
import logging
import salem
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path


from pathlib import Path
import shutil
import subprocess


# ds = salem.open_xr_dataset('/Volumes/WFRT-Ext21/fwf-data/adda/d01/01/fwf-hourly-d01-2005022300.zarr')
# Define the directory and pattern
# directory = "/Volumes/ThunderBay/CRodell/ADDA_V2/2005"
directory = "/Volumes/WFRT-Ext20/ADDA_V2/2006"
old_date = "2006-05-30_20"
new_date = "2006-05-30_21"
pattern = f"cstm_d01_{old_date}_*"

# Use glob to match the pattern and then sort the list of files
file_list = sorted(Path(directory).glob(pattern))

# Copy files with new names using a bash command
for file in file_list:
    # Create the new filename by replacing the old date with the new date
    new_file_name = str(file).replace(old_date, new_date)

    # Run the bash command to copy the file
    subprocess.run(["cp", str(file), new_file_name])
    print(f"Copied {file} to {new_file_name}")


directory = "/Volumes/WFRT-Ext20/ADDA_V2/TD2/2006"
old_date = "2006-11-23_08"
new_date = "2006-11-23_09"
pattern = f"TD2_{old_date}*"

# Use glob to match the pattern and then sort the list of files
file_list = sorted(Path(directory).glob(pattern))

# Copy files with new names using a bash command
for file in file_list:
    # Create the new filename by replacing the old date with the new date
    new_file_name = str(file).replace(old_date, new_date)

    # Run the bash command to copy the file
    subprocess.run(["cp", str(file), new_file_name])
    print(f"Copied {file} to {new_file_name}")

# Missing all TD2 on:  2006-05-16_07
# Missing all TD2 on:  2006-05-30_21
# Missing all TD2 on:  2006-11-23_09

# date_range = pd.date_range('2006-01-01', "2007-01-01", freq='h')
# directory = '/Volumes/WFRT-Ext20/ADDA_V2/'

# for doi in date_range:
#     year_dir = Path(directory) / doi.strftime("%Y")
#     file_pattern = f'cstm_d01_{doi.strftime("%Y-%m-%d_%H")}*'

#     # Debugging print statements
#     # print(f'Checking directory: {year_dir}')
#     # print(f'Using pattern: {file_pattern}')

#     files = list(year_dir.glob(file_pattern))

#     # Debugging print statements
#     # print(f'Found files: {files}')

#     if not files:
#         print('Missing all vars on:', doi.strftime("%Y-%m-%d_%H"))

# # Additional check to see if the directory and files are correct
# if not year_dir.exists():
#     print(f"Directory does not exist: {year_dir}")

# for doi in date_range:
#   if os.path.exists(f'/Volumes/WFRT-Ext20/ADDA_V2/TD2/{doi.strftime("%Y")}/TD2_{doi.strftime("%Y-%m-%d_%H")}.nc'):
#     pass
#   else:
#     print('Missing all TD2 on: ', doi.strftime("%Y-%m-%d_%H"))
