import pathlib

__author__ = 'EAMY'
__email__ = 'team@eamy.org'
__version__ = '0.1.0'

from . import config

datapath = pathlib.Path('.').resolve().joinpath(config.DATADIR)
config.DATADIR = str(datapath)
config.PIDFILE = str(datapath.joinpath(config.PIDFILE))
config.LOGFILE = str(datapath.joinpath(config.LOGFILE))
