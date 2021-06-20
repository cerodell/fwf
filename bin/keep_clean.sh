#!/bin/bash


echo "$(date) ---> make symlink to kml file"
cd /bluesky/archive/fireweather/forecasts/current/data
rm -r fire_locations.kml
rm -r fire_outlines.kml
ln -sv ../../../../forecasts/BSC06CA12-01/current/fire_locations.kml
ln -sv ../../../../forecasts/BSC06CA12-01/current/fire_outlines.kml
echo "$(date) ---> symlink to kml files created"


cd /bluesky/fireweather/fwf/data/FWF-WAN00CG-01
echo "cleaning FWF-WAN00CG-01 to remove forecast dat: --> $(date '+%Y-%m-%dT%H')"
rm -r fwf-daily-d02-$(date  -d "3 days ago" '+%Y%m%d06').nc
rm -r fwf-daily-d03-$(date  -d "3 days ago" '+%Y%m%d06').nc
rm -r fwf-hourly-d02-$(date  -d "3 days ago" '+%Y%m%d06').nc
rm -r fwf-hourly-d03-$(date  -d "3 days ago" '+%Y%m%d06').nc
echo "FWF-WAN00CG-01 cleaned at: --> $(date '+%Y-%m-%dT%H')"



cd /bluesky/fireweather/fwf/data/geojson/
echo "deleting yesterdays geojson files at: --> $(date '+%Y-%m-%dT%H')"
rm -r $(date  -d "1 days ago" '+%Y%m%d06/')
echo "deleted yesterdays geojson files at: --> $(date '+%Y-%m-%dT%H')"


cd /bluesky/fireweather/fwf/data/intercomp
echo "deleting intercomp from 5 days ago at: --> $(date '+%Y-%m-%dT%H')"
rm -r intercomp-d02-$(date  -d "5 days ago" '+%Y%m%d').zarr
rm -r intercomp-d03-$(date  -d "5 days ago" '+%Y%m%d').zarr
echo "deleted intercomp from 5 days ago at: --> $(date '+%Y-%m-%dT%H')"
