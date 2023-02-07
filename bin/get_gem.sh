#!/bin/bash -l
#
# Download the NAVGEM forecast for use as initial & boundary conditions
# Based on /home/wrf/bin/get_navgem by D. Siuta
#
# R. Schigas (rschigas@eos.ubc.ca)
# 2016 May 17
#

function usage() {
    echo "Download GEM forecast"
    echo
    echo "Usage: $0 [-d YYYYMMDD] [-r] INIT"
    echo "where: INIT = two-digit initialization time i.e. 00, 06, etc"
    echo "       -d = (optional) date to download, default is current date"
    echo "       -r = (optional) download RDPS; by default downloads GDPS files"
    echo "       -x = (optional) download HRDPS; by default downloads GDPS files"

}
function log_msg() {
    # Print log message with datetime stamp
    local msg="$1"
    echo "[`/bin/date +"%F %T %Z"`] ${msg}"
}
function get_file() {
    # Download the file from the remote host
    local url="$1"
    local file="$2"
    username=$(whoami)@$(hostname -s)
    if [ ! -e ${file} ]; then
        count=0
        while [ ! -e ${file} ]; do
            /opt/local/bin/wget -nc -v ${url}/${file} || rm -f ${file}
            # TODO implement counter to give up after 5 min
            test -e ${file} || sleep 60
            count=$((count+1))
            if [[ $count -eq 10 ]]; then
                warn_string="File $file has not been found for $count minutes."
                echo $warn_string
                /nfs/mgmt6/fcst/scripts/slack.sh -c "wrf_slack_test" -u "$username" -t "Cloud IBCS download taking too long" "${warn_string}"
            fi
        done
    else
        echo "${file} already exists, skipping"
    fi
}

module load use.own

# Initialize variables
date=$(date +"%Y%m%d")
year=""
hour=""
model=gdps

# Parse optional arguments
while getopts "d:rxh" opt; do
    case "$opt" in
    d)  date=$OPTARG
        ;;
    r)  model=rdps
        ;;
    x)  model=hrdps
        ;;
    h)  usage
        exit 0
        ;;
    *)  usage
        exit 1
        ;;
    esac
done


### CHRIS GET RID OF THESE AND HARDCODE IBC_PATH
if [[ $model == "rdps" ]]; then
    module load IBCS/rdps
    echo "Preparing to download RDPS files"
    STEPS=$(seq 0 3 84)
elif [[ $model == "hrdps" ]]; then
    module load IBCS/hrdps
    echo "Preparing to download HRDPS files"
    STEPS=$(seq 0 1 48) # BUT CHRIS KEEP THIS
else
    module load IBCS/gem
    echo "Preparing to donwload GDPS files"
    STEPS=$(seq 0 3 168)
fi
###

# Parse mandatory arguments
shift $((OPTIND-1))
if [[ -z "$@" ]]; then
    echo "You must supply an initialization time."
    echo
    usage
    exit 1
else
    hour="$@"
fi


# Initialize constants
# Changed to 15km from 25km

if [[ $model == rdps ]]; then
    SRCE_ROOT="https://dd.weather.gc.ca/model_gem_regional/10km/grib2/${hour}"
elif [[ $model == hrdps ]]; then
    SRCE_ROOT="https://dd.weather.gc.ca/model_hrdps/continental/grib2/${hour}"
else
    SRCE_ROOT="https://dd.weather.gc.ca/model_gem_global/15km/grib2/lat_lon/${hour}"

fi

# CHRIS CHANGE THIS TO HARDCODED DESTINATION
# DEST_ROOT=$IBC_PATH
DEST_ROOT=/Users/crodell/fwf/data/eccc
#####

#STEPS=( 000 006 012 018 024 030 036 042 048 054 060 066 072 078 084 090 096 102 108 114 120 )
#STEPS=( 0 6 12 18 24 30 36 42 48 54 60 66 72 78 84 90 96 102 108 114 120 )

###  Main  ###
echo
log_msg "Starting $0 ..."

# Check that remote host is up
# TODO implement counter to give up after 10 min
if [[ ! $(/opt/local/bin/wget -O /dev/null -q ${SRCE_ROOT} && echo $?) ]]; then
    title="GEM remote host is not available"
    body="wget can not reach ${SRCE_ROOT} = $0 Host = $(whoami)@$(hostname -s)"
    # ./slack.sh -c "#wrf_slack_test" -u "$(whoami)@$(hostname -s)" -s HIGH -t "${title}" "${body}"
    echo "ERROR - ${SRCE_ROOT} is not available."
    log_msg "$0 halted, exiting."
    echo
    exit 1
fi

# Set date & time of forecast to download
year=${date:0:4}
datetime="${date}${hour}"

# Build source & destination directories
dest_dir="${DEST_ROOT}"
#test -d ${dest_dir} || mkdir -pv ${dest_dir}
#test -d ${dest_dir} || rm -r ${dest_dir}
[[ ! -d ${dest_dir} ]] || rm -r ${dest_dir}

mkdir -pv ${dest_dir}
cd ${dest_dir}

#srce_dir=${SRCE_ROOT}/000
#/opt/local/bin/wget -nc -v -nd -nH -np -r -A '*TMP_ISBL*,*UGRD_ISBL*,*VGRD_ISBL*,*SPFH_ISBL*,*HGT_ISBL*,*PRES_SFC*,*TGL_2*,*PRMSL_MSL*,*DPT_IGL*,*SPFH_SFC*,*SNOD_SFC*' $srce_dir/

# Get the files
for each_step in ${STEPS[@]}; do
    step=$(printf %03d $each_step)
    #echo $step
    srce_dir="${SRCE_ROOT}/${step}"
    #get_file ${srce_dir} CMC_glb_HGT_ISBL_985_latlon.24x.24_${datetime}_P${step}.grib2
    /opt/local/bin/wget --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 0 -nc -v -nd -nH -np -r -A '*TMP*,*UGRD*,*VGRD*,*SPFH*,*RH*,*HGT*,*PRES_SFC*,*TGL_2*,*PRMSL_MSL*,*DPT_IGL*,*SNOD_SFC*,*SKIN*,*SOIL*' $srce_dir/
    cat *_P${step}*grib2 > gem.${datetime}.master.f${step}
    rm -f *_P${step}.grib2
    touch gem.${datetime}.mstr.f${step}.OK
done

# Clean up & exit
touch IC.OK
log_msg "$0 is done."
echo
exit 0
