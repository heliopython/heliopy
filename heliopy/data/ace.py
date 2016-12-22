"""
Methods for importing data from the ACE spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/ace/. The
ACE spacecraft homepage can be found at http://www.srl.caltech.edu/ACE/.
"""
import os
import pandas as pd

import heliopy.time as spacetime
from heliopy.data import helper
from heliopy import config

data_dir = config['default']['download_dir']
ace_dir = os.path.join(data_dir, 'ace')
remote_ace_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/ace/'


def mfi_h0(starttime, endtime):
    """
    Import 'mfi_h0' magnetic field data product from ACE.

    This data set has 16 second cadence.

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

    daylist = spacetime.daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        filename = 'ac_h0_mfi_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v06.cdf'
        this_relative_dir = os.path.join(relative_dir, str(day[0].year))
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

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) & (data['Time'] < endtime)]
    return data
