"""
Define the path to important folders without having
 to install anything -- just do:

import context

then the path for the data directory is

context.data_dir

"""
import sys
import site
from pathlib import Path

path = Path(__file__).resolve()  # this file
this_dir = path.parent  # this folder
notebooks_dir = this_dir
root_dir = notebooks_dir.parents[0]
data_dir = root_dir / Path("data")
json_dir = root_dir / Path("json")

tzone_dir = root_dir / Path("data/tzone/")
html_dir = root_dir / Path("fwf-web/static/html/")
ops_dir = Path("/bluesky/archive/fireweather/forecasts/")
wrf_dir = Path("/bluesky/working/wrf2arl/WAN00CG-01/")


sys.path.insert(0, str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n{sys.path[1]}\n{sep}\n")


print(f"through {__file__} -- pha")
