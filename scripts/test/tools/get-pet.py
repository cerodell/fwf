#!/Users/crodell/miniconda3/envs/fwx/bin/python

import subprocess
import pandas as pd


def download_data(url, output_filename):
    try:
        # Use subprocess to run wget command
        subprocess.run(["wget", url, "-O", output_filename], check=True)
        print(f"Download successful. Data saved to {output_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading data: {e}")


date_range = pd.date_range("2021", "2023", freq="Y")
# date_range = pd.date_range('2011', '2016', freq='Y')
# date_range = pd.date_range('2008', '2011', freq='Y')

for year in date_range:
    year = year.strftime("%Y")
    url = f"https://data.bris.ac.uk/datasets/qb8ujazzda0s2aykkv0oq0ctp/{year}_daily_pet.nc"  # Replace with your URL
    output_filename = f"/Volumes/WFRT-Ext23/pet/{year}_daily_pet.nc"  # Replace with your desired output file name
    download_data(url, output_filename)
