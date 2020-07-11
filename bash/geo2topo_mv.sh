#!/bin/bash

### Convert FFMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/ffmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

### Convert DMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/dmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

### Convert DC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/dc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

### Convert ISI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/isi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

### Convert BUI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/bui*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

### Convert FWI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/fwi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done


### Gzip (with max compression) every new topojson in website directory
for filename in /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/*.geojson; do
    gzip -9 < "$filename" > "$filename".gz
done

### Gzip (with max compression) json file..used in plotly lines plots
cd /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')
gzip -9 < fwf-32km-$(date '+%Y%m%d00').json > fwf-32km-$(date '+%Y%m%d00').json.gz
gzip -9 < fwf-16km-$(date '+%Y%m%d00').json > fwf-16km-$(date '+%Y%m%d00').json.gz
gzip -9 < fwf-west-$(date '+%Y%m%d00').json > fwf-west-$(date '+%Y%m%d00').json.gz

### set new permisions on the website folder
chmod 755 -R /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')



