import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService
import json
import pandas as pd

from urllib.request import urlopen

# URL for WFS backend
url = "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms"
url = "http://cwfis.cfs.nrcan.gc.ca/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities"












wfs = WebFeatureService(url=url)
# layer = list(wfs.contents)
# Get data from WFS
# -----------------
# Fetch the last available layer 
layer = 'public:firewx_scribe_fcst'


# Specify the parameters for fetching the data
params = dict(service='WFS', version="1.0.0", request='GetFeature',
      typeName=layer, outputFormat='json')

# Parse the URL with parameters
q = Request('GET', url, params=params).prepare().url


jsonp = urlopen(q).read()
# test = json.loads(jsonp)
# with open(jsonp) as f:
#   data = json.load(f)
# # tester = pd.read_csv(q)
# # # Read data from URL
# data = gpd.read_file(q)

