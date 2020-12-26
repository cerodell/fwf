for filename in /bluesky/fireweather/fwf/data/geojson/$(date '+%Y%m%d00')/temp*.geojson; do
    # echo "$filename"
    /bluesky/fireweather/fwf/node_modules/topojson-server/bin/geo2topo -q 1e4 temp="$filename" > "/bluesky/fireweather/fwf/web_dev/data/$(basename "$filename" .geojson).json"
done