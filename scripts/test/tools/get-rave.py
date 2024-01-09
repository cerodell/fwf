#!/Users/crodell/miniconda3/envs/fwf/bin/python

from ftplib import FTP
from pathlib import Path

ftp = FTP("ftp.avl.class.noaa.gov")
ftp.login()
ftp.cwd("304460/8371261208/001/")
# Get all files
files = ftp.nlst()

# Download all the files to C:\Temp
for file in files[2:]:
    print("Downloading:   " + file)
    ftp.retrbinary(
        f"RETR {file}", open(str(Path(r"/Volumes/WFRT-Ext24/rave") / file), "wb").write
    )
# ftp.close()
