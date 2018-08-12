"""
Methods for importing data from the THEMIS/ARTEMIS spacecraft.

All data is publically available at
http://themis.ssl.berkeley.edu/data/themis/.
"""
import pathlib as path

import pandas as pd
import numpy as np
import astropy.units as u
from collections import OrderedDict

from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
artemis_dir = data_dir / 'artemis'
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
        data : :class:`~sunpy.timeseries.TimeSeries`
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
    fgm_dir = path.Path('th' + probe) / 'l2' / 'fgm'
    daylist = util._daysplitinterval(starttime, endtime)

    dirs = []
    fnames = []
    extension = '.cdf'
    units = OrderedDict([('|B|', u.nT), ('Bz_dsl', u.nT),
                        ('By_dsl', u.nT), ('Bx_dsl', u.nT),
                        ('th{}_fgm_fg{}_quality'.format(probe, rate),
                         u.dimensionless_unscaled)])
    for day in daylist:
        date = day[0]
        filename = 'th{}_l2_fgm_{}{:02}{:02}_v01'.format(
            probe, date.year, date.month, date.day)
        fnames.append(filename)
        this_relative_dir = fgm_dir / str(date.year)
        dirs.append(this_relative_dir)

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        remote_url = remote_base_url + str(directory)
        # Now load remotely
        util.load(fname + extension,
                  local_base_dir / directory,
                  remote_url)

    def processing_func(cdf, **kwargs):
        probe = kwargs.pop('probe')
        rate = kwargs.pop('rate')
        coords = kwargs.pop('coords')

        probestr = 'th' + probe
        ratestr = '_fg' + rate + '_'
        df = util.cdf2df(cdf, probestr + ratestr + 'time',
                         dtimeindex=False)
        df = df.set_index(pd.to_datetime(df.index.values, unit='s'))
        df.index.name = 'Time'
        return df

    processing_kwargs = {'probe': probe, 'rate': rate, 'coords': coords}
    return util.process(dirs, fnames, extension, artemis_dir,
                        remote_themis_dir, download_func, processing_func,
                        starttime, endtime, units=units,
                        processing_kwargs=processing_kwargs)
