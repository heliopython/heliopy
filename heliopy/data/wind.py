"""
Methods for importing data from the WIND spacecraft. All data is publically
available at ftp://spdf.gsfc.nasa.gov/pub/data/wind.
"""
import os
import pandas as pd

import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config

data_dir = config['default']['download_dir']
wind_dir = data_dir + '/wind'
remote_wind_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/wind/'


def swe_h3(starttime, endtime):
    """
    Import 'h3' solar wind electron data product from WIND.

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

    daylist = spacetime.daysplitinterval(starttime, endtime)
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
        timekey = 'Epoch'
        energykey = 'Ve'
        helper.pitchdist_cdf2df(cdf, distkeys, energykey, timekey)

        data.append(df)

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]
    return data


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
    # Directory relative to main WIND data directory
    relative_dir = os.path.join('mfi', 'mfi_h0')

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'wi_h0_mfi_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v05.cdf'
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(wind_dir, this_relative_dir)
        helper.checkdir(local_dir)

        remote_url = remote_wind_dir + this_relative_dir

        cdf = helper.load(filename, local_dir, remote_url, guessversion=True)

        keys = {'B3GSE': ['Bx_gse', 'By_gse', 'Bz_gse'],
                'Epoch3': 'Time'}
        badvalues = {'Bx_gse': -1e+31,
                     'By_gse': -1e+31,
                     'Bz_gse': -1e+31}
        df = helper.cdf2df(cdf,
                           index_key='Epoch3',
                           keys=keys,
                           badvalues=badvalues)
        data.append(df)

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]
    return data


def threedp_pm(starttime, endtime):
    """
    Import 'pm' wind data.

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

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'wi_pm_3dp_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v05.cdf'
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
        # Absolute path to local directory for this data file
        local_dir = os.path.join(wind_dir, this_relative_dir)
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
        data.append(df)

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]
    return data
