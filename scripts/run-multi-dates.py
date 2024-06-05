#!/bluesky/fireweather/miniconda3/envs/fwx/bin/python

"""
Runs the FWF model for over user defined dates
"""

import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, timedelta
from utils.wrf_ import read_wrf
from utils.eccc import read_eccc
from utils.era5 import read_era5
from utils.utils import timer

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF


import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)
#  0:01:47.
date_range = pd.date_range("2024-06-04", "2024-06-04")
# date_range = pd.date_range("2021-01-02", "2021-01-05")
# date_range = pd.date_range("2021-01-01", "2021-01-01")



domains = ["d02","d03"]
for doi in date_range:
    for domain in domains:
        domain_startTime = datetime.now()
        print(f"start of domain {domain}: ", str(domain_startTime))
        config = dict(
            model="wrf",
            initialize=False,
            initialize_hffmc=False,
            overwinter=False,
            fbp_mode=True,
            frp_mode=True,
            correctbias=False,
        )
        config["doi"] = doi
        config['domain'] = domain
        coeff = FWF(
            config=config,
        )
        coeff.daily()
        coeff.hourly()
        timer(f"Domain {domain} run ", domain_startTime)

### Timer
timer("Total Run ", startTime)
print("RUN ENDED: ", str(datetime.now()))
### Timer
print("Total Run Time: ", datetime.now() - startTime)
