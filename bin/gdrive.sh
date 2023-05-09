## use this for running specific case studies
# declare -a arr=("20180612" "20180618")
cd /bluesky/archive/fireweather/data
# for j in {5..5};
# do
for i in {24..31};
do
  echo fwf-daily-202005"$i"00.tgz
  rclone copy fwf-daily-202005"$i"00.tgz grdive:FWF-WAN00CG/
  echo "finsihed rclone" fwf-hourly-202005"$i"00.tgz "to gdrive"
  rm -r fwf-daily-202005"$i"00.tgz
# done
done


rclone copy 202101.tgz grdive:FWF-WAN00CG/
