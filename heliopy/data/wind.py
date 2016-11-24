"""
Methods for importing data from the WIND spacecraft. All data is publically
available at ftp://spdf.gsfc.nasa.gov/pub/data/wind.
"""
import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config
import pandas as pd
data_dir = config['default']['download_dir']
wind_dir = data_dir + '/wind'
remote_wind_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/wind'


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
    relative_dir = '/mfi/mfi_h0'

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'wi_h0_mfi_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v05.cdf'
        this_relative_dir = relative_dir + '/' + str(day[0].year)
        # Absolute path to local directory for this data file
        local_dir = wind_dir + this_relative_dir
        helper.checkdir(local_dir)

        remote_url = remote_wind_dir + this_relative_dir

        cdf = helper.load(filename, local_dir, remote_url)

        keys = {'B3GSE': ['Bx_gse', 'By_gse', 'Bz_gse'],
                'Epoch3': 'Time'}
        df = helper.cdf2df(cdf, index_key='Epoch3', keys=keys)
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
    relative_dir = '/3dp/3dp_pm'

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'wi_pm_3dp_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v05.cdf'
        this_relative_dir = relative_dir + '/' + str(day[0].year)
        # Absolute path to local directory for this data file
        local_dir = wind_dir + this_relative_dir
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
