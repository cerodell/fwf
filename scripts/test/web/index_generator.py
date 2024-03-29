#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Creates an index.html (from template in static/html) file for each forecast.
"""
import context
import logging
from pathlib import Path
from datetime import datetime, date, timedelta

startTime = datetime.now()

from context import html_dir #ops_dir

ops_dir = '/bluesky/fireweather/fwf/web_dev/'
__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

forecast_start_date = date.today()
forecast_end_date = forecast_start_date + timedelta(days=2)
folderdate = forecast_start_date.strftime("%Y%m%d")

observations = forecast_start_date - timedelta(days=1)
observations = observations.strftime("%Y%m%d")

forecast_start_date = forecast_start_date.strftime("%Y-%m-%dT06:00:00Z")
forecast_end_date = forecast_end_date.strftime("%Y-%m-%dT12:00:00Z")

files_datetime = folderdate
print(f"{str(datetime.now())} ---> open/read html template")
fcst_template = str(html_dir) + "/fwf-forecast-template.html"
with open(fcst_template, "r") as fin:
    fcst = fin.read()
    ## update timedim start and end
    fcst = fcst.replace("{%FirstDateTime%}", forecast_start_date)
    fcst = fcst.replace("{%LastDateTime%}", forecast_end_date)
    fcst = fcst.replace("{%FileDateTime%}", files_datetime)
    fcst = fcst.replace("{%FileDateTimeYesterday%}", observations)

    make_dir = Path(str(ops_dir))
    make_dir.mkdir(parents=True, exist_ok=True)

    out_dir = str(make_dir) + "/index.html"
    with open(out_dir, "w") as fout:
        fout.write(fcst)
print(f"{str(datetime.now())} ---> write index.html")


# ### Timer
print("Run Time: ", datetime.now() - startTime)
