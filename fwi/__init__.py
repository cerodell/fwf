from pathlib import Path
import sys
import re
import site

#
# open the VERSION file and read it into fwi.__version__
# https://github.com/pypa/setuptools/issues/1316
#
__version_file__ = Path(__file__).parent / Path("VERSION")
#
#  if __version_file__ doesn't exist, try to create it and
#  write 'no_version', if that doesn't work (no write permission), set
#  __version_file__ to None
#
if not __version_file__.is_file():
    __version__ = "dev0"
    try:
        with open(__version_file__, "w") as f:
            f.write(f'__version__ = "{__version__}"')
    except:
        __version_file__ = None
else:
    with open(__version_file__) as f:
        version_string = f.read()
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", version_string, re.M
        )
        if version_match:
            __version__ = version_match.group(1)
        else:
            raise RuntimeError('expecting __version__ = "0.0.1" format')
#
# define two Path variables to help navigate the folder tree
# notebooks_dir and data_dir
#
path = Path(__file__).resolve()
# notebooks_dir = path.parent.parent / Path("notebooks")
root_dir = path.parent.parent
data_dir = root_dir / Path("data")
xr_dir = root_dir / Path("data/xr/")
wrf_dir = root_dir / Path("data/wrf/")
for the_dir in [data_dir, xr_dir, wrf_dir]:
    if not the_dir.is_dir():
        print(f"creating {the_dir}")
        the_dir.mkdir(parents=True, exist_ok=True)

print(f"through {__file__} pha II")