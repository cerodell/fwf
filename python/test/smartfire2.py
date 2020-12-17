import context
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from netCDF4 import Dataset
import cartopy.crs as crs


from datetime import datetime
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from datetime import datetime, date, timedelta
from context import data_dir, root_dir

startTime = datetime.now()


### Get All Stations CSV


### Open fire emissions
filein = str(data_dir) + str("/2020080508/fire_emissions.csv") 
df_emissions = pd.read_csv(filein)

### Open fire events
filein = str(data_dir) + str("/2020080508/fire_events.csv") 
df_events = pd.read_csv(filein)

### Open fire locations
filein = str(data_dir) + str("/2020080508/fire_locations.csv") 
df_locations = pd.read_csv(filein)
