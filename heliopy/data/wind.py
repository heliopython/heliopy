"""
Methods for importing data from the WIND spacecraft.
"""
import astropy.units as u
from heliopy.data import cdasrest


def _docstring(identifier, description):
    return cdasrest._docstring(identifier, 'W', description)


def _wind(starttime, endtime, identifier, units=None,
          intervals='monthly'):
    """
    Generic method for downloading ACE data.
    """
    dl = cdasrest.CDASDwonloader('wi', identifier, 'wind', units=units)
    # Override intervals
    if intervals == 'daily':
        dl.intervals = dl.intervals_daily
    else:
        dl.intervals = dl.intervals_monthly
    return dl.load(starttime, endtime)


# Actual download functions start here
def swe_h1(starttime, endtime):
    identifier = 'WI_H1_SWE'
    units = {'ChisQ_DOF_nonlin': u.dimensionless_unscaled}
    return _wind(starttime, endtime, identifier, units=units)


swe_h1.__doc__ = _docstring(
    'WI_H1_SWE', '92-second Solar Wind Alpha and Proton Anisotropy Analysis')


def mfi_h0(starttime, endtime):
    identifier = 'WI_H0_MFI'
    units = {'BGSEa_0': u.nT, 'BGSEa_1': u.nT, 'BGSEa_2': u.nT}
    return _wind(starttime, endtime, identifier, units=units,
                 intervals='daily')


mfi_h0.__doc__ = _docstring(
    'WI_H0_MFI', 'Composite magnetic field')


def mfi_h2(starttime, endtime):
    identifier = 'WI_H2_MFI'
    return _wind(starttime, endtime, identifier, intervals='daily')


mfi_h2.__doc__ = _docstring(
    'WI_H2_MFI', 'High resolution magnetic field')


def threedp_pm(starttime, endtime):
    identifier = 'WI_PM_3DP'
    return _wind(starttime, endtime, identifier, intervals='daily')


threedp_pm.__doc__ = _docstring(
    'WI_PM_3DP', '1 spin resolution ion (proton and alpha) moment')


def threedp_e0_emfits(starttime, endtime):
    identifier = 'WI_EMFITS_E0_3DP'
    return _wind(starttime, endtime, identifier)


threedp_e0_emfits.__doc__ = _docstring(
    'WI_EMFITS_E0_3DP', 'Electron moment')


def swe_h3(starttime, endtime):
    identifier = 'WI_H3_SWE'
    return _wind(starttime, endtime, identifier)


swe_h3.__doc__ = _docstring(
    'WI_H3_SWE', '12 second electron pitch angle')


def threedp_elpd(starttime, endtime):
    identifier = 'WI_ELPD_3DP'
    return _wind(starttime, endtime, identifier)


threedp_elpd.__doc__ = _docstring(
    'WI_ELPD_3DP', 'Electron pitch angle')
