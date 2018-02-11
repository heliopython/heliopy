"""
Methods for importing data from the THEMIS/ARTEMIS spacecraft.

All data is publically available at
http://themis.ssl.berkeley.edu/data/themis/.
"""
import os
import pandas as pd
import numpy as np

from heliopy.data import util
from heliopy import config

data_dir = config['download_dir']
themis_dir = data_dir + '/themis'
remote_themis_dir = 'http://themis.ssl.berkeley.edu/data/themis/'
valid_probes = ['a', 'b', 'c', 'd', 'e']


def _validate_probe(probe):
    if probe not in valid_probes:
        raise ValueError(('Probe argument %s is not in list of allowed'
                          'probes: %s') % (probe, valid_probes))


def fgm(probe, rate, coords, starttime, endtime):
    """
    Import fgm magnetic field data from THEMIS.

    Parameters
    ----------
        probe : string
            Alowed values are [a, b, c, d, e].
        rate : string
            Date rate to return. Allowed values are [e, h, l, s].
        coords : string
            Magnetic field co-ordinate system. Allowed values are
            [dsl, gse, gsm, ssl]. NOTE: Add link to co-ordinate system
            descriptions.
        starttime : datetime
            Interval start time.
        endtime : datetime
            Interval end time.

    Returns
    -------
        data : DataFrame
    """
    valid_rates = ['e', 'h', 'l', 's']
    valid_coords = ['dsl', 'gse', 'gsm', 'ssl']
    _validate_probe(probe)
    if rate not in valid_rates:
        raise ValueError(('rate argument %s is not in list of allowed'
                          'rates: %s') % (rate, valid_rates))
    if coords not in valid_coords:
        raise ValueError(('coords argument %s is not in list of allowed'
                          'co-ordinate systems: %s') % (rate, valid_rates))

    # Directory relative to main THEMIS data directory
    relative_dir = os.path.join('th' + probe, 'l2', 'fgm')

    daylist = util._daysplitinterval(starttime, endtime)
    data = []
    for day in daylist:
        date = day[0]
        this_relative_dir = os.path.join(relative_dir, str(date.year))
        filename = 'th' + probe + '_l2_fgm_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v01.cdf'
        # Absolute path to local directory for this data file
        local_dir = os.path.join(themis_dir, this_relative_dir)
        util._checkdir(local_dir)

        remote_url = remote_themis_dir + this_relative_dir
        cdf = util.load(filename, local_dir, remote_url)
        if cdf is None:
            print('File {}/{} not available\n'.format(
                remote_url, filename))
            continue

        probestr = 'th' + probe
        ratestr = '_fg' + rate + '_'
        keys = {probestr + ratestr + 'btotal': '|B|',
                probestr + ratestr + coords: ['Bx_' + coords,
                                              'By_' + coords,
                                              'Bz_' + coords],
                probestr + ratestr + 'time': 'Time'}
        df = util.cdf2df(cdf, probestr + ratestr + 'time', keys,
                         dtimeindex=False)
        df = df.set_index(pd.to_datetime(df.index.values, unit='s'))
        df['Time'] = df.index.values
        data.append(df)

    data = pd.concat(data)
    data = data[(data['Time'] > starttime) &
                (data['Time'] < endtime)]
    return data
