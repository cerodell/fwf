#!/bin/bash



mkdir /bluesky/archive/fireweather/xr/hourly/$(date '+%Y%m%d')
mv /bluesky/fireweather/fwf/data/xr/hourly/*.zarr /bluesky/archive/fireweather/xr/hourly/$(date '+%Y%m%d')
tar -czvf /bluesky/archive/fireweather/xr/hourly/$(date '+%Y%m%d').tar.gz /bluesky/archive/fireweather/xr/hourly/$(date '+%Y%m%d') 

mkdir /bluesky/archive/fireweather/xr/daily/$(date '+%Y%m%d')
mv /bluesky/fireweather/fwf/data/xr/daily/*.zarr /bluesky/archive/fireweather/xr/daily/$(date '+%Y%m%d')
tar -czvf /bluesky/archive/fireweather/xr/daily/$(date '+%Y%m%d').tar.gz /bluesky/archive/fireweather/xr/daily/$(date '+%Y%m%d') 



