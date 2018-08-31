"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/.
The ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
"""
from collections import OrderedDict
import pathlib as path
import re

import astropy.units as u
import pandas as pd

from heliopy import config
from heliopy.data import util
from heliopy.data import cdasrest

data_dir = path.Path(config['download_dir'])
ace_dir = data_dir / 'ace'
remote_ace_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/ace/'
remote_cda_dir = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/ace/'


def _docstring(identifier, extra=''):
    ds = r"""
    Import {extra} data.

    See https://cdaweb.sci.gsfc.nasa.gov/misc/NotesA.html#{identifier}
    for more information.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """.format(identifier=identifier,
               extra=extra)
    return ds


def _ace(starttime, endtime, identifier, units=None):
    """
    Generic method for downloading ACE data.
    """
    badvalues = -1e31
    relative_dir = path.Path(identifier)
    # Directory relative to main WIND data directory
    daylist = util._daysplitinterval(starttime, endtime)
    dirs = []
    fnames = []
    dates = []
    extension = '.cdf'
    for day in daylist:
        date = day[0]
        dates.append(date)
        filename = 'ac_{}_{}{:02}{:02}'.format(
            identifier, date.year, date.month, date.day)
        fnames.append(filename)
        this_relative_dir = relative_dir / str(date.year)
        dirs.append(this_relative_dir)

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension, date):
        return cdasrest.get_data(identifier, date)

    def processing_func(cdf):
        return util.cdf2df(cdf, index_key='Epoch',
                           badvalues=badvalues)

    return util.process(dirs, fnames, extension, ace_dir, remote_ace_dir,
                        download_func, processing_func, starttime,
                        endtime, units=units, download_info=dates)


# Actual download functions start here
def mfi_h0(starttime, endtime):
    identifier = 'AC_H0_MFI'
    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _ace(starttime, endtime, identifier, units=units)


mfi_h0.__doc__ = _docstring('AC_H0_MFI', '16-second magnetic field')


def mfi_h1(starttime, endtime):
    identifier = 'AC_H1_MFI'
    return _ace(starttime, endtime, identifier)


mfi_h1.__doc__ = _docstring('AC_H1_MFI', '4-minute magnetic field')


def mfi_h2(starttime, endtime):
    identifier = 'AC_H2_MFI'
    return _ace(starttime, endtime, identifier)


mfi_h2.__doc__ = _docstring('AC_H2_MFI', 'hourly magnetic field')


def mfi_h3(starttime, endtime):
    identifier = 'AC_H3_MFI'
    return _ace(starttime, endtime, identifier)


mfi_h3.__doc__ = _docstring('AC_H3_MFI', '1-second magnetic field')


def swe_h0(starttime, endtime):
    identifier = 'AC_H0_SWE'
    return _ace(starttime, endtime, identifier)


swe_h0.__doc__ = _docstring('AC_H0_SWE', '64-second particle moments')


def swe_h2(starttime, endtime):
    identifier = 'AC_H2_SWE'
    return _ace(starttime, endtime, identifier)


swe_h2.__doc__ = _docstring('AC_H2_SWE', '1-hour particle moments')


def swi_h2(starttime, endtime):
    identifier = 'AC_H2_SWI'
    return _ace(starttime, endtime, identifier)


swi_h2.__doc__ = _docstring('AC_H2_SWI', 'composition')


def swi_h3(starttime, endtime):
    identifier = 'AC_H3_SWI'
    return _ace(starttime, endtime, identifier)


swi_h3.__doc__ = _docstring('AC_H3_SWI', 'hourly composition')


def swi_h6(starttime, endtime):
    identifier = 'AC_H6_SWI'
    return _ace(starttime, endtime, identifier)


swi_h6.__doc__ = _docstring('AC_H6_SWI', '12 minute proton')
