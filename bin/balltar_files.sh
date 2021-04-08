#!/bin/bash


# (date '+%Y%m%d06')
cd /bluesky/fireweather/fwf/data/FWF-WAN00CG-01
echo "making fwf-daily-d02 tgz at: --> $(date '+%Y-%m-%dT%H')"
tar -czvf fwf-daily-d02-$(date '+%Y%m%d06').tgz fwf-daily-d02-$(date '+%Y%m%d06').zarr
mv fwf-daily-d02-$(date '+%Y%m%d06').tgz /bluesky/archive/fireweather/data/
rm -r fwf-daily-d02-$(date  -d "3 days ago" '+%Y%m%d06').zarr
echo "fwf-daily-d02 tgz made and mv at: --> $(date '+%Y-%m-%dT%H')"

echo "making fwf-hourly-d02 tgz at: --> $(date '+%Y%m%dT%H')"
tar -czvf fwf-hourly-d02-$(date '+%Y%m%d06').tgz fwf-hourly-d02-$(date '+%Y%m%d06').zarr
mv fwf-hourly-d02-$(date '+%Y%m%d06').tgz /bluesky/archive/fireweather/data/
rm -r fwf-hourly-d02-$(date  -d "3 days ago" '+%Y%m%d06').zarr
echo "fwf-hourly-d02 tgz made and mv at: --> $(date '+%Y%m%dT%H')"

echo "making fwf-daily-d03 tgz at: --> $(date '+%Y-%m-%dT%H')"
tar -czvf fwf-daily-d03-$(date '+%Y%m%d06').tgz fwf-daily-d03-$(date '+%Y%m%d06').zarr
mv fwf-daily-d03-$(date '+%Y%m%d06').tgz /bluesky/archive/fireweather/data/
rm -r fwf-daily-d03-$(date  -d "3 days ago" '+%Y%m%d06').zarr
echo "fwf-daily-d03 tgz made and mv at: --> $(date '+%Y-%m-%dT%H')"

echo "making fwf-hourly-d03 tgz at: --> $(date '+%Y%m%dT%H')"
tar -czvf fwf-hourly-d03-$(date '+%Y%m%d06').tgz fwf-hourly-d03-$(date '+%Y%m%d06').zarr
mv fwf-hourly-d03-$(date '+%Y%m%d06').tgz /bluesky/archive/fireweather/data/
rm -r fwf-hourly-d03-$(date  -d "3 days ago" '+%Y%m%d06').zarr
echo "fwf-hourly-d03 tgz made and mv at: --> $(date '+%Y%m%dT%H')"


cd /bluesky/fireweather/fwf/data/geojson/
echo "deleting yesterdays geojson files at: --> $(date '+%Y-%m-%dT%H')"
rm -r $(date  -d "1 days ago" '+%Y%m%d06/')
echo "deleted yesterdays geojson files at: --> $(date '+%Y-%m-%dT%H')"
