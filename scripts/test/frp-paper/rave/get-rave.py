#!/Users/crodell/miniconda3/envs/fwx/bin/python

import requests
from bs4 import BeautifulSoup
import os
import subprocess
from urllib.parse import urljoin

# URL of the page
url = "https://order.class.noaa.gov/downloads/public/8411195273/001/"

# Make a request to fetch the content of the page
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find all links that end with .nc
file_links = [
    urljoin(url, link.get("href"))
    for link in soup.find_all("a")
    if link.get("href").endswith(".nc")
]

# Directory to save downloaded files
download_dir = "/Users/crodell/Desktop/RAVE/"
os.makedirs(download_dir, exist_ok=True)

# Download each file
# Download each file using wget
for file_link in file_links:
    file_name = os.path.join(download_dir, os.path.basename(file_link))
    if os.path.isfile(file_name):
        print(f"File previously downloaded {file_name}")
    else:
        print(f"Downloading {file_name}")
        subprocess.run(["wget", "-P", download_dir, file_link])


print("All files downloaded.")
