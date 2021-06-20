


# cd /bluesky/archive/fireweather/data/
# declare -a arr=( "08" "09")
# for i in "${arr[@]}"
# # for i in {10..14}
# do
#     echo fwf-hourly-d03-202104"$i"06.tgz
#     tar -xzf fwf-hourly-d03-202104"$i"06.tgz

#     # echo fwf-hourly-d02-202104"$i"06.tgz
#     # tar -xzf fwf-hourly-d02-202104"$i"06.tgz

# done



# cd /bluesky/archive/fireweather/data/
# declare -a arr=("01" "02" "03" "04" "05" "06" "07" "08" "09")
# for i in "${arr[@]}"
# # for i in {1..14}
# do
#     echo fwf-hourly-d03-202104"$i"06.tgz
#     rm -r fwf-hourly-d03-202104"$i"06.tgz

#     echo fwf-hourly-d03-202104"$i"06.zarr
#     rm -r fwf-hourly-d03-202104"$i"06.zarr

#     echo fwf-daily-d03-202104"$i"06.tgz
#     rm -r fwf-daily-d03-202104"$i"06.tgz

#     echo fwf-hourly-d02-202104"$i"06.tgz
#     rm -r fwf-hourly-d02-202104"$i"06.tgz

#     echo fwf-hourly-d02-202104"$i"06.zarr
#     rm -r fwf-hourly-d02-202104"$i"06.zarr

#     echo fwf-daily-d02-202104"$i"06.tgz
#     rm -r fwf-daily-d02-202104"$i"06.tgz
# done

# cd /bluesky/archive/fireweather/data/
# declare -a arr=("09")
# for i in "${arr[@]}"
# do
#     echo fwf-hourly-d03-202103"$i"06.zarr
#     rm -r fwf-hourly-d03-202103"$i"06.zarr

#     echo fwf-daily-d03-202103"$i"06.zarr
#     rm -r fwf-daily-d03-202103"$i"06.zarr

#     echo fwf-hourly-d02-202103"$i"06.zarr
#     rm -r fwf-hourly-d02-202103"$i"06.zarr

#     echo fwf-daily-d02-202103"$i"06.zarr
#     rm -r fwf-daily-d02-202103"$i"06.zarr
# done

# cd /bluesky/fireweather/fwf/data/FWF-WAN00CG-01
# declare -a arr=("01" "02" "03" "04" "05" "06" "07" "08")
# for i in "${arr[@]}"
# do
#     echo fwf-hourly-d03-202103"$i"06.nc
#     rm -r fwf-hourly-d03-202103"$i"06.nc

#     echo fwf-daily-d03-202103"$i"06.nc
#     rm -r fwf-daily-d03-202103"$i"06.nc
# #
#     echo fwf-hourly-d02-202103"$i"06.nc
#     rm -r fwf-hourly-d02-202103"$i"06.nc

#     echo fwf-daily-d02-202103"$i"06.nc
#     rm -r fwf-daily-d02-202103"$i"06.nc
# done

cd /bluesky/fireweather/fwf/data/FWF-WAN00CG-01
for i in {16..28}
# declare -a arr=("01" "02" "03" "04" "05" "06" "07" "08" "09")
# for i in "${arr[@]}"
do
    echo fwf-hourly-d03-202104"$i"06.nc
    rm -r fwf-hourly-d03-202104"$i"06.nc

    echo fwf-daily-d03-202104"$i"06.nc
    rm -r fwf-daily-d03-202104"$i"06.nc

    echo fwf-hourly-d02-202104"$i"06.nc
    rm -r fwf-hourly-d02-202104"$i"06.nc

    echo fwf-daily-d02-202104"$i"06.nc
    rm -r fwf-daily-d02-202104"$i"06.nc
done
