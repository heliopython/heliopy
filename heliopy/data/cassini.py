"""
Methods for importing data from the Cassini spacecraft.

All data is publically available at http://pds-atmospheres.nmsu.edu/data_and_services/atmospheres_data/Cassini/Cassini.html
"""
import os
import pandas as pd
import calendar

from heliopy.data import helper
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

    daylist = helper.daysplitinterval(starttime, endtime)
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
        fname = str(year)[2:] + doy + '_FGM_KRTP'

        local_dir = os.path.join(cassini_dir, 'mag', 'hires', str(year))

        hdfloc = os.path.join(local_dir, fname + '.hdf')
        if os.path.isfile(hdfloc):
            df = pd.read_hdf(hdfloc)
            data.append(df)
            continue

        f = helper.load(fname + '.TAB', local_dir, url)
        df = pd.read_table(f, names=['Time', 'Bx', 'By', 'Bz'],
                           delim_whitespace=True,
                           parse_dates=[0], index_col=0)

        if use_hdf:
            df.to_hdf(hdfloc, key='data', mode='w')

        data.append(df)
    return helper.timefilter(data, starttime, endtime)
