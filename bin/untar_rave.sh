#!/bin/bash


for y in {2020..2023}; do
    for m in {1..12}; do
        if (( m < 10 )); then
            month=""0"$m"
        else
            month="$m"
        fi
      directory="/Volumes/WFRT-Ext24/rave/"$y"/"$month""
      # Check if the directory exists
      if [ -d "$directory" ]; then
          # Directory exists, do something
          echo "Directory exists. Untaring files"
          # Insert your action here
          echo "$directory"
          for tarball in "$directory"/*.tar.gz; do
              # Check if the file is a regular file
              if [ -f "$tarball" ]; then
                  # Untar the tarball into the same directory
                  tar -xvzf "$tarball" -C "$directory"
              fi
          done
          echo "Removing old tar files"
          cd "$directory"
          rm -rf ._RAVE-*
          rm -rf *.tar.gz
      else
          # Directory does not exist, do something else or pass
          echo "Directory does not exist. Skipping...."
          # Insert alternative action or simply pass
      fi
    done
done
