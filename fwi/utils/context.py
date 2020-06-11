"""
define the path to important folders without having
to install anything -- just do:
import contenxt
then the path for the data directory is
context.data_dir
"""
import sys
import site
from pathlib import Path

path = Path(__file__).resolve()  # this file
this_dir = path.parent  # this folder
notebooks_dir = this_dir
root_dir = notebooks_dir.parent
data_dir = root_dir / Path("data")
tzone_dir = root_dir / Path("data/tzone/")
xr_dir   = root_dir / Path("data/xr/")


wrf_dir = Path("/nfs/kitsault/archives/forecasts/WAN00CP-04/")
# xr_dir = Path("/bluesky/archive/fireweather/")


sys.path.insert(0, str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n{sys.path[1]}\n{sep}\n")


print(f"through {__file__} -- pha")