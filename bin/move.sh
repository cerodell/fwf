#!/bin/bash

cd /NASPANGEA2/HISTORICAL_WEATHER/FA_DTN_20_YEAR/cffdrs/fwi
for y in {2004..2024}; do
    for m in {1..12}; do
        printf -v month "%02d" "$m"
        # mkdir "$y$month"
        mv fwf-hourly-d03-"$y$month"*  "$y$month/"
        mv fwf-daily-d03-"$y$month"*   "$y$month/"
    done
done