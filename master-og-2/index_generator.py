#!/bluesky/fireweather/miniconda3/envs/fwf/bin/python

import context
import logging
from shell import shell
from pathlib import Path
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import html_dir, ops_dir


forecast_start_date = date.today()
forecast_end_date   = forecast_start_date + timedelta(days=2)
folderdate = forecast_start_date.strftime('%Y%m%d00')

forecast_start_date = forecast_start_date.strftime('%Y-%m-%dT00:00:00Z')
forecast_end_date   = forecast_end_date.strftime('%Y-%m-%dT00:00:00Z')

files_datetime    = folderdate
print(f"{str(datetime.now())} ---> open/read html template" )
fcst_template = str(html_dir) + "/fwf-forecast-template-og.html"
with open(fcst_template, 'r') as fin:
    fcst = fin.read()
    ## update timedim start and end
    fcst = fcst.replace('{%FirstDateTime%}', forecast_start_date)
    fcst = fcst.replace('{%LastDateTime%}', forecast_end_date)
    ## update line plot dir for fwf32km
    line_plot = f"fwf-32km-{files_datetime}.json"
    fcst = fcst.replace('{%FWFLineForecast32km%}', line_plot)
    ## update line plot dir for fwf32km
    line_plot = f"fwf-16km-{files_datetime}.json"
    fcst = fcst.replace('{%FWFLineForecast16km%}', line_plot)
    ## update line plot dir for fwf32km
    line_plot = f"fwf-4km-{files_datetime}.json"
    fcst = fcst.replace('{%FWFLineForecast4km%}', line_plot)
    ## update ffmc geo dir
    ffmc = f"ffmc-{files_datetime}.json"
    fcst = fcst.replace('{%FirstFFMCForecast%}', ffmc)
    ## update dmc geo dir
    dmc = f"dmc-{files_datetime[:-2]}.json"
    fcst = fcst.replace('{%FirstDMCForecast%}', dmc)
    ## update dc geo dir
    dc = f"dc-{files_datetime[:-2]}.json"
    fcst = fcst.replace('{%FirstDCForecast%}', dc)
    ## update isi geo dir
    isi = f"isi-{files_datetime}.json"
    fcst = fcst.replace('{%FirstISIForecast%}', isi)
    ## update bui geo dir
    bui = f"bui-{files_datetime[:-2]}.json"
    fcst = fcst.replace('{%FirstBUIForecast%}', bui)
    ## update fwi geo dir
    fwi = f"fwi-{files_datetime}.json"
    fcst = fcst.replace('{%FirstFWIForecast%}', fwi)

    make_dir = Path(str(ops_dir) + '/' + str(folderdate))
    # make_dir.mkdir(parents=True, exist_ok=True)
    out_dir = str(make_dir) + '/index.html' 
    with open(out_dir, 'w') as fout:
        fout.write(fcst)
print(f"{str(datetime.now())} ---> write index.html" )


# ### Timer
print("Run Time: ", datetime.now() - startTime)