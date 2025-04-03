#!/bin/bash

# Start the ssh-agent and add your key
eval "$(ssh-agent -s)"
ssh-add /home/$USER/.ssh/dtn_key

# Get the current date in the desired format (YYYYMMDD)
# TODAY=$(date +%Y%m%d)
TODAY="20250327"

# Define the filename with the current date, need to chage depending on dataset
FILENAME="all_wrf2d_d03_${TODAY}00MT.nc"

# Define remote server details and remote path
REMOTE_USER="technosylva"
REMOTE_SERVER="s-14b17278a13148339.server.transfer.us-east-1.amazonaws.com"
REMOTE_PATH="/wrf/tsalb/"

# Define the local path where the file will be saved
LOCAL_PATH="/NASPANGEA/WRF/Fortis_Alberta_forecast/"

# Use SFTP to retrieve the file
sftp ${REMOTE_USER}@${REMOTE_SERVER} <<EOF
get ${REMOTE_PATH}${FILENAME} ${LOCAL_PATH}
EOF

# Kill the ssh-agent to clean up
eval "$(ssh-agent -k)"

# Print a success message
echo "File transfer completed: ${FILENAME}"
