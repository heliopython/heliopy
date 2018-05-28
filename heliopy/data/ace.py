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


def _ace(starttime, endtime, instrument, product, fname, units=None, keys=None,
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
                           keys=keys, badvalues=badvalues)

    if units is None:
        units = keys
    return util.process(dirs, fnames, extension, ace_dir, remote_ace_dir,
                        download_func, processing_func, starttime,
                        endtime, units=keys)


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
    data : DataFrame
    """
    instrument = 'mag'
    product = 'mfi_h0'
    fname = 'h0_mfi'
    keys = {'Magnitude': 'Magnitude',
            'SC_pos_GSE': ['sc_gse_x', 'sc_gse_y', 'sc_gse_z'],
            'SC_pos_GSM': ['sc_gsm_x', 'sc_gsm_y', 'sc_gsm_z'],
            'BGSEc': ['BGSE_x', 'BGSE_y', 'BGSE_z'],
            'BGSM': ['BGSM_x', 'BGSM_y', 'BGSM_z'],
            'dBrms': 'dBrms',
            'Q_FLAG': 'Q_FLAG',
            'Epoch': 'Time'}
    version = '06'
    return _ace(starttime, endtime, instrument, product,
                fname, keys=keys, version=version)


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
    data : DataFrame
    """
    instrument = 'swepam'
    product = 'swe_h0'
    fname = 'h0_swe'
    keys = {'Np': 'n_p',
            'Tpr': 'T_pr',
            'SC_pos_GSE': ['sc_gse_x', 'sc_gse_y', 'sc_gse_z'],
            'SC_pos_GSM': ['sc_gsm_x', 'sc_gsm_y', 'sc_gsm_z'],
            'V_GSE': ['vp_gse_x', 'vp_gse_y', 'vp_gse_z'],
            'V_GSM': ['vp_gsm_x', 'vp_gsm_y', 'vp_gsm_z'],
            'V_RTN': ['vp_rtn_r', 'vp_rtn_t', 'vp_rtn_n'],
            'Vp': '|vp|',
            'alpha_ratio': 'n_a/n_p',
            'Epoch': 'Time'}
    version = '06'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname, keys=keys,
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
    data : DataFrame
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
    data : DataFrame
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
    data : DataFrame
    """
    instrument = 'swics'
    product = 'swi_h6'
    fname = 'h6_swi'
    version = '09'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname,
                version=version, badvalues=badvalues)
