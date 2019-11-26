"""
Methods for importing data from the IMP spacecraft.

All data is publically available at https://cdaweb.gsfc.nasa.gov/pub/data/imp/
"""
from collections import OrderedDict
from datetime import datetime
import pathlib

import astropy.units as u
import pandas as pd

from heliopy.data import util
from heliopy.data import cdasrest

imp_url = 'https://cdaweb.gsfc.nasa.gov/pub/data/imp/'


def _check_probe(probe, valid_probes):
    if probe not in valid_probes:
        raise ValueError(
            '"{}" is not in the list of allowed probes ({})'.format(
                probe, valid_probes))
    return True


class _MergedDownloader(util.Downloader):
    def __init__(self, probe):
        _check_probe(probe, ['8'])
        self.probe = probe

        self.units = OrderedDict(
            [('sw_flag', u.dimensionless_unscaled),
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
             ('v_fit', u.km / u.s), ('vx_fit_gse', u.km / u.s),
             ('vy_fit_gse', u.km / u.s), ('vz_fit_gse', u.km / u.s),
             ('vlong_fit', u.deg), ('vlat_fit', u.deg),
             ('np_fit', u.cm**-3), ('Tp_fit', u.K),
             ('v_mom', u.km / u.s), ('vx_mom_gse', u.km / u.s),
             ('vy_mom_gse', u.km / u.s), ('vz_mom_gse', u.km / u.s),
             ('vlong_mom', u.deg), ('vlat_mom', u.deg),
             ('np_mom', u.cm**-3), ('Tp_mom', u.K),
             ('FCp', u.dimensionless_unscaled),
             ('DWp', u.dimensionless_unscaled)])

    def intervals(self, starttime, endtime):
        return self.intervals_monthly(starttime, endtime)

    def fname(self, interval):
        start = interval.start.to_datetime()
        intervalstring = str(start.year) + str(start.month).zfill(2)
        return f'imp_min_merge{intervalstring}.asc'

    def local_dir(self, interval):
        return pathlib.Path('imp') / f'imp{self.probe}'

    def download(self, interval):
        filename = self.fname(interval)
        local_dir = self.local_path(interval).parent
        remote_base_url = imp_url + f'imp{self.probe}/merged'
        util._download_remote(remote_base_url, filename, local_dir)

    def load_local_file(self, interval, product_list=None):
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
        data = pd.read_csv(self.local_path(interval), **readargs)
        data['Time'] = (pd.to_datetime(data['Year'], format='%Y') +
                        pd.to_timedelta(data['doy'] - 1, unit='d') +
                        pd.to_timedelta(data['Hour'], unit='h') +
                        pd.to_timedelta(data['Minute'], unit='m'))
        data = data.drop(['Year', 'doy', 'Hour', 'Minute', 'FCm', 'DWm'],
                         axis=1)
        data = data.set_index('Time', drop=True)
        return data


def merged(probe, starttime, endtime):
    """
    Import merged plasma data. See
    https://cdaweb.gsfc.nasa.gov/pub/data/imp/imp8/merged/00readme.txt
    for information on variables.

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
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data.
    """
    dl = _MergedDownloader(probe)
    return dl.load(starttime, endtime)


def _imp8(starttime, endtime, identifier, units=None, badvalues=None,
          warn_missing_units=True):
    """
    Generic method for downloading IMP8 data.
    """
    dl = cdasrest.CDASDwonloader('imp8', identifier, 'imp', units=units,
                                 badvalues=badvalues,
                                 warn_missing_units=warn_missing_units)
    return dl.load(starttime, endtime)


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
