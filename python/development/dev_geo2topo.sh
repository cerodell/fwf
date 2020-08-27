#!/bin/bash


# geobuf decode < ffmc-2020082600.pbf > example.pbf.json
# geobuf encode < ffmc-2020082600-test.geojson > ffmc-2020082600-test.pbf
# # cd /bluesky/fireweather/fwf/data/geojson/2020082600/
# /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC=ffmc-2020082600.geojson > /bluesky/fireweather/fwf/web_dev/data/ffmc-2020082600.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI=isi-2020082600.geojson > /bluesky/fireweather/fwf/web_dev/data/isi-2020082600.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI=fwi-2020082600.geojson > /bluesky/fireweather/fwf/web_dev/data/fwi-2020082600.json

# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC=dmc-20200817.geojson > /bluesky/fireweather/fwf/web_dev/data/dmc-20200817.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC=dc-20200817.geojson > /bluesky/fireweather/fwf/web_dev/data/dc-20200817.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI=bui-20200817.geojson > /bluesky/fireweather/fwf/web_dev/data/bui-20200817.json
# gzip < ffmc-2020082600.json > ffmc-2020082600.json.gz
# gzip -9 < ffmc-2020082600.pbf > ffmc-2020082600.pbf.gz
# tippecanoe -zg -o ffmc-2020082600-42.mbtiles --drop-densest-as-needed ffmc-2020082600.geojson
# tippecanoe -zg -o ffmc-2020082600-extended-zooms.mbtiles --extend-zooms-if-still-dropping ffmc-2020082600.geojson
# tippecanoe -o ffmc-2020082600-zz.mbtiles ffmc-2020082600.json
# tippecanoe -zg -o ffmc-2020082600-blah.mbtiles --drop-densest-as-needed ffmc-2020082600.json
# tippecanoe -o ffmc-2020082600-blah.mbtiles --detect-shared-borders ffmc-2020082600.json
## Convert FFMC to topojson and move to website directory
# /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp=wsp-2020082600.geojson > /bluesky/fireweather/fwf/web_dev/data/wsp-2020082600.json
# /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp=temp-2020082600.geojson > /bluesky/fireweather/fwf/web_dev/data/temp-2020082600.json
# /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh=rh-2020082600.geojson > /bluesky/fireweather/fwf/web_dev/data/rh-2020082600.json


for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/ffmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

# Convert DMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/dmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert DC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/dc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert ISI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/isi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert BUI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/bui*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert FWI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/fwi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert Wind Speed to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/wsp*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert Temperautre to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/temp*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert Relative Humidity to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/rh*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert total accumulated precip to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020082600/qpf*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

# gzip < fwf-zone.json > fwf-zone.json.gz

# ### Gzip (with max compression) every new topojson in website directory
# for filename in /bluesky/fireweather/fwf/web_dev/data/*.json; do
#     gzip < "$filename" > "$filename".gz
# done







