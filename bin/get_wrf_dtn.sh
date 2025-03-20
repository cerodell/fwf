#!/bin/bash

# Load SSH key
eval `ssh-agent -s`
ssh-add /home/$USER/.ssh/dtn_key

# Define server and file paths
SFTP_SERVER="technosylva@s-14b17278a13148339.server.transfer.us-east-1.amazonaws.com"
REMOTE_PATH="/wrf/tsalb/all_wrf2d_d03_$(date +%Y%m%d)00MT.nc"
LOCAL_PATH="/NASPANGEA/WRF/Fortis_Alberta_forecast/"

# Use SFTP to fetch the file
sftp -oBatchMode=no -b - $SFTP_SERVER <<EOF
get $REMOTE_PATH $LOCAL_PATH
bye
EOF

# Stop SSH agent
eval `ssh-agent -k`
