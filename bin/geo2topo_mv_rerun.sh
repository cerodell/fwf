#!/bin/bash

cp /bluesky/fireweather/fwf/data/json/topo.json /bluesky/archive/fireweather/forecasts/$previous_date00/

current_date=$(date '+%Y%m%d')  # Get current date in the format YYYY-MM-DD

previous_date=$(date -d "$current_date - 1 day" '+%Y%m%d')  # Subtract one day
previous_date00=$(date -d "$current_date - 1 day" '+%Y%m%d00')  # Subtract one day
previous_date06=$(date -d "$current_date - 1 day" '+%Y%m%d06')  # Subtract one day
previous_date_day2=$(date '+%Y%m%d') # Subtract one day
previous_date_day3=$(date -d "+1 days" '+%Y%m%d')

previous_date_folder=$(date -d "$current_date - 1 day" '+%Y%m%d06')  # Subtract one day

echo $previous_date
echo $previous_date_day2
echo $previous_date_day3

# ### Convert FFMC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date_folder/

declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$previous_date"$i"-d02.geojson ffmc-$previous_date"$i"-d03.geojson > ffmc-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$previous_date_day2"$i"-d02.geojson ffmc-$previous_date_day2"$i"-d03.geojson > ffmc-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ffmc-$previous_date_day3"$i"-d02.geojson ffmc-$previous_date_day3"$i"-d03.geojson > ffmc-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/ffmc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FFMC="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


# ## Convert DMC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
/bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dmc-$previous_date-d02.geojson dmc-$previous_date-d03.geojson > dmc-merge-$previous_date.geojson
/bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dmc-$previous_date_day2-d02.geojson dmc-$previous_date_day2-d03.geojson > dmc-merge-$previous_date_day2.geojson


for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/dmc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DMC="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


# ## Convert DC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
/bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dc-$previous_date-d02.geojson dc-$previous_date-d03.geojson > dc-merge-$previous_date.geojson
/bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge dc-$previous_date_day2-d02.geojson dc-$previous_date_day2-d03.geojson > dc-merge-$previous_date_day2.geojson


for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/dc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 DC="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
## Convert ISI to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$previous_date"$i"-d02.geojson isi-$previous_date"$i"-d03.geojson > isi-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$previous_date_day2"$i"-d02.geojson isi-$previous_date_day2"$i"-d03.geojson > isi-merge-$previous_date_day2"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge isi-$previous_date_day3"$i"-d02.geojson isi-$previous_date_day3"$i"-d03.geojson > isi-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/isi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ISI="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done




# ## Convert BUI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
/bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge bui-$previous_date-d02.geojson bui-$previous_date-d03.geojson > bui-merge-$previous_date.geojson
/bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge bui-$previous_date_day2-d02.geojson bui-$previous_date_day2-d03.geojson > bui-merge-$previous_date_day2.geojson

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/bui-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 BUI="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done




## Convert FWI to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$previous_date"$i"-d02.geojson fwi-$previous_date"$i"-d03.geojson > fwi-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$previous_date_day2"$i"-d02.geojson fwi-$previous_date_day2"$i"-d03.geojson > fwi-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge fwi-$previous_date_day3"$i"-d02.geojson fwi-$previous_date_day3"$i"-d03.geojson > fwi-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/fwi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 FWI="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done



# ### Convert HFI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge hfi-$previous_date"$i"-d02.geojson hfi-$previous_date"$i"-d03.geojson > hfi-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge hfi-$previous_date_day2"$i"-d02.geojson hfi-$previous_date_day2"$i"-d03.geojson > hfi-merge-$previous_date_day2"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge hfi-$previous_date_day3"$i"-d02.geojson hfi-$previous_date_day3"$i"-d03.geojson > hfi-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/hfi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 hfi="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


# ### Convert ROS to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ros-$previous_date"$i"-d02.geojson ros-$previous_date"$i"-d03.geojson > ros-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ros-$previous_date_day2"$i"-d02.geojson ros-$previous_date_day2"$i"-d03.geojson > ros-merge-$previous_date_day2"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ros-$previous_date_day3"$i"-d02.geojson ros-$previous_date_day3"$i"-d03.geojson > ros-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/ros-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 ros="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


# ### Convert CFB to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge cfb-$previous_date"$i"-d02.geojson cfb-$previous_date"$i"-d03.geojson > cfb-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge cfb-$previous_date_day2"$i"-d02.geojson cfb-$previous_date_day2"$i"-d03.geojson > cfb-merge-$previous_date_day2"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge cfb-$previous_date_day3"$i"-d02.geojson cfb-$previous_date_day3"$i"-d03.geojson > cfb-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/cfb-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 cfb="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


# ### Convert SFC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge sfc-$previous_date"$i"-d02.geojson sfc-$previous_date"$i"-d03.geojson > sfc-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge sfc-$previous_date_day2"$i"-d02.geojson sfc-$previous_date_day2"$i"-d03.geojson > sfc-merge-$previous_date_day2"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge sfc-$previous_date_day3"$i"-d02.geojson sfc-$previous_date_day3"$i"-d03.geojson > sfc-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/sfc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 sfc="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


# ### Convert TFC to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$previous_date06/
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge tfc-$previous_date"$i"-d02.geojson tfc-$previous_date"$i"-d03.geojson > tfc-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge tfc-$previous_date_day2"$i"-d02.geojson tfc-$previous_date_day2"$i"-d03.geojson > tfc-merge-$previous_date_day2"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge tfc-$previous_date_day3"$i"-d02.geojson tfc-$previous_date_day3"$i"-d03.geojson > tfc-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/tfc-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 tfc="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done


## Convert Wind Speed to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$previous_date"$i"-d02.geojson ws-$previous_date"$i"-d03.geojson > ws-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$previous_date_day2"$i"-d02.geojson ws-$previous_date_day2"$i"-d03.geojson > ws-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge ws-$previous_date_day3"$i"-d02.geojson ws-$previous_date_day3"$i"-d03.geojson > ws-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/ws-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 wsp="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done



# Convert Temperautre to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$previous_date"$i"-d02.geojson temp-$previous_date"$i"-d03.geojson > temp-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$previous_date_day2"$i"-d02.geojson temp-$previous_date_day2"$i"-d03.geojson > temp-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge temp-$previous_date_day3"$i"-d02.geojson temp-$previous_date_day3"$i"-d03.geojson > temp-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/temp-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done




## Convert Relative Humidity to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$previous_date"$i"-d02.geojson rh-$previous_date"$i"-d03.geojson > rh-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$previous_date_day2"$i"-d02.geojson rh-$previous_date_day2"$i"-d03.geojson > rh-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge rh-$previous_date_day3"$i"-d02.geojson rh-$previous_date_day3"$i"-d03.geojson > rh-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/rh-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 rh="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done




## Convert total accumulated precip to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$previous_date"$i"-d02.geojson precip-$previous_date"$i"-d03.geojson > precip-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$previous_date_day2"$i"-d02.geojson precip-$previous_date_day2"$i"-d03.geojson > precip-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip-$previous_date_day3"$i"-d02.geojson precip-$previous_date_day3"$i"-d03.geojson > precip-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/precip*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done



## Convert total accumulated precip to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$previous_date"$i"-d02.geojson precip_3h-$previous_date"$i"-d03.geojson > precip_3h-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$previous_date_day2"$i"-d02.geojson precip_3h-$previous_date_day2"$i"-d03.geojson > precip_3h-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge precip_3h-$previous_date_day3"$i"-d02.geojson precip_3h-$previous_date_day3"$i"-d03.geojson > precip_3h-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/precip_3h-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 qpf="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done



## Convert total accumulated snow to topojson and move to website directory
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$previous_date"$i"-d02.geojson snw-$previous_date"$i"-d03.geojson > snw-merge-$previous_date"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$previous_date_day2"$i"-d02.geojson snw-$previous_date_day2"$i"-d03.geojson > snw-merge-$previous_date_day2"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge snw-$previous_date_day3"$i"-d02.geojson snw-$previous_date_day3"$i"-d03.geojson > snw-merge-$previous_date_day3"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$previous_date06/snw-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 snw="$filename" > "/bluesky/archive/fireweather/forecasts/$previous_date00/data/map/$(basename "$filename" .geojson).json"
done
