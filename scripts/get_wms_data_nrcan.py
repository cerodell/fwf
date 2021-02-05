#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

"""
Scrapes Natural Resource Canada's wms server for fwi point forecast.
Saves data as csv file.

"""
import context
import pandas as pd
import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService
from datetime import datetime, date, timedelta

from context import data_dir, wrf_dir, root_dir, xr_dir

__author__ = "Christopher Rodell"
__email__ = "crodell@eoas.ubc.ca"

# URL for WFS backend
url = "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms"

wfs = WebFeatureService(url=url)
layers = list(wfs.contents)

layer = "public:firewx_scribe_fcst"

# Specify the parameters for fetching the data
params = dict(
    service="WFS",
    version="1.0.0",
    request="GetFeature",
    typeName=layer,
    outputFormat="json",
)

# # Parse the URL with parameters
q = Request("GET", url, params=params).prepare().url

data = gpd.read_file(q)
df = pd.DataFrame(data)

data_date = datetime.strptime(df["rep_date"][0], "%Y-%m-%dT%H:%M:%S").strftime(
    "%Y%m%d%H"
)

csv_dir_today = str(data_dir) + f"/csv/nrcan-fwi-forecast-{data_date}.csv"
df.to_csv(csv_dir_today, sep=",", encoding="utf-8")
print(f"{str(datetime.now())} ---> wrote {csv_dir_today}")
