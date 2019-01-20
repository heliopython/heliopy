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
from heliopy.data import cdasrest

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
                      directory, fname, remote_fname, extension):
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
        data = data.set_index('Time', drop=True)
        return data

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime, units=units,
                        try_download=try_download)


def _imp8(starttime, endtime, identifier, units=None, badvalues=None,
          warn_missing_units=True):
    """
    Generic method for downloading IMP8 data.
    """
    dataset = 'imp8'
    return cdasrest._process_cdas(starttime, endtime, identifier, dataset,
                                  imp_dir,
                                  units=units,
                                  badvalues=badvalues,
                                  warn_missing_units=warn_missing_units)


def _docstring(identifier, extra):
    return cdasrest._docstring(identifier, 'I', extra)


def i8_mitplasma(starttime, endtime):
    identifier = 'I8_H0_MITPLASMA'
    return _imp8(starttime, endtime, identifier, warn_missing_units=False)


i8_mitplasma.__doc__ = _docstring(
    'I8_320MSEC_MAG', 'MIT plasma data')


def i8_mag320ms(starttime, endtime):
    identifier = 'I8_320MSEC_MAG'
    return _imp8(starttime, endtime, identifier)


i8_mag320ms.__doc__ = _docstring(
    'I8_15SEC_MAG', '320 millisecond magnetic field')


def i8_mag15s(starttime, endtime):
    identifier = 'I8_15SEC_MAG'
    units = OrderedDict([('N_of_points', u.dimensionless_unscaled),
                         ('SourceFlag', u.dimensionless_unscaled),
                         ('|B|', u.nT),
                         ('Bx gse', u.nT), ('By gse', u.nT),
                         ('Bz gse', u.nT), ('By gsm', u.nT),
                         ('Bz gsm', u.nT), ('Bxx gse', u.nT**2),
                         ('Byy gse', u.nT**2), ('Bzz gse', u.nT**2),
                         ('Byx gse', u.nT**2), ('Bzx gse', u.nT**2),
                         ('Bzy gse', u.nT**2), ('Time shift', u.s),
                         ('SW_flag', u.dimensionless_unscaled)])
    for coord in ['GSE', 'GSET', 'GSM', 'GSMT']:
        for i in range(3):
            units[f'SC_Pos_{coord}_{i}'] = u.earthRad
    return _imp8(starttime, endtime, identifier, units=units)


i8_mag15s.__doc__ = _docstring('I8_15SEC_MAG', '15 second magnetic field')
