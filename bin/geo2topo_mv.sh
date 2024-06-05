#!/bin/bash

cp /bluesky/fireweather/fwf/data/json/topo.json /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/

# ### Convert FRP to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/frp-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FRP="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done

# ### Convert FFMC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/ffmc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert DMC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/dc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert ISI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/isi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


# ## Convert BUI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/bui-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert FWI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/fwi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done

# ### Convert HFI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/hfi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 hfi="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done

# ### Convert ROS to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/ros-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ros="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


# ### Convert CFB to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/cfb-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 cfb="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


# ### Convert TFC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/tfc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 tfc="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert Wind Speed to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/ws-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


# Convert Temperautre to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/temp-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert Relative Humidity to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/rh-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done

## Convert total accumulated precip to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/precip*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert total accumulated precip to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/precip_3h-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done


## Convert total accumulated snow to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/snw-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 snw="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done
