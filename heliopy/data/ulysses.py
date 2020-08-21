"""
Methods for importing data from the Ulysses spacecraft.
"""
from collections import OrderedDict
from datetime import datetime, timedelta
import pathlib
import urllib.error

import astropy.units as u
import pandas as pd

from heliopy.data import util

ulysses_url = 'http://ufa.esac.esa.int/ufa-sl-server/data-action?'
url_options = {'PROTOCOL': 'HTTP',
               'PRODUCT_TYPE': 'ALL'}


def swics_heavy_ions(starttime, endtime):
    """
    Import swics heavy ion data.

    The variables in this dataset are:

      - DENS_ALPHA: alpha to oxygen 6+ density ratio
      - VEL_ALPHA:  alpha velocity
      - TEMP_ALPHA: alpha temperature
      - DENS_C6:    carbon 6+ to oxygen 6+ density ratio
      - VEL_C6:     carbon 6+ velocity
      - TEMP_C6:    carbon 6+ temperature
      - DENS_O6:    oxygen 6+ density in cm^-3
      - VEL_O6:     oxygen 6+ velocity
      - TEMP_O6:    oxygen 6+ temperature
      - DENS_NE8:   neon 8+ to oxygen 6+ density ratio
      - VEL_NE8:    neon 8+ velocity
      - TEMP_NE8:   neon 8+ temperature
      - DENS_MG10:  magnesium 10+ to oxygen 6+ density ratio
      - VEL_MG10:   magnesium 10+ velocity
      - TEMP_MG10:  magnesium 10+ temperature
      - DENS_SI9:   silicon 9+ to oxygen 6+ density ratio
      - VEL_SI9:    silicon 9+ velocity
      - TEMP_SI9:   silicon 9+ temperature
      - DENS_S10:   sulphur 10+ to oxygen 6+ density ratio
      - VEL_S10:    sulphur 10+ velocity
      - TEMP_S10:   sulphur 10+ temperature
      - DENS_FE11:  iron 11+ to oxygen 6+ density ratio
      - VEL_FE11:   iron 11+ velocity
      - TEMP_FE11:  iron 11+ temperature

    See http://ufa.esac.esa.int/ufa-sl-server/data-action?PROTOCOL=HTTP&PRODUCT_TYPE=ALL&FILE_NAME=readme.txt&FILE_PATH=/ufa/HiRes/data/swics
    for more information.

    Parameters
    ----------
    starttime : datetime.datetime
        Start of interval
    endtime : datetime.datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data
    """
    names = ['year', 'doy', 'hour', 'minute', 'second']
    for ion in ['ALPHA', 'C6', 'O6', 'NE8', 'MG10', 'SI9', 'SI10', 'FE11']:
        names += ['DENS_' + ion, 'VEL_' + ion, 'TEMP_' + ion]
    product = 'uswimatb'
    units = OrderedDict([('VEL_ALPHA', u.km / u.s), ('TEMP_ALPHA', u.K),
                        ('VEL_C6', u.km / u.s), ('TEMP_C6', u.K),
                        ('VEL_O6', u.km / u.s), ('TEMP_O6', u.K),
                        ('VEL_NE8', u.km / u.s), ('TEMP_NE8', u.K),
                        ('VEL_MG10', u.km / u.s), ('TEMP_MG10', u.K),
                        ('VEL_SI9', u.km / u.s), ('TEMP_SI9', u.K),
                        ('VEL_SI10', u.km / u.s), ('TEMP_SI10', u.K),
                        ('VEL_FE11', u.km / u.s), ('TEMP_FE11', u.K),
                        ('DENS_O6', u.cm**-3),
                        ('DENS_ALPHA', u.dimensionless_unscaled),
                        ('DENS_C6', u.dimensionless_unscaled),
                        ('DENS_O6', u.dimensionless_unscaled),
                        ('DENS_NE8', u.dimensionless_unscaled),
                        ('DENS_MG10', u.dimensionless_unscaled),
                        ('DENS_SI9', u.dimensionless_unscaled),
                        ('DENS_SI10', u.dimensionless_unscaled),
                        ('DENS_FE11', u.dimensionless_unscaled)])
    return _swics(starttime, endtime, names, product, units)


def swics_abundances(starttime, endtime):
    """
    Import swics abundance data.

    The variables in this dataset are:

      - VEL_ALPHA:  alpha velocity
      - RAT_C6_C5:  ratio of carbon 6+ to 5+
      - RAT_O7_O6:  ratio of oxygen 7+ to 6+
      - RAT_FE_O:   abundance ratio of iron to oxygen
      - CHARGE_FE:  average charge state of iron
      - N_CYC:      number of instrument cycles in average

    See http://ufa.esac.esa.int/ufa-sl-server/data-action?PROTOCOL=HTTP&PRODUCT_TYPE=ALL&FILE_NAME=readme.txt&FILE_PATH=/ufa/HiRes/data/swics
    for more information.

    Parameters
    ----------
    starttime : datetime.datetime
        Start of interval
    endtime : datetime.datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data
    """
    names = ['year', 'doy', 'hour', 'minute', 'second',
             'VEL_ALPHA', 'RAT_C6_C5', 'RAT_O7_O6', 'RAT_FE_O', 'CHARGE_FE',
             'N_CYC']
    product = 'uswichst'
    units = OrderedDict([('VEL_ALPHA', u.km / u.s),
                        ('RAT_C6_C5', u.dimensionless_unscaled),
                        ('RAT_O7_O6', u.dimensionless_unscaled),
                        ('RAT_FE_O', u.dimensionless_unscaled),
                        ('CHARGE_FE', u.dimensionless_unscaled),
                        ('N_CYC', u.dimensionless_unscaled)])
    return _swics(starttime, endtime, names, product, units)


class _swicsDownloader(util.Downloader):
    def __init__(self, product, names, units):
        self.product = product
        self.names = names
        self.units = units

    def intervals(self, starttime, endtime):
        return self.intervals_yearly(starttime, endtime)

    def fname(self, interval):
        yearstr = interval.start.strftime('%Y')[-2:]
        return f'{self.product}{yearstr}.dat'

    def local_dir(self, interval):
        return pathlib.Path('ulysses') / 'swics'

    def download(self, interval):
        local_dir = self.local_path(interval).parent
        local_dir.mkdir(parents=True, exist_ok=True)
        fname = self.fname(interval)

        swics_options = url_options
        swics_options['FILE_NAME'] = fname
        swics_options['FILE_PATH'] = '/ufa/HiRes/data/swics'
        _download_ulysses(swics_options, fname, local_dir)
        return self.local_path(interval)

    def load_local_file(self, interval):
        readargs = {'names': self.names,
                    'delim_whitespace': True,
                    'na_values': ['******']}
        thisdata = pd.read_csv(self.local_path(interval), **readargs)
        thisdata = _convert_ulysses_time(thisdata)
        return thisdata


def _swics(starttime, endtime, names, product, units=None):
    downloader = _swicsDownloader(product, names, units)
    return downloader.load(starttime, endtime)


class _fgmDownloader(util.Downloader):
    def __init__(self, units):
        self.units = units

    def intervals(self, starttime, endtime):
        return self.intervals_daily(starttime, endtime)

    def fname(self, interval):
        dtime = interval.start
        yearstr = self.yearstr(interval)
        filename = ('U' + yearstr[-2:] + dtime.strftime('%j') + 'SH')
        return f'{filename}.ASC'

    @staticmethod
    def yearstr(interval):
        return interval.start.strftime('%Y')

    def local_dir(self, interval):
        return pathlib.Path('ulysses') / 'fgm' / 'hires'

    def download(self, interval):
        local_dir = self.local_path(interval).parent
        local_dir.mkdir(parents=True, exist_ok=True)
        fname = self.fname(interval)
        yearstr = self.yearstr(interval)

        fgm_options = url_options
        fgm_options['FILE_NAME'] = fname
        fgm_options['FILE_PATH'] = '/ufa/HiRes/VHM-FGM/' + yearstr
        _download_ulysses(fgm_options, fname, local_dir)
        return self.local_path(interval)

    def load_local_file(self, interval):
        readargs = {'names': ['year', 'doy', 'hour', 'minute', 'second',
                              'Bx', 'By', 'Bz', '|B|'],
                    'delim_whitespace': True}
        thisdata = pd.read_csv(self.local_path(interval), **readargs)
        thisdata = _convert_ulysses_time(thisdata)
        return thisdata


def fgm_hires(starttime, endtime):
    """
    Import high resolution fluxgate magnetometer data.

    Parameters
    ----------
    starttime : datetime.datetime
        Start of interval
    endtime : datetime.datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data
    """
    units = OrderedDict([('Bx', u.nT), ('By', u.nT),
                         ('Bz', u.nT), ('|B|', u.nT)])
    downloader = _fgmDownloader(units)
    return downloader.load(starttime, endtime)


class _swoopsionDownloader(util.Downloader):
    def __init__(self, units):
        self.units = units

    def intervals(self, starttime, endtime):
        return self.intervals_monthly(starttime, endtime)

    def fname(self, interval):
        dtime = interval.start
        year = dtime.strftime('%Y')
        doy = dtime.strftime('%j')
        return 'u{}{}bam.dat'.format(str(year)[2:], doy)

    @staticmethod
    def yearstr(interval):
        return interval.start.strftime('%Y')

    def local_dir(self, interval):
        return pathlib.Path('ulysses') / 'swoops' / 'ions'

    def download(self, interval):
        local_dir = self.local_path(interval).parent
        local_dir.mkdir(parents=True, exist_ok=True)
        fname = self.fname(interval)

        swoops_options = url_options
        year = fname[1:3]
        # doy = fname[5:8]
        swoops_options['FILE_NAME'] = fname
        swoops_options['FILE_PATH'] =\
            (f'/ufa/stageIngestArea/swoops/ions/bamion{year}.zip_files')
        _download_ulysses(swoops_options, fname, local_dir)
        return self.local_path(interval)

    def load_local_file(self, interval):
        readargs = {'names': ['year', 'doy', 'hour', 'minute', 'second',
                              'r', 'hlat', 'hlon', 'n_p', 'n_a',
                              'T_p_large', 'T_p_small',
                              'v_r', 'v_t', 'v_n', 'iqual'],
                    'delim_whitespace': True}
        thisdata = pd.read_csv(self.local_path(interval), **readargs)
        thisdata = _convert_ulysses_time(thisdata)
        return thisdata


def swoops_ions(starttime, endtime):
    """
    Import SWOOPS ion data.

    Parameters
    ----------
    starttime : datetime.datetime
        Start of interval
    endtime : datetime.datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.GenericTimeSeries`
        Requested data
    """

    units = OrderedDict([('T_p_large', u.K), ('T_p_small', u.K),
                        ('v_t', u.km / u.s), ('v_r', u.km / u.s),
                        ('v_n', u.km / u.s), ('r', u.au),
                        ('n_a', u.cm**-3), ('n_p', u.cm**-3),
                        ('hlat', u.deg),
                        ('hlon', u.deg),
                        ('iqual', u.dimensionless_unscaled)])
    downloader = _swoopsionDownloader(units)
    return downloader.load(starttime, endtime)


def _download_ulysses(options, fname, local_dir):
    """Common downloading functionality"""
    dl_url = ulysses_url
    for key in options:
        dl_url += key + '=' + options[key] + '&'
    # Download data
    try:
        util._download_remote(dl_url, fname, local_dir)
    except urllib.error.HTTPError:
        raise util.NoDataError


def _convert_ulysses_time(data):
    """Method to convert timestamps to datetimes"""
    if (data['year'] < 1900).all():
        data.loc[data['year'] > 50, 'year'] += 1900
        data.loc[data['year'] < 50, 'year'] += 2000

    data['Time'] = pd.to_datetime(data['year'].astype(str) + ':' +
                                  data['doy'].astype(str),
                                  format='%Y:%j')
    data['Time'] += (pd.to_timedelta(data['hour'], unit='h') +
                     pd.to_timedelta(data['minute'], unit='m') +
                     pd.to_timedelta(data['second'], unit='s'))
    data = data.drop(['year', 'doy', 'hour', 'minute', 'second'],
                     axis=1)
    return data
