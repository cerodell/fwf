#!/bin/bash

# Define variables
SFTP_SERVER="technosylva@s-14b17278a13148339.server.transfer.us-east-1.amazonaws.com"
PRIVATE_KEY="/home/crodell/.ssh/dtn_key"
LOCAL_PATH="/NASPANGEA/WRF/Fortis_Alberta_forecast/"
START_DATE="20250306"
END_DATE="20250314"

get /wrf/tsalb/all_wrf2d_d03_2025030700MT.nc /NASPANGEA/WRF/Fortis_Alberta_forecast/
get /wrf/tsalb/all_wrf2d_d03_2025031100MT.nc /NASPANGEA/WRF/Fortis_Alberta_forecast/
get /wrf/tsalb/all_wrf2d_d03_2025031200MT.nc /NASPANGEA/WRF/Fortis_Alberta_forecast/

# Convert to seconds for looping
CURRENT_DATE=$(date -d "$START_DATE" +%s)
END_DATE_SECONDS=$(date -d "$END_DATE" +%s)

# Loop through the date range
while [ "$CURRENT_DATE" -le "$END_DATE_SECONDS" ]; do
    # Format date as YYYYMMDD
    DATE_STR=$(date -d "@$CURRENT_DATE" +%Y%m%d)

    echo "Fetching file for date: $DATE_STR"

    # Start SFTP with the private key
    sftp -i "$PRIVATE_KEY" "$SFTP_SERVER" <<EOF
get /wrf/tsalb/all_wrf2d_d03_${DATE_STR}00MT.nc $LOCAL_PATH
bye
EOF

    # Increment by one day
    CURRENT_DATE=$((CURRENT_DATE + 86400))
done

echo "Download completed."



get /wrf/tsalb/all_wrf2d_d03_2025032000MT.nc /NASPANGEA/WRF/Fortis_Alberta_forecast/
