#!/bin/bash

# cp /bluesky/fireweather/fwf/json/fwf-zone.json /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/
# cp /bluesky/fireweather/fwf/json/topo-notab.json /bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/

### Convert FFMC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$(date '+%Y%m%d')"$i"-d02.geojson ffmc-$(date '+%Y%m%d')"$i"-d03.geojson > ffmc-merge-$(date '+%Y%m%d')"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson ffmc-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > ffmc-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson ffmc-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > ffmc-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/ffmc-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done



# ## Convert DMC to topojson and move to website directory
# cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dmc-$(date '+%Y%m%d')-d02.geojson dmc-$(date '+%Y%m%d')-d03.geojson > dmc-merge-$(date '+%Y%m%d').geojson
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dmc-$(date -d "+1 days" '+%Y%m%d')-d02.geojson dmc-$(date -d "+1 days" '+%Y%m%d')-d03.geojson > dmc-merge-$(date -d "+1 days" '+%Y%m%d').geojson


# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/dmc-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done


# # ## Convert DC to topojson and move to website directory
# cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dc-$(date '+%Y%m%d')-d02.geojson dc-$(date '+%Y%m%d')-d03.geojson > dc-merge-$(date '+%Y%m%d').geojson
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dc-$(date -d "+1 days" '+%Y%m%d')-d02.geojson dc-$(date -d "+1 days" '+%Y%m%d')-d03.geojson > dc-merge-$(date -d "+1 days" '+%Y%m%d').geojson


# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/dc-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done


# cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/
# ## Convert ISI to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$(date '+%Y%m%d')"$i"-d02.geojson isi-$(date '+%Y%m%d')"$i"-d03.geojson > isi-merge-$(date '+%Y%m%d')"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson isi-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > isi-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson isi-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > isi-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/isi-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done




# # ## Convert BUI to topojson and move to website directory
# cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge bui-$(date '+%Y%m%d')-d02.geojson bui-$(date '+%Y%m%d')-d03.geojson > bui-merge-$(date '+%Y%m%d').geojson
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge bui-$(date -d "+1 days" '+%Y%m%d')-d02.geojson bui-$(date -d "+1 days" '+%Y%m%d')-d03.geojson > bui-merge-$(date -d "+1 days" '+%Y%m%d').geojson

# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/bui-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done





# ## Convert FWI to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$(date '+%Y%m%d')"$i"-d02.geojson fwi-$(date '+%Y%m%d')"$i"-d03.geojson > fwi-merge-$(date '+%Y%m%d')"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson fwi-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > fwi-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson fwi-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > fwi-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/fwi-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done





## Convert Wind Speed to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$(date '+%Y%m%d')"$i"-d02.geojson ws-$(date '+%Y%m%d')"$i"-d03.geojson > ws-merge-$(date '+%Y%m%d')"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson ws-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > ws-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson ws-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > ws-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/ws-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done



# # Convert Temperautre to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$(date '+%Y%m%d')"$i"-d02.geojson temp-$(date '+%Y%m%d')"$i"-d03.geojson > temp-merge-$(date '+%Y%m%d')"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson temp-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > temp-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson temp-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > temp-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/temp-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done




## Convert Relative Humidity to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$(date '+%Y%m%d')"$i"-d02.geojson rh-$(date '+%Y%m%d')"$i"-d03.geojson > rh-merge-$(date '+%Y%m%d')"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson rh-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > rh-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson rh-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > rh-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/rh-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done




## Convert total accumulated precip to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$(date '+%Y%m%d')"$i"-d02.geojson precip-$(date '+%Y%m%d')"$i"-d03.geojson > precip-merge-$(date '+%Y%m%d')"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson precip-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > precip-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson precip-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > precip-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/precip-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done



## Convert total accumulated precip to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$(date '+%Y%m%d')"$i"-d02.geojson precip_3h-$(date '+%Y%m%d')"$i"-d03.geojson > precip_3h-merge-$(date '+%Y%m%d')"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson precip_3h-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > precip_3h-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson precip_3h-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > precip_3h-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/precip_3h-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done



## Convert total accumulated snow to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$(date '+%Y%m%d')"$i"-d02.geojson snw-$(date '+%Y%m%d')"$i"-d03.geojson > snw-merge-$(date '+%Y%m%d')"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson snw-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > snw-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson snw-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > snw-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/snw-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 snw="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done




