#!/bin/bash
# Convert FFMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/FFMC/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/test/json/FFMC/$(basename "$filename" .geojson).geojson"
done
chmod 755 -R /bluesky/archive/fireweather/test/json/FFMC

# Convert DMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/DMC/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/archive/fireweather/test/json/DMC/$(basename "$filename" .geojson).geojson"
done
chmod 755 -R /bluesky/archive/fireweather/test/json/DMC

# Convert DC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/DC/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/test/json/DC/$(basename "$filename" .geojson).geojson"
done
chmod 755 -R /bluesky/archive/fireweather/test/json/DC

# Convert ISI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/ISI/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/test/json/ISI/$(basename "$filename" .geojson).geojson"
done
chmod 755 -R /bluesky/archive/fireweather/test/json/ISI

# Convert BUI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/BUI/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/test/json/BUI/$(basename "$filename" .geojson).geojson"
done
chmod 755 -R /bluesky/archive/fireweather/test/json/BUI

# Convert FWI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/FWI/*.geojson; do
    /bluesky/fireweather/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/test/json/FWI/$(basename "$filename" .geojson).geojson"
done
chmod 755 -R /bluesky/archive/fireweather/test/json/FWI



# /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d')/