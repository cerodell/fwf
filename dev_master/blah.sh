#!/bin/bash

# cp /bluesky/fireweather/fwf/json/fwf-zone.json /bluesky/archive/fireweather/forecasts/$filefolder/
# cp /bluesky/fireweather/fwf/json/topo-notab.json /bluesky/archive/fireweather/forecasts/$filefolder/

declare filefolder=$(date -d "-4 days" '+%Y%m%d00')
declare filedate0=$(date -d "-4 days" '+%Y%m%d')
declare filedate1=$(date -d "-3 days" '+%Y%m%d')
declare filedate2=$(date -d "-2 days" '+%Y%m%d')

echo $filedate0
echo $filedate1
echo $filedate2

### Convert FFMC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$filefolder/
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$filedate0"$i"-d02.geojson ffmc-$filedate0"$i"-d03.geojson > ffmc-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$filedate1"$i"-d02.geojson ffmc-$filedate1"$i"-d03.geojson > ffmc-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$filedate2"$i"-d02.geojson ffmc-$filedate2"$i"-d03.geojson > ffmc-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/ffmc-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done



# ## Convert DMC to topojson and move to website directory
# cd /bluesky/fireweather/fwf/data/geojson/$filefolder/
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dmc-$filedate0-d02.geojson dmc-$filedate0-d03.geojson > dmc-merge-$filedate0.geojson
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dmc-$filedate1-d02.geojson dmc-$filedate1-d03.geojson > dmc-merge-$filedate1.geojson


# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/dmc-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done


# # ## Convert DC to topojson and move to website directory
# cd /bluesky/fireweather/fwf/data/geojson/$filefolder/
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dc-$filedate0-d02.geojson dc-$filedate0-d03.geojson > dc-merge-$filedate0.geojson
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dc-$filedate1-d02.geojson dc-$filedate1-d03.geojson > dc-merge-$filedate1.geojson


# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/dc-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done


# cd /bluesky/fireweather/fwf/data/geojson/$filefolder/
# ## Convert ISI to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$filedate0"$i"-d02.geojson isi-$filedate0"$i"-d03.geojson > isi-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$filedate1"$i"-d02.geojson isi-$filedate1"$i"-d03.geojson > isi-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$filedate2"$i"-d02.geojson isi-$filedate2"$i"-d03.geojson > isi-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/isi-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done




# # ## Convert BUI to topojson and move to website directory
# cd /bluesky/fireweather/fwf/data/geojson/$filefolder/
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge bui-$filedate0-d02.geojson bui-$filedate0-d03.geojson > bui-merge-$filedate0.geojson
# /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge bui-$filedate1-d02.geojson bui-$filedate1-d03.geojson > bui-merge-$filedate1.geojson

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/bui-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done





# ## Convert FWI to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$filedate0"$i"-d02.geojson fwi-$filedate0"$i"-d03.geojson > fwi-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$filedate1"$i"-d02.geojson fwi-$filedate1"$i"-d03.geojson > fwi-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$filedate2"$i"-d02.geojson fwi-$filedate2"$i"-d03.geojson > fwi-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/fwi-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done





# ## Convert Wind Speed to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$filedate0"$i"-d02.geojson ws-$filedate0"$i"-d03.geojson > ws-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$filedate1"$i"-d02.geojson ws-$filedate1"$i"-d03.geojson > ws-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$filedate2"$i"-d02.geojson ws-$filedate2"$i"-d03.geojson > ws-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/ws-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done



# # Convert Temperautre to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$filedate0"$i"-d02.geojson temp-$filedate0"$i"-d03.geojson > temp-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$filedate1"$i"-d02.geojson temp-$filedate1"$i"-d03.geojson > temp-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$filedate2"$i"-d02.geojson temp-$filedate2"$i"-d03.geojson > temp-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/temp-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done




# ## Convert Relative Humidity to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$filedate0"$i"-d02.geojson rh-$filedate0"$i"-d03.geojson > rh-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$filedate1"$i"-d02.geojson rh-$filedate1"$i"-d03.geojson > rh-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$filedate2"$i"-d02.geojson rh-$filedate2"$i"-d03.geojson > rh-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/rh-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done




## Convert total accumulated precip to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$filedate0"$i"-d02.geojson precip-$filedate0"$i"-d03.geojson > precip-merge-$filedate0"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$filedate1"$i"-d02.geojson precip-$filedate1"$i"-d03.geojson > precip-merge-$filedate1"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$filedate2"$i"-d02.geojson precip-$filedate2"$i"-d03.geojson > precip-merge-$filedate2"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/precip-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done



## Convert total accumulated precip to topojson and move to website directory
declare -a arr=("00" "03" "06" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$filedate0"$i"-d02.geojson precip_3h-$filedate0"$i"-d03.geojson > precip_3h-merge-$filedate0"$i".geojson
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$filedate1"$i"-d02.geojson precip_3h-$filedate1"$i"-d03.geojson > precip_3h-merge-$filedate1"$i".geojson
done

declare -a arr=("00" "03" "06" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$filedate2"$i"-d02.geojson precip_3h-$filedate2"$i"-d03.geojson > precip_3h-merge-$filedate2"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/precip_3h-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done



# ## Convert total accumulated snow to topojson and move to website directory
# declare -a arr=("00" "03" "06" "12" "15" "18" "21")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$filedate0"$i"-d02.geojson snw-$filedate0"$i"-d03.geojson > snw-merge-$filedate0"$i".geojson
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$filedate1"$i"-d02.geojson snw-$filedate1"$i"-d03.geojson > snw-merge-$filedate1"$i".geojson
# done

# declare -a arr=("00" "03" "06" "12")
# for i in "${arr[@]}"
# do
#     /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$filedate2"$i"-d02.geojson snw-$filedate2"$i"-d03.geojson > snw-merge-$filedate2"$i".geojson
# done

# for filename in /bluesky/fireweather/fwf/data/geojson/$filefolder/snw-merge*.geojson; do
#     # echo "$filename"
#     /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 snw="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
# done




