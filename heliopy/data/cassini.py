"""
Methods for importing data from the Cassini spacecraft.

All data is publically available at http://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/Cassini/Cassini.html
"""
import os
import pandas as pd
import calendar

from heliopy.data import util
from heliopy import config

data_dir = config['download_dir']
use_hdf = config['use_hdf']
cassini_dir = os.path.join(data_dir, 'cassini')

# These mappings from months to strings are used in directory names
month2str = {1: '001_031_JAN',
             2: '032_059_FEB',
             3: '060_090_MAR',
             4: '091_120_APR',
             5: '121_151_MAY',
             6: '152_181_JUN',
             7: '182_212_JUL',
             8: '213_243_AUG',
             9: '244_273_SEP',
             10: '274_304_OCT',
             11: '305_334_NOV',
             12: '335_365_DEC'}
leapmonth2str = {1: '001_031_JAN',
                 2: '032_060_FEB',
                 3: '061_091_MAR',
                 4: '092_121_APR',
                 5: '122_152_MAY',
                 6: '153_182_JUN',
                 7: '183_213_JUL',
                 8: '214_244_AUG',
                 9: '245_274_SEP',
                 10: '275_305_OCT',
                 11: '306_335_NOV',
                 12: '336_366_DEC'}


def mag_1min(starttime, endtime, coords):
    """
    Import 1 minute magnetic field from Cassini.

    See https://pds-ppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/CO-E_SW_J_S-MAG-4-SUMM-1MINAVG-V1.0
    for more information.

    Cassini Orbiter Magnetometer Calibrated MAG data in 1 minute averages
    available covering the period 1999-08-16 (DOY 228) to 2016-12-31 (DOY 366).
    The data are provided in RTN coordinates throughout the mission, with
    Earth, Jupiter, and Saturn centered coordinates for the respective
    flybys of those planets.

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.
    coords : strings
        Requested coordinate system. Must be one of
        ``['KRTP', 'KSM', 'KSO', 'RTN']``

    Returns
    -------
    data : DataFrame
        Requested data
    """
    valid_coords = ['KRTP', 'KSM', 'KSO', 'RTN']
    if coords not in valid_coords:
        raise ValueError('coords must be one of {}'.format(valid_coords))
    base_url = ('https://pds-ppi.igpp.ucla.edu/ditdos/download?'
                'id=pds://PPI/CO-E_SW_J_S-MAG-4-SUMM-1MINAVG-V1.0/DATA')

    data = []
    for year in starttime.year, endtime.year:
        url = '{}/{}'.format(base_url, year)
        local_dir = os.path.join(cassini_dir, 'mag', '1min')

        fname = '{}_FGM_{}_1M'.format(year, coords)

        hdfloc = os.path.join(local_dir, fname + '.hdf')
        if os.path.isfile(hdfloc):
            df = pd.read_hdf(hdfloc)
            data.append(df)
            continue

        f = util.load(fname + '.TAB', local_dir, url)
        if 'error_message' in f.readline():
            f.close()
            os.remove(os.path.join(local_dir, fname + '.TAB'))
            continue

        df = pd.read_table(f, names=['Time', 'Bx', 'By', 'Bz', '|B|',
                                     'X', 'Y', 'Z', 'Local hour', 'n points'],
                           delim_whitespace=True,
                           parse_dates=[0], index_col=0)
        data.append(df)

        if use_hdf:
            df.to_hdf(hdfloc, key='data', mode='w')

    return util.timefilter(data, starttime, endtime)


def mag_hires(starttime, endtime):
    """
    Import high resolution magnetic field from Cassini.

    See http://pds-ppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/CO-E_SW_J_S-MAG-3-RDR-FULL-RES-V1.0
    for more information.

    Cassini Orbiter Magnetometer Calibrated MAG data at the highest time
    resolution available covering the period 1999-08-16 (DOY 228) to
    2016-12-31 (DOY 366).

    The data are in RTN coordinates prior Cassini's arrival at Saturn, and
    Kronographic (KRTP) coordinates at Saturn (beginning 2004-05-14, DOY 135).

    Parameters
    ----------
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : DataFrame
        Requested data
    """
    base_url = ('http://pds-ppi.igpp.ucla.edu/ditdos/download?id='
                'pds://PPI/CO-E_SW_J_S-MAG-3-RDR-FULL-RES-V1.0/DATA')

    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    for [day, stime, etime] in daylist:
        year = day.year
        url = '{}/{}'.format(base_url, year)

        if calendar.isleap(year):
            monthstr = leapmonth2str[day.month]
        else:
            monthstr = month2str[day.month]

        url = '{}/{}'.format(url, monthstr)

        doy = day.strftime('%j')
        local_dir = os.path.join(cassini_dir, 'mag', 'hires', str(year))

        # No way to work out co-ordinates, so guess Kronian and then RTN
        try:
            coords = 'KRTP'
            df = _mag_hires_helper(year, doy, local_dir, url, coords)

        except RuntimeError:
            try:
                coords = 'RTN'
                df = _mag_hires_helper(year, doy, local_dir, url, coords)
            except RuntimeError:
                continue
        df['coords'] = coords

        data.append(df)
    return util.timefilter(data, starttime, endtime)


def _mag_hires_helper(year, doy, local_dir, url, coords):
    fname = str(year)[2:] + doy + '_FGM_' + coords

    hdf_fname = '{}_{}.hdf'.format(year, doy)
    hdfloc = os.path.join(local_dir, hdf_fname)
    if os.path.isfile(hdfloc):
        return pd.read_hdf(hdfloc)

    f = util.load(fname + '.TAB', local_dir, url)
    if f is None:
        raise RuntimeError(
            'No file named {} exits on remote server'.format(fname))
    elif 'error_message' in f.readline():
        f.close()
        os.remove(os.path.join(local_dir, fname + '.TAB'))
        raise RuntimeError(
            'No file named {} exits on remote server'.format(fname))

    df = pd.read_table(f, names=['Time', 'Bx', 'By', 'Bz'],
                       delim_whitespace=True,
                       parse_dates=[0], index_col=0)

    if use_hdf:
        df.to_hdf(hdfloc, key='data', mode='w')

    return df
