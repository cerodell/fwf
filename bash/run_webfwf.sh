

# create geojson files for display on leaflet
# /bluesky/fireweather/fwf/firewx_website/python/geojson_maker.py

## Create json file for plotly line plots
/bluesky/fireweather/fwf/firewx_website/python/ds2json.py

## Convert gejsons to topojsons and move to current forecast folder
/bluesky/fireweather/fwf/bash/geo2topo_mv.sh

## Create new index.html file for current forecast
/bluesky/fireweather/fwf/firewx_website/python/index_generator.py