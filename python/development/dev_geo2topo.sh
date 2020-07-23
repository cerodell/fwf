#!/bin/bash

/bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC=ffmc-2020071700.geojson > /bluesky/archive/fireweather/forecasts/2020071700/ffmc-2020071700.json
gzip -9 < ffmc-2020071700.json > ffmc-2020071700.json.gz
# ### Convert FFMC to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020071700/ffmc*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/forecasts/2020071700/$(basename "$filename" .geojson).json"
# done

# ## Convert DMC to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020071700/dmc*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/archive/fireweather/forecasts/2020071700/$(basename "$filename" .geojson).json"
# done

# ## Convert DC to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020071700/dc*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/forecasts/2020071700/$(basename "$filename" .geojson).json"
# done

# ## Convert ISI to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020071700/isi*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/forecasts/2020071700/$(basename "$filename" .geojson).json"
# done

# ## Convert BUI to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020071700/bui*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/forecasts/2020071700/$(basename "$filename" .geojson).json"
# done

# ## Convert FWI to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020071700/fwi*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/forecasts/2020071700/$(basename "$filename" .geojson).json"
# done


# ### Gzip (with max compression) every new topojson in website directory
# for filename in /bluesky/archive/fireweather/forecasts/2020071700/*.json; do
#     gzip -9 < "$filename" > "$filename".gz
# done

# # Gzip (with max compression) json file..used in plotly lines plots
# cd /bluesky/archive/fireweather/forecasts/2020071700
# gzip -9 < fwf-32km-2020071700.json > fwf-32km-2020071700.json.gz
# gzip -9 < fwf-16km-2020071700.json > fwf-16km-2020071700.json.gz
# gzip -9 < fwf-4km-2020071700.json > fwf-4km-2020071700.json.gz





