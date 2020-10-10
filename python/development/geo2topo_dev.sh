#!/bin/bash


# geobuf decode < ffmc-2020090700.pbf > example.pbf.json
# geobuf encode < ffmc-2020090700-test.geojson > ffmc-2020090700-test.pbf
# # cd /bluesky/fireweather/fwf/data/geojson/2020090700/
# /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC=ffmc-2020090700.geojson > /bluesky/fireweather/fwf/web_dev/data/ffmc-2020090700.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI=isi-2020090700.geojson > /bluesky/fireweather/fwf/web_dev/data/isi-2020090700.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI=fwi-2020090700.geojson > /bluesky/fireweather/fwf/web_dev/data/fwi-2020090700.json

# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC=dmc-20200817.geojson > /bluesky/fireweather/fwf/web_dev/data/dmc-20200817.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC=dc-20200817.geojson > /bluesky/fireweather/fwf/web_dev/data/dc-20200817.json
# # /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI=bui-20200817.geojson > /bluesky/fireweather/fwf/web_dev/data/bui-20200817.json
# gzip < ffmc-2020090700.json > ffmc-2020090700.json.gz
# gzip -9 < ffmc-2020090700.pbf > ffmc-2020090700.pbf.gz
# tippecanoe -zg -o ffmc-2020090700-42.mbtiles --drop-densest-as-needed ffmc-2020090700.geojson
# tippecanoe -zg -o ffmc-2020090700-extended-zooms.mbtiles --extend-zooms-if-still-dropping ffmc-2020090700.geojson
# tippecanoe -o ffmc-2020090700-zz.mbtiles ffmc-2020090700.json
# tippecanoe -zg -o ffmc-2020090700-blah.mbtiles --drop-densest-as-needed ffmc-2020090700.json
# tippecanoe -o ffmc-2020090700-blah.mbtiles --detect-shared-borders ffmc-2020090700.json
## Convert FFMC to topojson and move to website directory
/bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 snw=snw-2020101112.geojson > /bluesky/fireweather/fwf/web_dev/data/snw-2020090700.json
/bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp=temp-2020100718.geojson > /bluesky/fireweather/fwf/web_dev/data/temp-2020090718.json


for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/ffmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

# Convert DMC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/dmc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert DC to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/dc*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert ISI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/isi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

# Convert BUI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/bui*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

## Convert FWI to topojson and move to website directory
for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/fwi*.geojson; do
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done

# ## Convert Wind Speed to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/wsp*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done

# # Convert Temperautre to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/temp*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done

# ## Convert Relative Humidity to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/rh*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done

# ## Convert total accumulated precip to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/qpf-*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done

# ## Convert total accumulated precip to topojson and move to website directory
# for filename in /bluesky/fireweather/fwf/data/geojson/2020090700/qpf_3h*.geojson; do
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done

# gzip < fwf-zone.json > fwf-zone.json.gz

# ### Gzip (with max compression) every new topojson in website directory
# for filename in /bluesky/fireweather/fwf/web_dev/data/*.json; do
#     gzip < "$filename" > "$filename".gz
# done







