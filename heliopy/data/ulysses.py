"""
Methods for importing data from the Ulysses spacecraft.

All data is publically available at http://ufa.esac.esa.int/ufa/
"""
import pandas as pd
import pathlib as path
from datetime import datetime, date
from urllib.error import HTTPError

from heliopy.data import util
from collections import OrderedDict
import astropy.units as u
from heliopy import config

use_hdf = config['use_hdf']
data_dir = path.Path(config['download_dir'])

ulysses_dir = data_dir / 'ulysses'
ulysses_url = 'http://ufa.esac.esa.int/ufa-sl-server/data-action?'
url_options = {'PROTOCOL': 'HTTP',
               'PRODUCT_TYPE': 'ALL'}


def swics_heavy_ions(starttime, endtime, try_download=True):
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
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
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
                        ('DENS_O6', u.cm**-3), ('DENS_ALPHA', u.dimensionless_unscaled),
                        ('DENS_C6', u.dimensionless_unscaled),
                        ('DENS_O6', u.dimensionless_unscaled),
                        ('DENS_NE8', u.dimensionless_unscaled),
                        ('DENS_MG10', u.dimensionless_unscaled),
                        ('DENS_SI9', u.dimensionless_unscaled),
                        ('DENS_SI10', u.dimensionless_unscaled),
                        ('DENS_FE11', u.dimensionless_unscaled)])
    return _swics(starttime, endtime, names, product, units, try_download)


def swics_abundances(starttime, endtime, try_download=True):
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
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
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
    return _swics(starttime, endtime, names, product, units, try_download)


def _swics(starttime, endtime, names, product, units=None, try_download=True):
    data = []
    dtimes = util._daysplitinterval(starttime, endtime)
    dirs = []
    fnames = []
    extension = '.dat'
    local_base_dir = ulysses_dir / 'swics'
    remote_base_url = ulysses_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        local_dir = local_base_dir / directory
        swics_options = url_options
        swics_options['FILE_NAME'] = fname + extension
        swics_options['FILE_PATH'] = '/ufa/HiRes/data/swics'
        for key in swics_options:
            remote_base_url += key + '=' + swics_options[key] + '&'
        try:
            util._load_remote(remote_base_url, fname + extension, local_dir, 'ascii')
            # f = util.load('', local_dir, remote_base_url)
        except Exception as err:
            return

    def processing_func(f):
        readargs = {'names': names,
                    'delim_whitespace': True,
                    'na_values': ['******']}
        thisdata = pd.read_csv(f, **readargs)
        thisdata = _convert_ulysses_time(thisdata)
        return thisdata

    # Loop through years
    for year in range(starttime.year, endtime.year + 1):
        fname = '{}{}'.format(product, str(year)[-2:])
        # Local locaiton to download to
        dirs.append('')
        fnames.append(fname)

    return util.process(
        dirs, fnames, extension, local_base_dir, remote_base_url,
        download_func, processing_func, starttime, endtime,
        units=units, try_download=True)


def fgm_hires(starttime, endtime, try_download=True):
    """
    Import high resolution fluxgate magnetometer data.

    Parameters
    ----------
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data
    """
    dtimes = util._daysplitinterval(starttime, endtime)
    dirs = []
    fnames = []
    extension = '.ASC'
    local_base_dir = ulysses_dir / 'fgm' / 'hires'
    remote_base_url = ulysses_url
    units = OrderedDict([('Bx', u.nT), ('By', u.nT),
                         ('Bz', u.nT), ('|B|', u.nT)])

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        local_dir = local_base_dir / directory
        fgm_options = url_options
        fgm_options['FILE_NAME'] = fname + extension
        fgm_options['FILE_PATH'] = '/ufa/HiRes/VHM-FGM/' + yearstr
        remote_url = ulysses_url
        for key in fgm_options:
            remote_url += key + '=' + fgm_options[key] + '&'
        try:
            util._load_remote(remote_url, fname + extension, local_dir, 'ascii')
        except Exception as err:
            return

    def processing_func(f):
        readargs = {'names': ['year', 'doy', 'hour', 'minute', 'second',
                              'Bx', 'By', 'Bz', '|B|'],
                    'delim_whitespace': True}
        thisdata = pd.read_csv(f, **readargs)
        thisdata = _convert_ulysses_time(thisdata)
        return thisdata

    for dtime in dtimes:
        date = dtime[0]
        yearstr = date.strftime('%Y')
        filename = ('U' + yearstr[-2:] + date.strftime('%j') + 'SH')
        fnames.append(filename)
        this_relative_dir = local_base_dir / yearstr
        dirs.append(this_relative_dir)

    return util.process(
        dirs, fnames, extension, local_base_dir, remote_base_url,
        download_func, processing_func, starttime, endtime, units=units,
        try_download=True)


def swoops_ions(starttime, endtime, try_download=True):
    """
    Import SWOOPS ion data.

    Parameters
    ----------
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval

    Returns
    -------
    data : :class:`~sunpy.timeseries.TimeSeries`
        Requested data
    """

    dirs = []
    fnames = []
    extension = '.dat'
    local_base_dir = ulysses_dir / 'swoops' / 'ions'
    remote_base_url = ulysses_url
    units = OrderedDict([('T_p_large', u.K), ('T_p_small', u.K),
                        ('v_t', u.km / u.s), ('v_r', u.km / u.s),
                        ('v_n', u.km / u.s), ('r', u.au),
                        ('n_a', u.cm**-3), ('n_p', u.cm**-3),
                        ('hlat', u.deg),
                        ('hlon', u.deg),
                        ('iqual', u.dimensionless_unscaled)])

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        local_dir = local_base_dir / directory
        swoops_options = url_options
        year = fname[1:3]
        # doy = fname[5:8]
        swoops_options['FILE_NAME'] = fname + extension
        swoops_options['FILE_PATH'] =\
            ('/ufa/stageIngestArea/swoops/ions/bamion{}.zip_files'.format(year))
        for key in swoops_options:
            remote_base_url += key + '=' + swoops_options[key] + '&'
        try:
            util._load_remote(remote_base_url, fname + extension, local_dir, 'ascii')
            # f = util.load('', local_dir, remote_base_url)
        except Exception as err:
            return

    def processing_func(f):
        readargs = {'names': ['year', 'doy', 'hour', 'minute', 'second',
                              'r', 'hlat', 'hlon', 'n_p', 'n_a',
                              'T_p_large', 'T_p_small',
                              'v_r', 'v_t', 'v_n', 'iqual'],
                    'delim_whitespace': True}
        thisdata = pd.read_csv(f, **readargs)
        thisdata = _convert_ulysses_time(thisdata)
        return thisdata

    # Loop through years
    for year in range(starttime.year, endtime.year + 1):
        if year == starttime.year:
            start_month = starttime.month
        else:
            start_month = 1

        if year == endtime.year:
            end_month = endtime.month
        else:
            end_month = 12
        for month in range(start_month, end_month + 1):
            doy = datetime(year, month, 1).strftime('%j')
            fanme = ('u{}{}bam'.format(str(year)[2:], doy))
            # Local locaiton to download to
            dirs.append('{}'.format(year))
            fnames.append(fanme)

    return util.process(
        dirs, fnames, extension, local_base_dir, remote_base_url,
        download_func, processing_func, starttime, endtime,
        units=units, try_download=try_download)


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
