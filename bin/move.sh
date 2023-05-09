#!/bin/bash

<<<<<<< HEAD
cd /bluesky/archive/fireweather/data/
for y in {2023..2023}; do
    for m in {1..3}; do
        printf -v month "%02d" "$m"
        # mkdir -p "$y$month"
        mv fwf-hourly-d03-"$y$month"* d03"/$y$month"/
        mv fwf-daily-d03-"$y$month"* d03"/$y$month"/
    done
done
=======
cd /Volumes/Backup0/eccc/hrdps
for y in {2021..2021}; do
    for m in {1..12}; do
        printf -v month "%02d" "$m"
        tar -czvf "$y$month".tgz "$y$month"
        # mkdir -p "$y$month"
        # mv era5-"$y$month"* "$y$month"/
    done
done

 tar -czvf 202101.tgz 202101
>>>>>>> 4fec3ad82ce600f3a83dbac11c39365cf12d3f2d
