#!/Users/crodell/miniconda3/envs/fwf/bin/python


import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth


# Define the URL of the directory listing page
url = (
    "https://mft.sdstate.edu/public/folder/uVoriLnMm0Sgb8E_JBjiZQ/NorthAmerica/2021/04/"
)
# Send an HTTP GET request to the website
response = requests.get(url, headers={"Password": "RAVE@SDSU"})
# response = requests.get(url, auth=HTTPBasicAuth('', "RAVE@SDSU"))

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # Example: Find all <a> tags (links) on the page
    links = soup.find_all("a")

    # Example: Print the URLs of all the links
    for link in links:
        print(link.get("href"))
else:
    print("Failed to retrieve webpage. Status code:", response.status_code)


# from ftplib import FTP
# from pathlib import Path

# ftp = FTP("ftp.avl.class.noaa.gov")
# ftp.login()
# ftp.cwd("304460/8371261208/001/")
# # Get all files
# files = ftp.nlst()

# # Download all the files to C:\Temp
# for file in files[2:]:
#     print("Downloading:   " + file)
#     ftp.retrbinary(
#         f"RETR {file}", open(str(Path(r"/Volumes/WFRT-Ext24/rave") / file), "wb").write
#     )
# # ftp.close()
