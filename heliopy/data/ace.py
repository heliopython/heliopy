"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/. The
ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
"""
import os
import pandas as pd

from heliopy.data import util
from heliopy import config

data_dir = config['download_dir']
ace_dir = os.path.join(data_dir, 'ace')
remote_ace_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/ace/'
remote_cda_dir = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/ace/'


def _ace(starttime, endtime, instrument, product, fname, keys, version='01',
         badvalues={}):
    """
    Generic method for downloading ACE data from cdaweb.
    """
    # Directory relative to main WIND data directory
    relative_dir = os.path.join(instrument, 'level_2_cdaweb', product)

    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'ac_{}_{}{:02}{:02}_v{}.cdf'.format(
            fname, date.year, date.month, date.day, version)
        this_relative_dir = os.path.join(relative_dir, str(date.year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(ace_dir, this_relative_dir)
        util._checkdir(local_dir)

        remote_url = remote_ace_dir + this_relative_dir
        cdf = util.load(filename, local_dir, remote_url, guessversion=True)
        if cdf is None:
            print('File {}/{} not available\n'.format(
                remote_url, filename))
            continue

        df = util.cdf2df(cdf, index_key='Epoch',
                         keys=keys, badvalues=badvalues)
        data.append(df)

    data = util.timefilter(data, starttime, endtime)
    return data


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
    keys = {'BGSEc': ['Bx_gse', 'By_gse', 'Bz_gse'],
            'Magnitude': '|B|',
            'SC_pos_GSE': ['sc_gse_x', 'sc_gse_y', 'sc_gse_z'],
            'Epoch': 'Time'}
    version = '06'
    return _ace(starttime, endtime, instrument, product, fname, keys, version)


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
    return _ace(starttime, endtime, instrument, product, fname, keys, version,
                badvalues)


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
    keys = {'Epoch': 'Time',
            'C5_qual': 'C5_qual',
            'C6to4': 'C6to4',
            'C6to4_err': 'C6to4_err',
            'C6to4_qual': 'C6to4_qual',
            'C6to5': 'C6to5',
            'C6to5_err': 'C6to5_err',
            'C6to5_qual': 'C6to5_qual',
            'Fe10_qual': 'Fe10_qual',
            'FetoO': 'FetoO',
            'FetoO_err': 'FetoO_err',
            'FetoO_qual': 'FetoO_qual',
            'He_qual': 'He_qual',
            'O6_qual': 'O6_qual',
            'O7to6': 'O7to6',
            'O7to6_err': 'O7to6_err',
            'O7to6_qual': 'O7to6_qual',
            'SW_type': 'SW_type',
            'avqC': 'avqC',
            'avqC_err': 'avqC_err',
            'avqC_qual': 'avqC_qual',
            'avqFe': 'avqFe',
            'avqFe_err': 'avqFe_err',
            'avqFe_qual': 'avqFe_qual',
            'avqMg': 'avqMg',
            'avqMg_err': 'avqMg_err',
            'avqMg_qual': 'avqMg_qual',
            'avqO': 'avqO',
            'avqO_err': 'avqO_err',
            'avqO_qual': 'avqO_qual',
            'avqSi': 'avqSi',
            'avqSi_err': 'avqSi_err',
            'avqSi_qual': 'avqSi_qual',
            'nHe2': 'nHe2',
            'nHe2_err': 'nHe2_err',
            'vC5': 'vC5',
            'vFe10': 'vFe10',
            'vHe2': 'vHe2',
            'vO6': 'vO6',
            'vthC5': 'vthC5',
            'vthFe10': 'vthFe10',
            'vthHe2': 'vthHe2',
            'vthO6': 'vthO6'}
    version = '09'
    badvalues = -1e31
    return _ace(starttime, endtime, instrument, product, fname,
                keys, version, badvalues)
