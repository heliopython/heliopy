"""
Methods for importing data from the WIND spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/wind.
See https://wind.nasa.gov/data_sources.php for more information on different
data products.
"""
import os
import pandas as pd
import numpy as np

from heliopy.data import helper
from heliopy import config

data_dir = config['download_dir']
use_hdf = config['use_hdf']
wind_dir = os.path.join(data_dir, 'wind')
remote_wind_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/wind/'


def swe_h1(starttime, endtime):
    """
    Import 'h1' (Bi-Maxwellian, Anisotropic Analysis of Protons and Alphas)
    solar wind ion data product from WIND.

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
    relative_dir = os.path.join('swe', 'swe_h1')

    daylist = helper.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'wi_h1_swe_{}{:02}{:02}_v01'.format(
            date.year, date.month, date.day)
        local_dir = os.path.join(wind_dir, relative_dir, str(date.year))

        hdfname = filename + 'hdf'
        hdfloc = os.path.join(local_dir, hdfname)
        if os.path.isfile(hdfloc):
            df = pd.read_hdf(hdfloc)
            data.append(df)
            continue

        helper.checkdir(local_dir)
        remote_url = '{}swe/swe_h1/{}'.format(remote_wind_dir, date.year)
        cdf = helper.load(filename + '.cdf', local_dir, remote_url)
        badvalues = {'Proton_V_nonlin': 99999.9,
                     'Proton_sigmaV_nonlin': 99999.9,
                     'Proton_VY_nonlin': 99999.9,
                     'Proton_sigmaVY_nonlin': 99999.9,
                     'Proton_W_nonlin': 99999.9,
                     'Proton_sigmaW_nonlin': 99999.9,
                     'Proton_Wperp_nonlin': 99999.9,
                     'Proton_sigmaWperp_nonlin': 99999.9,
                     'Proton_Wpar_nonlin': 99999.9,
                     'Proton_sigmaWpar_nonlin': 99999.9,
                     'EW_flowangle': 99999.9,
                     'SigmaEW_flowangle': 99999.9,
                     'NS_flowangle': 99999.9,
                     'SigmaNS_flowangle': 99999.9,
                     'Alpha_V_nonlin': 99999.9,
                     'Alpha_sigmaV_nonlin': 99999.9,
                     'Alpha_VX_nonlin': 99999.9,
                     'Alpha_sigmaVX_nonlin': 99999.9,
                     'Alpha_VY_nonlin': 99999.9,
                     'Alpha_sigmaVY_nonlin': 99999.9,
                     'Alpha_VZ_nonlin': 99999.9,
                     'Alpha_sigmaVZ_nonlin': 99999.9,
                     'Alpha_W_nonlin': 99999.9,
                     'Alpha_sigmaW_nonlin': 99999.9,
                     'Alpha_Wperp_nonlin': 99999.9,
                     'Alpha_sigmaWperp_nonlin': 99999.9,
                     'Alpha_Wpar_nonlin': 99999.9,
                     'Alpha_sigmaWpar_nonlin': 99999.9,
                     'Alpha_Na_nonlin': 99999.9,
                     'Alpha_sigmaNa_nonlin': 99999.9,
                     'Proton_Wperp_moment': 99999.9,
                     'Proton_Wpar_moment': 99999.9,
                     'Alpha_Na_nonlin': 100000.0,
                     'Alpha_sigmaNa_nonlin': 100000.0}
        df = helper.cdf2df(cdf, 'Epoch', badvalues=badvalues)
        if use_hdf:
            df.to_hdf(hdfloc, 'pm', mode='w', format='f')
        data.append(df)

    return helper.timefilter(data, starttime, endtime)


def swe_h3(starttime, endtime):
    """
    Import 'h3' solar wind electron data product from WIND.

    Electron pitch angle files providing electron fluxes at 30 directional bins
    relative to the instantaneous magnetic field direction at 13 different
    energy levels

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
    relative_dir = os.path.join('swe', 'swe_h3')

    daylist = helper.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'wi_h3_swe_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v01.cdf'
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(wind_dir, this_relative_dir)
        helper.checkdir(local_dir)

        remote_url = remote_wind_dir + this_relative_dir

        cdf = helper.load(filename, local_dir, remote_url)
        distkeys = []
        for i in range(0, 13):
            distkeys.append('f_pitch_E' + str(i).zfill(2))
        anglelabels = []
        for i in range(0, 30):
            anglelabels.append((i + 0.5) * np.pi / 30)
        timekey = 'Epoch'
        energykey = 'Ve'

        df = helper.pitchdist_cdf2df(cdf, distkeys, energykey, timekey,
                                     anglelabels)

        data.append(df)

    return helper.timefilter(data, starttime, endtime)


def mfi_h0(starttime, endtime):
    """
    Import 'mfi_h0' magnetic field data product from WIND.

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
    return _mfi(starttime, endtime, 'h0')


def mfi_h2(starttime, endtime):
    """
    Import 'mfi_h2' magnetic field data product from WIND.

    The highest time resolution data (11 vectors/sec usually, and
    22 vectors/sec when near Earth)

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
    return _mfi(starttime, endtime, 'h2')


def _mfi(starttime, endtime, version):
    """
    Import mfi magnetic field data products from WIND.

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
    relative_dir = os.path.join('mfi', 'mfi_' + version)

    daylist = helper.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(wind_dir, this_relative_dir)
        filename = 'wi_' + version + '_mfi_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v05.cdf'
        hdfname = filename[:-4] + '.hdf'
        hdfloc = os.path.join(local_dir, hdfname)
        if os.path.isfile(hdfloc):
            df = pd.read_hdf(hdfloc)
            data.append(df)
            continue

        helper.checkdir(local_dir)
        remote_url = remote_wind_dir + this_relative_dir
        cdf = helper.load(filename, local_dir, remote_url, guessversion=True)

        epoch_dict = {'h0': 'Epoch3', 'h2': 'Epoch'}
        mag_dict = {'h0': 'B3GSE', 'h2': 'BGSE'}

        epoch_key = epoch_dict[version]
        mag_key = mag_dict[version]

        keys = {mag_key: ['Bx_gse', 'By_gse', 'Bz_gse'],
                epoch_key: 'Time'}
        badvalues = {'Bx_gse': -1e+31,
                     'By_gse': -1e+31,
                     'Bz_gse': -1e+31}
        df = helper.cdf2df(cdf,
                           index_key=epoch_key,
                           keys=keys,
                           badvalues=badvalues)
        if use_hdf:
            df.to_hdf(hdfloc, 'mag', mode='w', format='f')
        data.append(df)

    return helper.timefilter(data, starttime, endtime)


def threedp_pm(starttime, endtime):
    """
    Import 'pm' wind data.

    3 second time resolution solar wind proton and alpha particle moments from
    the PESA LOW sensor, computed on-board the spacecraft

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
    relative_dir = os.path.join('3dp', '3dp_pm')

    daylist = helper.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(wind_dir, this_relative_dir)
        filename = 'wi_pm_3dp_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v05.cdf'
        hdfname = filename[:-4] + 'hdf'
        hdfloc = os.path.join(local_dir, hdfname)
        if os.path.isfile(hdfloc):
            df = pd.read_hdf(hdfloc)
            data.append(df)
            continue

        helper.checkdir(local_dir)
        remote_url = remote_wind_dir + this_relative_dir
        cdf = helper.load(filename, local_dir, remote_url, guessversion=True)

        keys = {'A_DENS': 'n_a',
                'A_TEMP': 'T_a',
                'A_VELS': ['va_x', 'va_y', 'va_z'],
                'P_DENS': 'n_p',
                'P_TEMP': 'T_p',
                'P_VELS': ['vp_x', 'vp_y', 'vp_z'],
                'Epoch': 'Time'}
        df = helper.cdf2df(cdf, index_key='Epoch', keys=keys)
        if use_hdf:
            df.to_hdf(hdfloc, 'pm', mode='w', format='f')
        data.append(df)

    return helper.timefilter(data, starttime, endtime)
