"""
Methods for importing data from the OMNI.
"""
from heliopy.data import cdasrest


def _docstring(identifier, description):
    return cdasrest._docstring(identifier, 'O', description)


def _omni(starttime, endtime, identifier, intervals='monthly',
          warn_missing_units=True):
    """
    Generic method for downloading OMNI data.
    """
    dl = cdasrest.CDASDwonloader('omni', identifier, 'omni',
                                 warn_missing_units=warn_missing_units)
    # Override intervals
    if intervals == 'daily':
        dl.intervals = dl.intervals_daily
    elif intervals == 'monthly':
        dl.intervals = dl.intervals_monthly
    elif intervals == 'yearly':
        dl.intervals = dl.intervals_yearly
    return dl.load(starttime, endtime)


# Actual download functions start here
def h0_mrg1hr(starttime, endtime):
    identifier = 'OMNI2_H0_MRG1HR'
    return _omni(starttime, endtime, identifier, warn_missing_units=False,
                 intervals='yearly')


h0_mrg1hr.__doc__ = _docstring(
    'OMNI2_H0_MRG1HR', 'Hourly averaged definitive multi-spacecraft '
                       'interplanetary parameters.')


def hro2_1min(starttime, endtime):
    identifier = 'OMNI_HRO2_1MIN'
    return _omni(starttime, endtime, identifier, warn_missing_units=False,
                 intervals='monthly')


hro2_1min.__doc__ = _docstring(
    'OMNI_HRO2_1MIN', '1 minute averaged definitive multi-spacecraft '
                      'interplanetary parameters.')


def hro2_5min(starttime, endtime):
    identifier = 'OMNI_HRO2_5MIN'
    return _omni(starttime, endtime, identifier, warn_missing_units=False,
                 intervals='monthly')


hro2_1min.__doc__ = _docstring(
    'OMNI_HRO2_5MIN', '5 minute averaged definitive multi-spacecraft '
                      'interplanetary parameters.')
