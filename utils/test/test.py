import context
import math
import json
import numpy as np
import pandas as pd
import xarray as xr


s = "/Volumes/WFRT-Data02/era5"
if s.find("era"):
    print("No 'is' here!")
else:
    print("Found 'is' in the string.")
