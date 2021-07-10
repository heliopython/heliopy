"""
Methods for importing data from the Voyager spacecraft.
"""
import astropy.units as u
from heliopy.data import cdasrest


def _docstring(identifier, description):
    return cdasrest._docstring(identifier, 'V', description)


def _voyager(starttime, endtime, identifier, spacecraft):
    """
    Generic method for downloading Voyager data.
    """
    dl = cdasrest.CDASDwonloader(f'VOYAGER{spacecraft}', identifier, 'voyager')
    dl.intervals = dl.intervals_yearly
    return dl.load(starttime, endtime)


# Actual download functions start here
def voyager1_merged(starttime, endtime):
    identifier = 'VOYAGER1_COHO1HR_MERGED_MAG_PLASMA'
    return _voyager(starttime, endtime, identifier, 1)


voyager1_merged.__doc__ = _docstring(
    'VOYAGER1_COHO1HR_MERGED_MAG_PLASMA',
    'Voyager 1 merged hourly magnetic field, plasma, proton fluxes, '
    'and ephemeris data')


def voyager2_merged(starttime, endtime):
    identifier = 'VOYAGER2_COHO1HR_MERGED_MAG_PLASMA'
    return _voyager(starttime, endtime, identifier, 2)


voyager2_merged.__doc__ = _docstring(
    'VOYAGER2_COHO1HR_MERGED_MAG_PLASMA',
    'Voyager 2 merged hourly magnetic field, plasma, proton fluxes, '
    'and ephemeris data')
