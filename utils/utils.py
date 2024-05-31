#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python


import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta

def timer(title, start_time):
    time_diff = datetime.now() - start_time
    # Extract the hours, minutes, and seconds from the time difference
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    seconds = (time_diff.seconds % 3600) % 60
    print(f"{title} time: {hours} hours, {minutes} minutes, {seconds} seconds")
    return
