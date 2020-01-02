import site
import sys

def add_path():
    """
    find the full path to the directory above this one and
    add it to sys.path so we can import local modules 
    """
    the_path = Path('..').resolve()
    print(f'adding {the_path} to sys.path')
    sys.path.insert(0, str(the_path))
    site.removeduppaths()