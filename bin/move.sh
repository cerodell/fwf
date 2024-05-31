#!/bin/bash

cd /bluesky/archive/fireweather/data/
for y in {2024..2024}; do
    for m in {3..4}; do
        domain='d02'
        printf -v month "%02d" "$m"
        mkdir -p $domain/"$y$month"
        echo $domain/"$y$month"
        mv fwf-hourly-$domain-"$y$month"*  $domain/"$y$month/"
        mv fwf-daily-$domain-"$y$month"*   $domain/"$y$month/"

        domain='d03'
        printf -v month "%02d" "$m"
        mkdir -p $domain/"$y$month"
        echo $domain/"$y$month"
        mv fwf-hourly-$domain-"$y$month"*  $domain/"$y$month/"
        mv fwf-daily-$domain-"$y$month"*   $domain/"$y$month/"
    done
done
