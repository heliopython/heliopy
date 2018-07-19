"""
Methods for importing data from the IMP spacecraft.

All data is publically available at ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/
"""
from datetime import datetime
from collections import OrderedDict
import os
import pathlib as path

import pandas as pd
import astropy.units as u

from heliopy import config
from heliopy.data import util

data_dir = path.Path(config['download_dir'])
use_hdf = config['use_hdf']
imp_url = 'ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/'
imp_dir = data_dir / 'imp'
valid_probes = ['1', '2', '3', '4', '5', '6', '7', '8']


def _check_probe(probe, valid_probes):
    if probe not in valid_probes:
        raise ValueError(
            '"{}" is not in the list of allowed probes ({})'.format(
                probe, valid_probes))
    return True


def merged(probe, starttime, endtime, try_download=True):
    """
    Import merged plasma data. See
    ftp://cdaweb.gsfc.nasa.gov/pub/data/imp/imp8/merged/00readme.txt
    for information on variables.

    Parameters
    ----------
    probe : string
        Probe number.
    starttime : datetime
        Start of interval.
    endtime : datetime
        End of interval.
    verbose : bool, optional
        If ``True``, print information whilst loading. Default is
        ``False``.

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data.
    """
    _check_probe(probe, ['8'])
    dirs = []
    fnames = []
    extension = '.asc'
    units = OrderedDict([('sw_flag', u.dimensionless_unscaled),
                        ('x_gse', u.R_earth), ('y_gse', u.R_earth),
                        ('z_gse', u.R_earth), ('y_gsm', u.R_earth),
                        ('z_gsm', u.R_earth), ('Nm', u.dimensionless_unscaled),
                        ('<|B|>', u.nT), ('|<B>|', u.nT), ('<B_lat>', u.nT),
                        ('<B_long>', u.nT), ('Bx_gse', u.nT), ('By_gse', u.nT),
                        ('Bz_gse', u.nT), ('By_gsm', u.nT), ('Bz_gsm', u.nT),
                        ('sigma|B|', u.nT), ('sigma B', u.nT),
                        ('sigma B_x', u.nT), ('sigma B_y', u.nT),
                        ('sigma B_z', u.nT),
                        ('plas_reg', u.dimensionless_unscaled),
                        ('Npp', u.dimensionless_unscaled),
                        ('v_fit', u.km/u.s), ('vx_fit_gse', u.km/u.s),
                        ('vy_fit_gse', u.km/u.s), ('vz_fit_gse', u.km/u.s),
                        ('vlong_fit', u.deg), ('vlat_fit', u.deg),
                        ('np_fit', u.cm**-3), ('Tp_fit', u.K),
                        ('v_mom', u.km/u.s), ('vx_mom_gse', u.km/u.s),
                        ('vy_mom_gse', u.km/u.s), ('vz_mom_gse', u.km/u.s),
                        ('vlong_mom', u.deg), ('vlat_mom', u.deg),
                        ('np_mom', u.cm**-3), ('Tp_mom', u.K),
                        ('FCp', u.dimensionless_unscaled),
                        ('DWp', u.dimensionless_unscaled)])
    local_base_dir = imp_dir / 'imp{}'.format(probe) / 'merged'
    remote_base_url = imp_url + 'imp{}/merged'.format(probe)

    # Populate directories and filenames
    startyear = starttime.year
    endyear = endtime.year
    for year in range(startyear, endyear + 1):
        if year == startyear:
            startmonth = starttime.month
        else:
            startmonth = 1

        if year == endyear:
            endmonth = endtime.month
        else:
            endmonth = 12
        for month in range(startmonth, endmonth + 1):
            intervalstring = str(year) + str(month).zfill(2)
            fname = 'imp_min_merge' + intervalstring
            fnames.append(fname)
            dirs.append('')

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, extension):
        filename = fname + extension
        local_dir = path.Path(local_base_dir) / directory
        util._download_remote(remote_base_url, filename, local_dir)

    def processing_func(f):
        readargs = {'names': ['Year', 'doy', 'Hour', 'Minute', 'sw_flag',
                              'x_gse', 'y_gse', 'z_gse', 'y_gsm', 'z_gsm',
                              'Nm', 'FCm', 'DWm',
                              '<|B|>', '|<B>|', '<B_lat>', '<B_long>',
                              'Bx_gse', 'By_gse', 'Bz_gse',
                              'By_gsm', 'Bz_gsm',
                              'sigma|B|', 'sigma B',
                              'sigma B_x', 'sigma B_y', 'sigma B_z',
                              'plas_reg', 'Npp', 'FCp', 'DWp',
                              'v_fit',
                              'vx_fit_gse', 'vy_fit_gse', 'vz_fit_gse',
                              'vlong_fit', 'vlat_fit',
                              'np_fit', 'Tp_fit',
                              'v_mom',
                              'vx_mom_gse', 'vy_mom_gse', 'vz_mom_gse',
                              'vlong_mom', 'vlat_mom',
                              'np_mom', 'Tp_mom'],
                    'na_values': ['9999', '999', '99', '99', '9',
                                  '9999.99', '9999.99', '9999.99',
                                  '9999.99', '9999.99',
                                  '9', '99', '9.99', '9999.99', '9999.99',
                                  '9999.99', '9999.99',
                                  '9999.99', '9999.99',
                                  '9999.99', '9999.99',
                                  '9999.99', '9999.99',
                                  '9999.99',
                                  '9999.99', '9999.99', '9999.99',
                                  '9', '9', '99', '9.99',
                                  '9999.9', '9999.9', '9999.9', '9999.9',
                                  '9999.9', '9999.9', '9999.9', '9999999.',
                                  '9999.9', '9999.9', '9999.9', '9999.9',
                                  '9999.9', '9999.9',
                                  '9999.9', '9999999.'],
                    'delim_whitespace': True}
        # Read in data
        data = pd.read_table(f, **readargs)
        data['Time'] = (pd.to_datetime(data['Year'], format='%Y') +
                        pd.to_timedelta(data['doy'] - 1,
                                        unit='d') +
                        pd.to_timedelta(data['Hour'], unit='h') +
                        pd.to_timedelta(data['Minute'], unit='m'))
        data = data.drop(['Year', 'doy', 'Hour', 'Minute', 'FCm', 'DWm'],
                         axis=1)
        return data

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)


def mitplasma_h0(probe, starttime, endtime, try_download=True):
    """
    Import mit h0 plasma data.

    Parameters
    ----------
    probe : string
        Probe number.
    starttime : datetime
        Start of interval.
    endtime : datetime
        End of interval.

    Returns
    -------
    data : DataFrame
        Requested data.
    """
    dirs = []
    fnames = []
    extension = '.cdf'
    units = OrderedDict([('mode', u.dimensionless_unscaled),
                         ('Region', u.dimensionless_unscaled),
                         ('Spacecraft', u.dimensionless_unscaled)])
    for date, _, _ in util._daysplitinterval(starttime, endtime):
        intervalstring = str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2)
        filename = 'i' + probe + '_h0_mitplasma_' + intervalstring + '_v01'
        fnames.append(filename)
        # Location of file relative to local directory or remote url
        relative_loc = 'imp{}/plasma_mit/mitplasma_h0/{}'.format(
            probe, date.year)
        dirs.append(relative_loc)

    local_base_dir = imp_dir
    remote_base_url = imp_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, extension):
        remote_url = remote_base_url + str(directory)
        filename = fname + extension
        local_dir = local_base_dir / directory
        util._download_remote(remote_url, filename, local_dir)

    def processing_func(f):
        thisdata = util.cdf2df(f, 'Epoch')
        thisdata.index.name = 'Time'
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)


def mag320ms(probe, starttime, endtime, try_download=True):
    """
    Import 320ms cadence magnetic field data.

    Parameters
    ----------
        probe : string
            Probe number.
        starttime : datetime
            Start of interval.
        endtime : datetime
            End of interval.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    data = []
    fnames = []
    dirs = []
    extension = '.cdf'
    dtimes = util._daysplitinterval(starttime, endtime)
    # Loop through years
    for dtime in dtimes:
        date = dtime[0]
        intervalstring = str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2)
        filename = 'i8_320msec_mag_' + intervalstring + '_v01'
        fnames.append(filename)
        # Location of file relative to local directory or remote url
        relative_loc = 'imp' + probe + '/mag/mag_320msec_cdaweb/' +\
            str(date.year)
        dirs.append(relative_loc)

    local_base_dir = imp_dir
    remote_base_url = imp_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, extension):
        remote_url = remote_base_url + str(directory)
        filename = fname + extension
        local_dir = local_base_dir / directory
        util._download_remote(remote_url, filename, local_dir)

    def processing_func(f):
        thisdata = util.cdf2df(f, 'Epoch')
        thisdata.index.name = 'Time'
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime,
                        try_download=try_download)


def mag15s(probe, starttime, endtime, verbose=False, try_download=True):
    """
    Import 15s cadence magnetic field data.

    Parameters
    ----------
    probe : string
        Probe number.
    starttime : datetime
        Start of interval.
    endtime : datetime
        End of interval.
    verbose : bool, optional
        If ``True``, print information whilst loading. Default is ``False``.

    Returns
    -------
        data : DataFrame
            Requested data.
    """
    data = []
    fnames = []
    dirs = []
    extension = '.asc'
    units = OrderedDict([('n points', u.dimensionless_unscaled),
                         ('x gse', u.earthRad), ('y gse', u.earthRad),
                         ('z gse', u.earthRad), ('y gsm', u.earthRad),
                         ('z gsm', u.earthRad), ('|B|', u.nT),
                         ('Bx gse', u.nT), ('By gse', u.nT),
                         ('Bz gse', u.nT), ('By gsm', u.nT),
                         ('Bz gsm', u.nT), ('Bxx gse', u.nT**2),
                         ('Byy gse', u.nT**2), ('Bzz gse', u.nT**2),
                         ('Byx gse', u.nT**2), ('Bzx gse', u.nT**2),
                         ('Bzy gse', u.nT**2), ('Time shift', u.s),
                         ('sw flag', u.dimensionless_unscaled)])
    dtimes = util._daysplitinterval(starttime, endtime)
    # Loop through years
    for dtime in dtimes:
        startdt = dtime[0]
        year = startdt.year
        doy = util.dtime2doy(startdt)
        if verbose:
            print('Loading IMP 15s mag probe {}, {:03d}/{}'.format(probe,
                                                                   doy,
                                                                   year))
        filename = '{}{:03d}_imp{}_mag_15s_v3'.format(year, doy, probe)
        fnames.append(filename)
        # Location of file relative to local directory or remote url
        relative_loc = os.path.join('imp{}'.format(probe),
                                    'mag',
                                    '15s_ascii_v3',
                                    str(year))
        dirs.append(relative_loc)

    local_base_dir = imp_dir
    remote_base_url = imp_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, extension):
        remote_url = remote_base_url + str(directory)
        filename = fname + extension
        local_dir = local_base_dir / directory
        util._download_remote(remote_url, filename, local_dir)

    remote_url = imp_url + relative_loc

    # Read in data
    def processing_func(f):
        readargs = {'names': ['Year', 'doy', 'Second', 'Source flag',
                              'n points', 'x gse', 'y gse', 'z gse',
                              'y gsm', 'z gsm',
                              '|B|', 'Bx gse', 'By gse', 'Bz gse',
                              'By gsm', 'Bz gsm',
                              'Bxx gse', 'Byy gse', 'Bzz gse',
                              'Byx gse', 'Bzx gse', 'Bzy gse',
                              'Time shift', 'sw flag'],
                    'na_values': ['9999', '999', '99', '9',
                                  '999', '99.99', '99.99', '99.99',
                                  '99.99', '99.99',
                                  '9999.99', '9999.99', '9999.99', '9999.99',
                                  '9999.99', '9999.99',
                                  '9999.99', '9999.99', '9999.99',
                                  '9999.99', '9999.99', '9999.99',
                                  '999.9', '9'],
                    'delim_whitespace': True}
        thisdata = pd.read_table(f, **readargs)
        thisdata['Time'] = (pd.to_datetime(thisdata['Year'], format='%Y') +
                            pd.to_timedelta(thisdata['doy'] - 1,
                                            unit='d') +
                            pd.to_timedelta(thisdata['Second'], unit='s'))
        thisdata = thisdata.set_index('Time', drop=False)
        thisdata = thisdata.drop(['Year', 'doy', 'Second'], 1)
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)
