"""
Methods for importing data from the Messenger spacecraft.
"""
import pathlib as path

from heliopy import config
from heliopy.data import cdasrest

data_dir = path.Path(config['download_dir'])
mess_dir = data_dir / 'messenger'


def _messenger(starttime, endtime, identifier, units=None, badvalues=None,
               warn_missing_units=True):
    """
    Generic method for downloading IMP8 data.
    """
    dataset = 'messenger'
    return cdasrest._process_cdas(starttime, endtime, identifier, dataset,
                                  mess_dir,
                                  units=units,
                                  badvalues=badvalues,
                                  warn_missing_units=warn_missing_units)


def _docstring(identifier, extra):
    return cdasrest._docstring(identifier, 'M', extra)


def mag_rtn(starttime, endtime):
    identifier = 'MESSENGER_MAG_RTN'
    return _messenger(starttime, endtime, identifier, warn_missing_units=False)


mag_rtn.__doc__ = _docstring('MESSENGER_MAG_RTN', 'magnetic field')
