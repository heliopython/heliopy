"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/. The
ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
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


def _ace(starttime, endtime, identifier, units=None, badvalues={}):
    """
    Generic method for downloading ACE data.
    """
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


def mfi_h0(starttime, endtime):
    """
    Import 'mfi_h0' magnetic field data product from ACE. See
    ftp://spdf.gsfc.nasa.gov/pub/data/ace/mag/ for more information.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """
    identifier = 'AC_H0_MFI'
    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _ace(starttime, endtime, identifier, units=units)


def swe_h0(starttime, endtime):
    """
    Import swe_h0 particle moment data product from ACE. See
    https://cdaweb.sci.gsfc.nasa.gov/misc/NotesA.html#AC_H0_SWE
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
    """
    identifier = 'AC_H0_SWE'
    badvalues = -1e31
    return _ace(starttime, endtime, identifier, badvalues=badvalues)


def swi_h2(starttime, endtime):
    """
    Import hourly SWICS data.

    See https://cdaweb.sci.gsfc.nasa.gov/misc/NotesA.html#AC_H2_SWI for more
    information.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """
    identifier = 'AC_H2_SWI'
    badvalues = -1e31
    return _ace(starttime, endtime, identifier, badvalues=badvalues)


def swi_h3(starttime, endtime):
    """
    Import hourly SWICS composition data.

    See https://cdaweb.sci.gsfc.nasa.gov/misc/NotesA.html#AC_H3_SWI for more
    information.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """
    identifier = 'AC_H3_SWI'
    badvalues = -1e31
    return _ace(starttime, endtime, identifier, badvalues=badvalues)


def swi_h6(starttime, endtime):
    """
    Import 12 minute SWICS proton data.

    See https://cdaweb.sci.gsfc.nasa.gov/misc/NotesA.html#AC_H6_SWI for more
    information.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
    """
    identifier = 'AC_H6_SWI'
    badvalues = -1e31
    return _ace(starttime, endtime, identifier, badvalues=badvalues)
