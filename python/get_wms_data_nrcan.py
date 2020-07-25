import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService
import json
import pandas as pd
import matplotlib.pyplot as plt

from urllib.request import urlopen

# URL for WFS backend
url = "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms"


wfs = WebFeatureService(url=url)
layers = list(wfs.contents)

layer = 'public:firewx_stns_current'

# Specify the parameters for fetching the data
params = dict(service='WFS', version="1.0.0", request='GetFeature',
      typeName=layer, outputFormat='json')

# # Parse the URL with parameters
q = Request('GET', url, params=params).prepare().url

data = gpd.read_file(q)
























# url = "http://cwfis.cfs.nrcan.gc.ca/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities"

# wfs11 = WebFeatureService(url=url, version='1.1.0')


# nrcan_title = wfs11.identification.title


# nrcan_ops = [operation.name for operation in wfs11.operations]

# response = wfs11.getfeature(typename='public:firewx_scribe_fcst', \
#       bbox=(-2322698.03550066,-662912.092927479,3011665.30167772,3810393.75946683), srsname='EPSG:3978')

# data = gpd.read_file(response)
# firewx = wfs11.get_schema('public:firewx_scribe_fcst')


# wfs = WebFeatureService(url=url)
# layer = list(wfs.contents)
# Get data from WFS
# -----------------
# Fetch the last available layer 
# layer = 'public:firewx_scribe_fcst'

# response = wfs11.getfeature(typename='bvv:gmd_ex', bbox=(4500000,5500000,4500500,5500500), srsname='urn:x-ogc:def:crs:EPSG:31468')

# # Specify the parameters for fetching the data
# params = dict(service='WFS', version="1.0.0", request='GetFeature',
#       typeName=layer, outputFormat='json')
# url = "https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms"

# # # Parse the URL with parameters
# q = Request('GET', url, params=params).prepare().url
# data2 = gpd.read_file(q)

# # q3 = 'http://cwfis.cfs.nrcan.gc.ca/geoserver/ows?service=wms&version=1.3.0&request=GetFeature&typeName=public%3Afirewx_scribe_fcst&outputFormat=json'
# # data3 = gpd.read_file(q3)

# # https://cwfis.cfs.nrcan.gc.ca/geoserver/public/wms?service=WFS&version=1.0.0
# # &request=GetFeature&typeName=public%3Afirewx_scribe_fcst&outputFormat=json


# jsonp = urlopen(q).read()
# # test = json.loads(jsonp)
# # with open(jsonp) as f:
# #   data = json.load(f)
# # # tester = pd.read_csv(q)
# # # # Read data from URL
# # data = gpd.read_file(q)

