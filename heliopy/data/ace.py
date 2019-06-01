"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/.
The ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
"""
from heliopy.data import cdasrest


def _docstring(identifier, extra):
    return cdasrest._docstring(identifier, 'A', extra)


def _ace(starttime, endtime, identifier, warn_missing_units=True):
    """
    Generic method for downloading ACE data.
    """
    badvalues = 1e-31
    return cdasrest.CDASDwonloader('ac', identifier, 'ace', badvalues=badvalues,
                                   warn_missing_units=warn_missing_units)


# Actual download functions start here
def mfi_h0(starttime, endtime):
    identifier = 'AC_H0_MFI'
    return _ace(starttime, endtime, identifier).load(starttime, endtime)


mfi_h0.__doc__ = _docstring('AC_H0_MFI', '16-second magnetic field')


def mfi_h1(starttime, endtime):
    identifier = 'AC_H1_MFI'
    return _ace(starttime, endtime, identifier).load(starttime, endtime)


mfi_h1.__doc__ = _docstring('AC_H1_MFI', '4-minute magnetic field')


def mfi_h2(starttime, endtime):
    identifier = 'AC_H2_MFI'
    return _ace(starttime, endtime, identifier).load(starttime, endtime)


mfi_h2.__doc__ = _docstring('AC_H2_MFI', '1-hour magnetic field')


def mfi_h3(starttime, endtime):
    identifier = 'AC_H3_MFI'
    return _ace(starttime, endtime, identifier).load(starttime, endtime)


mfi_h3.__doc__ = _docstring('AC_H3_MFI', '1-second magnetic field')


def swe_h0(starttime, endtime):
    identifier = 'AC_H0_SWE'
    return _ace(starttime, endtime, identifier).load(starttime, endtime)


swe_h0.__doc__ = _docstring('AC_H0_SWE', '64-second particle moments')


def swe_h2(starttime, endtime):
    identifier = 'AC_H2_SWE'
    dl = _ace(starttime, endtime, identifier, warn_missing_units=False)
    dl.intervals = cdasrest._year_intervals
    return dl.load(starttime, endtime)


swe_h2.__doc__ = _docstring('AC_H2_SWE', '1-hour particle moments')


def swi_h2(starttime, endtime):
    identifier = 'AC_H2_SWI'
    dl = _ace(starttime, endtime, identifier, warn_missing_units=False)
    dl.intervals = cdasrest._year_intervals
    return dl.load(starttime, endtime)


swi_h2.__doc__ = _docstring('AC_H2_SWI', '1-hour composition')


def swi_h3(starttime, endtime):
    identifier = 'AC_H3_SWI'
    dl = _ace(starttime, endtime, identifier, warn_missing_units=False)
    dl.intervals = cdasrest._year_intervals
    return dl.load(starttime, endtime)


swi_h3.__doc__ = _docstring('AC_H3_SWI', '2-hour composition')


def swi_h3b(starttime, endtime):
    identifier = 'AC_H3_SW2'
    dl = _ace(starttime, endtime, identifier)
    dl.intervals = cdasrest._year_intervals
    return dl.load(starttime, endtime, warn_missing_units=False)


swi_h3b.__doc__ = _docstring(
    'AC_H3_SW2', '2-hour composition (Post 2011-08-23)')


def swi_h4(starttime, endtime):
    identifier = 'AC_H4_SWI'
    dl = _ace(starttime, endtime, identifier, warn_missing_units=False)
    dl.intervals = cdasrest._year_intervals
    return dl.load(starttime, endtime)


swi_h4.__doc__ = _docstring('AC_H4_SWI', '1-day composition')


def swi_h5(starttime, endtime):
    identifier = 'AC_H5_SWI'
    dl = _ace(starttime, endtime, identifier, warn_missing_units=False)
    dl.intervals = cdasrest._year_intervals
    return dl.load(starttime, endtime)


swi_h5.__doc__ = _docstring('AC_H5_SWI', '2-hour charge state')


def swi_h6(starttime, endtime):
    identifier = 'AC_H6_SWI'
    return _ace(starttime, endtime, identifier, warn_missing_units=False).load(starttime, endtime)


swi_h6.__doc__ = _docstring('AC_H6_SWI', '12-minute protons')
