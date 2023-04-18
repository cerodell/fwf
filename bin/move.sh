#!/bin/bash

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
