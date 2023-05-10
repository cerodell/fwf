#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Runs the FWF model for each model domain.
Saves dataset as nc file containing all fwi/fbp and associated met products

"""
import context
import math
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path

from datetime import datetime, date, timedelta

startTime = datetime.now()
print("RUN STARTED AT: ", str(startTime))

from utils.fwf import FWF
from context import wrf_dir
import warnings

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# ignore RuntimeWarning
warnings.filterwarnings("ignore", category=RuntimeWarning)

# """######### create forecast directory for webapge  #############"""
doi = pd.Timestamp("today")
make_dir = Path(f'/bluesky/archive/fireweather/forecasts/{doi.strftime("%Y%m%d00")}/')
make_dir.mkdir(parents=True, exist_ok=True)


domains = ["d03"]
for domain in domains:
    domain_startTime = datetime.now()
    print(f"start of domain {domain}: ", str(domain_startTime))
    config = dict(
        model="wrf",
        initialize=False,
        initialize_hffmc=False,
        overwinter=False,
        fbp_mode=True,
        correctbias=False,
    )
    config["doi"] = doi
    config['domain'] = domain
    coeff = FWF(
        config=config,
    )
    coeff.daily()
    coeff.hourly()
    print(f"Domain {domain} run time: ", datetime.now() - domain_startTime)

### Timer
print("Total Run Time: ", datetime.now() - startTime)
