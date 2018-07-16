"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/. The
ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
"""
from collections import OrderedDict
import pathlib as path

import astropy.units as u
import pandas as pd

from heliopy import config
from heliopy.data import util

data_dir = path.Path(config['download_dir'])
ace_dir = data_dir / 'ace'
remote_ace_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/ace/'
remote_cda_dir = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/ace/'


def _ace(starttime, endtime, instrument, product, fname, units=None,
         version='01', badvalues={}):
    """
    Generic method for downloading ACE data from cdaweb.
    """
    # Directory relative to main WIND data directory
    relative_dir = path.Path(instrument) / 'level_2_cdaweb' / product
    daylist = util._daysplitinterval(starttime, endtime)
    dirs = []
    fnames = []
    extension = '.cdf'
    for day in daylist:
        date = day[0]
        filename = 'ac_{}_{}{:02}{:02}_v{}'.format(
            fname, date.year, date.month, date.day, version)
        fnames.append(filename)
        this_relative_dir = relative_dir / str(date.year)
        dirs.append(this_relative_dir)

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, extension):
        def check_exists():
            # Because the version might be different to the one we guess, work
            # out the downloaded filename
            for f in (local_base_dir / directory).iterdir():
                fstr = str(f.name)
                if (fstr[:-6] == (fname + extension)[:-6]):
                    # Return filename with '.cdf' stripped off the end
                    return fstr[:-4]
        if check_exists() is not None:
            return check_exists()

        # Now load remotely
        util.load(fname + extension,
                  local_base_dir / directory,
                  remote_base_url + str(directory), guessversion=True)
        return check_exists()

    def processing_func(cdf):
        return util.cdf2df(cdf, index_key='Epoch',
                           badvalues=badvalues)

    return util.process(dirs, fnames, extension, ace_dir, remote_ace_dir,
                        download_func, processing_func, starttime,
                        endtime, units=units)


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
    instrument = 'mag'
    product = 'mfi_h0'
    fname = 'h0_mfi'
    version = '06'
    units = OrderedDict([('Q_FLAG', u.dimensionless_unscaled)])
    return _ace(starttime, endtime, instrument, product,
                fname, units=units, version=version)


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
    instrument = 'swepam'
    product = 'swe_h0'
    fname = 'h0_swe'
    version = '06'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname,
                version=version, badvalues=badvalues)


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
    instrument = 'swics'
    product = 'swi_h2'
    fname = 'h2_swi'
    version = '09'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname,
                version=version, badvalues=badvalues)


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
    instrument = 'swics'
    product = 'swi_h3'
    fname = 'h3_swi'
    version = '01'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname,
                version=version, badvalues=badvalues)


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
    instrument = 'swics'
    product = 'swi_h6'
    fname = 'h6_swi'
    version = '09'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname,
                version=version, badvalues=badvalues)
