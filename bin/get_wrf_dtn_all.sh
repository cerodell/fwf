#!/bin/bash

# Start the ssh-agent and add your key
eval "$(ssh-agent -s)"
ssh-add /home/$USER/.ssh/dtn_key

# List of dates in YYYYMMDD format
DATES=("20250328" "20250329" "20250330" "20250331" "20250401")

# Define remote server details and remote path
REMOTE_USER="technosylva"
REMOTE_SERVER="s-14b17278a13148339.server.transfer.us-east-1.amazonaws.com"
REMOTE_PATH="/wrf/tsalb/"

# Define the local path where the file will be saved
LOCAL_PATH="/NASPANGEA/WRF/Fortis_Alberta_forecast/"

# Loop through each date
for TODAY in "${DATES[@]}"; do
    FILENAME="all_wrf2d_d03_${TODAY}00MT.nc"

    echo "Transferring: ${FILENAME}"

    # Use SFTP to retrieve the file
    sftp ${REMOTE_USER}@${REMOTE_SERVER} <<EOF
get ${REMOTE_PATH}${FILENAME} ${LOCAL_PATH}
EOF

    echo "Transfer complete: ${FILENAME}"
done

# Kill the ssh-agent to clean up
eval "$(ssh-agent -k)"
