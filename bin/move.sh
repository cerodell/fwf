#!/bin/bash

cd /Volumes/WFRT-Ext23/fwf-data/ecmwf/era5/
for y in {2020..2022}; do
    for m in {1..12}; do
        printf -v month "%02d" "$m"
        mkdir -p "$y$month"
        # mv era5-"$y$month"* "$y$month"/
    done
done
