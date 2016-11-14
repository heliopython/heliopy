"""
Methods for importing data from the four MMS spacecraft.

All data is publically available at
https://lasp.colorado.edu/mms/sdc/public/data/, and the MMS science data centre
is at https://lasp.colorado.edu/mms/sdc/public/.
"""
import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config
import pandas as pd
data_dir = config['default']['download_dir']
mms_dir = data_dir + '/mms/'
remote_mms_dir = 'https://lasp.colorado.edu/mms/sdc/public/data/'


def fgm_survey(probe, starttime, endtime):
    """
    Import fgm survey mode data.

    Parameters
    ----------
        probe : int
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
    relative_dir = 'mms' + str(probe) + '/fgm/srvy/l2/'

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        this_relative_dir = relative_dir + str(date.year) + '/' +\
            str(date.month).zfill(2)
        filename = 'mms' + str(probe) + '_fgm_srvy_l2_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v4.18.0.cdf'

        # Absolute path to local directory for this data file
        local_dir = mms_dir + this_relative_dir
        helper.checkdir(local_dir)

        remote_url = remote_mms_dir + this_relative_dir
        # Load cdf file
        cdf = helper.load(filename, local_dir, remote_url)

        # Convert cdf to dataframe
        keys = {'mms2_fgm_b_gsm_srvy_l2': ['Bx', 'By', 'Bz', 'Br'],
                'Epoch': 'Time'}
        df = helper.cdf2df(cdf, 'Epoch', keys)
        data.append(df)

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]
    return data
