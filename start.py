"""Naval Fate.

Usage:
  start.py [set_manual_settings] [use_proxy] [use_tg]
  start.py (-h | --help)
  start.py --version

Options:
  -h --help      Show this screen.
  --version      Show version.

"""
from docopt import docopt

from src.main import start


__version__ = "0.9.1"


if __name__ == "__main__":
    arguments = docopt(__doc__, version=f"version {__version__}")
    start(arguments)
