#!/bin/bash

cp /bluesky/fireweather/fwf/json/fwf-zone.json /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/
cp /bluesky/fireweather/fwf/json/topo-notab.json /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/

### Convert FFMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/ffmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert DMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/dmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert DC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/dc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert ISI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/isi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert BUI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/bui*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert FWI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/fwi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done


## Convert Wind Speed to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/wsp*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

# Convert Temperautre to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/temp*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert Relative Humidity to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/rh*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert total accumulated precip to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/qpf-*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done

## Convert total accumulated precip to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/qpf_3h*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/$(basename "$filename" .geojson).json"
done








