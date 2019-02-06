"""
Methods for importing data from the STEREO spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/stereo/.
The STEREO spacecraft homepage can be found at https://stereo.gsfc.nasa.gov/.
"""
from collections import OrderedDict
import pathlib as path

import astropy.units as u
import pandas as pd

from heliopy import config
from heliopy.data import cdasrest

data_dir = path.Path(config['download_dir'])
ace_dir = data_dir / 'stereo'


def _docstring(identifier, extra):
    return cdasrest._docstring_stereo(identifier, 'S', extra)

def _identifier_select(spacecraft):
    """
    Spacecraft selector for stereo
    """

    if spacecraft == 'sta':
        return 'STA'
    elif spacecraft == 'stb':
        return 'STB'
    else:
        raise ValueError("Invalid spacecraft, must be sta or stb")


def _stereo(starttime, endtime, dataset, identifier, units=None,
            warn_missing_units=True):
    """
    Generic method for downloading STEREO data.
    """
    badvalues = 1e-31
    return cdasrest._process_cdas(starttime, endtime, identifier, dataset,
                                  ace_dir,
                                  units=units,
                                  badvalues=badvalues,
                                  warn_missing_units=warn_missing_units)


# Actual download functions start here
def mag_l1_rtn(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_MAG_RTN'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


mag_l1_rtn.__doc__ = _docstring('STA_L1_MAG_RTN',
                                    'STEREO IMPACT/MAG Magnetic Field Vectors')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


mag_l1_rtn.__doc__ = _docstring('STA_L2_MAGPLASMA_1M', 'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data')


def magplasma_l2(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L2_MAGPLASMA_1M'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


magplasma_l2.__doc__ = _docstring('STA_L2_MAGPLASMA_1M', 'STEREO IMPACT/MAG Magnetic Field and PLASTIC Solar Wind Plasma Data')


def let_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_LET'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


let_l1.__doc__ = _docstring('STA_L1_LET',
                            'STEREO IMPACT/LET Level 1 Data')

def sept_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_SEPT'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


sept_l1.__doc__ = _docstring('STA_L1_SEPT',
                            'STEREO IMPACT/SEPT Level 1 Data')


def sit_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_SIT'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


sit_l1.__doc__ = _docstring('STA_L1_SIT',
                            'STEREO IMPACT/SIT Level 1 Data')


def ste_l1(starttime, endtime, spacecraft):
    identifier = _identifier_select(spacecraft)+'_L1_STE'

    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _stereo(starttime, endtime, spacecraft, identifier, units=units)


ste_l1.__doc__ = _docstring('STA_L1_STE',
                            'STEREO IMPACT/STE Level 1 Data')
