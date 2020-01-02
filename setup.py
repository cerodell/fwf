from setuptools import setup, find_packages
from pathlib import Path
import re

# https://packaging.python.org/guides/single-sourcing-package-version/
root_dir = Path(__file__).parent
version_file = root_dir / 'VERSION'

package_name='fwi'

def find_version(version_file):
    # __file__ is the full path to setup.py
    version_file = Path(__file__).parent / f'{package_name}/VERSION'
    with open(version_file) as in_file:
        version_string=in_file.read()
    print(f"version string {version_string}")
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_string, re.M)
    if version_match:
        print(f"returning {version_match.group(1)}")
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name = "fwi",
    version=find_version(version_file),
    packages=find_packages(),
    entry_points={
          'console_scripts': [
              'killprocs = fwi.utils.killprocs:main',
              'pyncdump = fwi.utils.ncdump:main'
          ]
    },

)
