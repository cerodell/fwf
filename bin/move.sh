#!/bin/bash

cd /bluesky/archive/fireweather/data/
for y in {2023..2023}; do
    for m in {1..3}; do
        printf -v month "%02d" "$m"
        # mkdir -p "$y$month"
        mv fwf-hourly-d03-"$y$month"* d03"/$y$month"/
        mv fwf-daily-d03-"$y$month"* d03"/$y$month"/
    done
done
