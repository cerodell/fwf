#!/bin/bash

cd /Volumes/WFRT-Ext23/fwf-data/ecmwf/era5-land/04
for y in {1991..2023}; do
    for m in {1..12}; do
        if (( m < 10 )); then
            echo "$y"0"$m"
            mkdir "$y"0"$m"
            mv fwf-hourly-era5-land-"$y"0"$m"* "$y"0"$m"/
            mv fwf-daily-era5-land-"$y"0"$m"* "$y"0"$m"/
        else
            echo "$y$m"
            mkdir "$y$m"
            mv fwf-hourly-era5-land-"$y$m"* "$y$m"/
            mv fwf-daily-era5-land-"$y$m"* "$y$m"/
        fi
    done
done
