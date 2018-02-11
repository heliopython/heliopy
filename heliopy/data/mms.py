"""
Methods for importing data from the four MMS spacecraft.

All data is publically available at
https://lasp.colorado.edu/mms/sdc/public/data/, and the MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
from datetime import datetime
import numpy as np
import pandas as pd
import os
import urllib

from heliopy.data import util
from heliopy import config

data_dir = config['download_dir']
mms_dir = os.path.join(data_dir, 'mms')
remote_mms_dir = 'https://lasp.colorado.edu/mms/sdc/public/data/'


def fpi_dis_moms(probe, mode, starttime, endtime):
    """
    Import fpi ion distribution moment data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    mode : string
        Data mode, must be 'fast' or 'brst'
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : DataFrame
        Imported data.
    """
    valid_modes = ['fast', 'brst']
    if mode not in valid_modes:
        raise RuntimeError('Mode must be either fast or brst')
    # Directory relative to main MMS data directory
    relative_dir = os.path.join('mms' + probe, 'fpi', mode, 'l2', 'dis-moms')

    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        starthour = day[1].hour
        endhour = day[2].hour + 1
        # fips fast data product has files every two hours, so get nearest two
        # hour stamps
        starthour -= np.mod(starthour, 2)
        endhour += np.mod(endhour, 2)
        for h in range(starthour, endhour, 2):
            this_relative_dir = os.path.join(relative_dir,
                                             str(date.year),
                                             str(date.month).zfill(2))
            filename = ('mms{}_fpi_{}_l2_dis-moms_'
                        '{}{:02}{:02}{:02}0000_v3.1.1.cdf').format(
                            probe, mode, date.year, date.month, date.day, h)

            # Absolute path to local directory for this data file
            local_dir = os.path.join(mms_dir, this_relative_dir)
            util._checkdir(local_dir)

            remote_url = remote_mms_dir + this_relative_dir
            # Load cdf file
            try:
                cdf = util.load(filename, local_dir, remote_url)
            except urllib.error.HTTPError as e:
                if str(e) == 'HTTP Error 404: Not Found':
                    print('No data available for hours', str(h) + '-' +
                          str(h + 2), 'on', date.strftime('%d/%m/%Y'))
                    continue
                else:
                    raise

            probestr = 'mms' + probe + '_'
            # Convert cdf to dataframe
            keys = {'Epoch': 'Time',
                    probestr + 'dis_bulkv_gse_fast': ['bulkv_x',
                                                      'bulkv_y',
                                                      'bulkv_z'],
                    probestr + 'dis_heatq_gse_fast': ['heatq_x',
                                                      'heatq_y',
                                                      'heatq_z'],
                    probestr + 'dis_numberdensity_fast': 'n',
                    probestr + 'dis_temppara_fast': 'T_par',
                    probestr + 'dis_tempperp_fast': 'T_perp'}
            df = util.cdf2df(cdf, 'Epoch', keys)
            data.append(df)

    return util.timefilter(data, starttime, endtime)


def fgm_survey(probe, starttime, endtime):
    """
    Import fgm survey mode magnetic field data.

    Parameters
    ----------
    probe : string
        Probe number, must be 1, 2, 3, or 4
    starttime : datetime
        Interval start time.
    endtime : datetime
        Interval end time.

    Returns
    -------
    data : DataFrame
        Imported data.
    """
    # Directory relative to main MMS data directory
    relative_dir = os.path.join('mms' + probe, 'fgm', 'srvy', 'l2')

    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        this_relative_dir = os.path.join(relative_dir,
                                         str(date.year),
                                         str(date.month).zfill(2))
        filename = 'mms{}_fgm_srvy_l2_{}{:02}{:02}_v4.18.0.cdf'.format(
            probe, date.year, date.month, date.day)

        # Absolute path to local directory for this data file
        local_dir = os.path.join(mms_dir, this_relative_dir)
        util._checkdir(local_dir)

        remote_url = remote_mms_dir + this_relative_dir
        # Load cdf file
        cdf = util.load(filename, local_dir, remote_url)

        # Convert cdf to dataframe
        keys = {'mms' + probe + '_fgm_b_gsm_srvy_l2': ['Bx', 'By', 'Bz', 'Br'],
                'Epoch': 'Time'}
        df = util.cdf2df(cdf, 'Epoch', keys)
        data.append(df)

    return util.timefilter(data, starttime, endtime)
