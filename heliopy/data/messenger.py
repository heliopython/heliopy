"""
Methods for importing data from the Messenger spacecraft.
"""
from heliopy.data import cdasrest


def _messenger(starttime, endtime, identifier):
    """
    Generic method for downloading IMP8 data.
    """
    dl = cdasrest.CDASDwonloader('messenger', identifier, 'messenger')
    return dl.load(starttime, endtime)


def _docstring(identifier, extra):
    return cdasrest._docstring(identifier, 'M', extra)


def mag_rtn(starttime, endtime):
    identifier = 'MESSENGER_MAG_RTN'
    return _messenger(starttime, endtime, identifier)


mag_rtn.__doc__ = _docstring('MESSENGER_MAG_RTN', 'magnetic field')
