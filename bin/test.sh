# ### Convert HFI to topojson and move to website directory
cd /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/
declare -a arr=("06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge hfi-$(date '+%Y%m%d')"$i"-d02.geojson hfi-$(date '+%Y%m%d')"$i"-d03.geojson > hfi-merge-$(date '+%Y%m%d')"$i".geojson
done

declare -a arr=("00" "03" "06" "09" "12" "15" "18" "21")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge hfi-$(date -d "+1 days" '+%Y%m%d')"$i"-d02.geojson hfi-$(date -d "+1 days" '+%Y%m%d')"$i"-d03.geojson > hfi-merge-$(date -d "+1 days" '+%Y%m%d')"$i".geojson
done


declare -a arr=("00" "03" "06" "09" "12")
for i in "${arr[@]}"
do
    /bluesky/fireweather/fwf/node_modules/@mapbox/geojson-merge/geojson-merge hfi-$(date -d "+2 days" '+%Y%m%d')"$i"-d02.geojson hfi-$(date -d "+2 days" '+%Y%m%d')"$i"-d03.geojson > hfi-merge-$(date -d "+2 days" '+%Y%m%d')"$i".geojson
done

for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d06')/hfi-merge*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 hfi="$filename" > "/bluesky/archive/fireweather/forecasts/$(date '+%Y%m%d00')/data/map/$(basename "$filename" .geojson).json"
done
