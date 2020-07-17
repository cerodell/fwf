#!/bin/bash


# (date '+%Y%m%d00')
cd /bluesky/fireweather/fwf/data/xr
echo "making fwf-daily tgz at: --> $(date '+%Y-%m-%dT%H')"
tar -czvf fwf-daily-$(date '+%Y%m%d00').tgz fwf-daily-$(date '+%Y%m%d00').zarr
mv fwf-daily-$(date '+%Y%m%d00').tgz /bluesky/archive/fireweather/data/
rm -r fwf-daily-$(date  -d "2 days ago" '+%Y%m%d00').zarr
echo "fwf-daily tgz made and mv at: --> $(date '+%Y-%m-%dT%H')"

echo "making fwf-hourly tgz at: --> $(date '+%Y%m%dT%H')"
tar -czvf fwf-hourly-$(date '+%Y%m%d00').tgz fwf-hourly-$(date '+%Y%m%d00').zarr
mv fwf-hourly-$(date '+%Y%m%d00').tgz /bluesky/archive/fireweather/data/
rm -r fwf-hourly-$(date  -d "2 days ago" '+%Y%m%d00').zarr
echo "fwf-hourly tgz made and mv at: --> $(date '+%Y%m%dT%H')"


