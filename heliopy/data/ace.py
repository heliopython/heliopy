"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/. The
ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
"""
import os
import pandas as pd

from heliopy.data import helper
from heliopy import config

data_dir = config['download_dir']
ace_dir = os.path.join(data_dir, 'ace')
remote_ace_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/ace/'
remote_cda_dir = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/ace/'


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
    # Directory relative to main WIND data directory
    relative_dir = os.path.join('mag', 'level_2_cdaweb', 'mfi_h0')

    daylist = helper._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'ac_h0_mfi_{}{:02}{:02}_v06.cdf'.format(
            date.year, date.month, date.day)
        this_relative_dir = os.path.join(relative_dir, str(date.year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(ace_dir, this_relative_dir)
        helper.checkdir(local_dir)

        remote_url = remote_ace_dir + this_relative_dir
        cdf = helper.load(filename, local_dir, remote_url, guessversion=True)

        keys = {'BGSEc': ['Bx_gse', 'By_gse', 'Bz_gse'],
                'Magnitude': '|B|',
                'SC_pos_GSE': ['sc_gse_x', 'sc_gse_y', 'sc_gse_z'],
                'Epoch': 'Time'}
        badvalues = {}
        df = helper.cdf2df(cdf,
                           index_key='Epoch',
                           keys=keys,
                           badvalues=badvalues)
        data.append(df)

    data = helper.timefilter(data, starttime, endtime)
    return data


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
    # Directory relative to main WIND data directory
    relative_dir = os.path.join('swepam', 'level_2_cdaweb', 'swe_h0')

    daylist = helper._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'ac_h0_swe_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v06.cdf'
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(ace_dir, this_relative_dir)
        helper.checkdir(local_dir)

        remote_url = remote_cda_dir + this_relative_dir
        cdf = helper.load(filename, local_dir, remote_url, guessversion=True)

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
        badvalues = {}
        df = helper.cdf2df(cdf,
                           index_key='Epoch',
                           keys=keys,
                           badvalues=badvalues)
        data.append(df)

    data = helper.timefilter(data, starttime, endtime)
    return data
