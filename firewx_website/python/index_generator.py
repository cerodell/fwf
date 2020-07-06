import context
import logging
from shell import shell
from pathlib import Path
from datetime import datetime, date, timedelta
startTime = datetime.now()

from context import html_dir, ops_dir

# logger = logging.getLogger(__name__)
# LOG_LEVELS = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
# LOG_DIR    = '/bluesky/fireweather/fwf/logs'



forecast_start_date = date.today()
forecast_end_date   = forecast_start_date + timedelta(days=2)
folder = forecast_start_date.strftime('%Y%m%d00')

forecast_start_date = forecast_start_date.strftime('%Y-%m-%dT00:00:00Z')
forecast_end_date   = forecast_end_date.strftime('%Y-%m-%dT00:00:00Z')

files_datetime    = forecast_start_date[:-7]

fcst_template = str(html_dir) + "/fwf-forecast-template.html"
with open(fcst_template, 'r') as fin:
    fcst = fin.read()
    ## update timedim start and end
    fcst = fcst.replace('{%FirstDateTime%}', forecast_start_date)
    fcst = fcst.replace('{%LastDateTime%}', forecast_end_date)
    ## update line plot dir
    line_plot = f"fwf-line-{files_datetime}.json"
    fcst = fcst.replace('{%FWFLineForecast%}', line_plot)
    ## update ffmc geo dir
    ffmc = f"fwf-ffmc-{files_datetime}.geojson"
    fcst = fcst.replace('{%FirstFFMCForecast%}', ffmc)
    ## update dmc geo dir
    dmc = f"fwf-dmc-{files_datetime}.geojson"
    fcst = fcst.replace('{%FirstDMCForecast%}', dmc)
    ## update dc geo dir
    dc = f"fwf-dc-{files_datetime}.geojson"
    fcst = fcst.replace('{%FirstDCForecast%}', dc)
    ## update isi geo dir
    isi = f"fwf-isi-{files_datetime}.geojson"
    fcst = fcst.replace('{%FirstISIForecast%}', isi)
    ## update bui geo dir
    bui = f"fwf-bui-{files_datetime}.geojson"
    fcst = fcst.replace('{%FirstBUIForecast%}', bui)
    ## update fwi geo dir
    fwi = f"fwf-fwi-{files_datetime}.geojson"
    fcst = fcst.replace('{%FirstFWIForecast%}', fwi)

    make_dir = Path(str(ops_dir) + '/' + str(folder))
    make_dir.mkdir(parents=True, exist_ok=True)
    out_dir = str(make_dir) + '/fwf-forecast.html' 
    with open(out_dir, 'w') as fout:
        fout.write(fcst)

# Link default page to correct forecast page
# command = "ln -fnsv fwf-forecast.html {}/index.html".format(out_dir)
# shell(command)