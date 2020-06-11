#!/bin/bash



mkdir /bluesky/archive/fireweather/hourly/$(date '+%Y%m%d')
mv /bluesky/fireweather/fwf/data/xr/hourly/*.zarr /bluesky/archive/fireweather/hourly/$(date '+%Y%m%d')

tar -czvf $(date '+%Y%m%d').tar.gz /bluesky/archive/fireweather/hourly/$(date '+%Y%m%d') 

tar -czvf 20200610.tar.gz /bluesky/archive/fireweather/daily/20200610