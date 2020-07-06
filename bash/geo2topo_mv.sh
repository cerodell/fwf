#!/bin/bash

# Convert FFMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/FFMC/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

# Convert DMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/DMC/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

# Convert DC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/DC/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

# Convert ISI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/ISI/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

# Convert BUI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/BUI/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

# Convert FWI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/FWI/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/$(basename "$filename" .geojson).geojson"
done

chmod 755 -R /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')



