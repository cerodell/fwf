
cd /Volumes/cer/fireweather/data/xr/
for filename in *.zarr; do
    echo ${filename%%.*}
    tar -czvf ${filename%%.*}.tgz ${filename%%.*}.zarr
    mv ${filename%%.*}.tgz /Volumes/cer/fireweather/data/tar/

done


