#!/bin/bash

cd /Volumes/ThunderBay/CRodell/ecmwf/era5
for y in {2019..2019}; do
    for m in {1..12}; do
        if (( m < 10 )); then
            echo "$y"0"$m"
            mkdir "$y"0"$m"
            mv era5-"$y"0"$m"* "$y"0"$m"/
        else
            echo "$y$m"
            mkdir "$y$m"
            mv era5-"$y$m"* "$y$m"/
        fi
    done
done
