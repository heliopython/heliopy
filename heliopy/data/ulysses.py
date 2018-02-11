"""
Methods for importing data from the Ulysses spacecraft.

All data is publically available at http://ufa.esac.esa.int/ufa/
"""
import os
import pandas as pd
from datetime import datetime, date
from urllib.error import HTTPError

from heliopy.data import util
from heliopy import config

use_hdf = config['use_hdf']
data_dir = config['download_dir']

ulysses_dir = os.path.join(data_dir, 'ulysses')
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
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval

    Returns
    -------
    data : DataFrame
        Requested data
    """
    names = ['year', 'doy', 'hour', 'minute', 'second']
    for ion in ['ALPHA', 'C6', 'O6', 'NE8', 'MG10', 'SI9', 'SI10', 'FE11']:
        names += ['DENS_' + ion, 'VEL_' + ion, 'TEMP_' + ion]
    product = 'uswimatb'
    return _swics(starttime, endtime, names, product)


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
    starttime : datetime
        Start of interval
    endtime : datetime
        End of interval

    Returns
    -------
    data : DataFrame
        Requested data
    """
    names = ['year', 'doy', 'hour', 'minute', 'second',
             'VEL_ALPHA', 'RAT_C6_C5', 'RAT_O7_O6', 'RAT_FE_O', 'CHARGE_FE',
             'N_CYC']
    product = 'uswichst'
    return _swics(starttime, endtime, names, product)


def _swics(starttime, endtime, names, product):
    swics_options = url_options
    readargs = {'names': names,
                'delim_whitespace': True}

    data = []
    dtimes = util._daysplitinterval(starttime, endtime)
    # Loop through years
    for year in range(starttime.year, endtime.year + 1):
        swics_options['FILE_NAME'] = '{}{}.dat'.format(product,
                                                       str(year)[-2:])
        # Local locaiton to download to
        local_dir = os.path.join(ulysses_dir, 'swics')
        local_file = os.path.join(local_dir, swics_options['FILE_NAME'])
        local_hdf = local_file[:-4] + '.hdf'
        # If we have already saved a hdf file
        if os.path.exists(local_hdf):
            thisdata = pd.read_hdf(local_hdf)
        else:
            # Put together remote url
            swics_options['FILE_PATH'] = '/ufa/HiRes/data/swics'
            remote_url = ulysses_url
            for key in swics_options:
                remote_url += key + '=' + swics_options[key] + '&'
            f = util.load(swics_options['FILE_NAME'], local_dir, remote_url)
            if f is None:
                print('File {}/{} not available\n'.format(
                    remote_url, filename))
                continue

            # Read in data
            thisdata = pd.read_table(f, **readargs)
            # Process data/time
            thisdata = _convert_ulysses_time(thisdata)
            if use_hdf:
                thisdata.to_hdf(local_hdf, 'swics')
        data.append(thisdata)
    return util.timefilter(data, starttime, endtime)


def fgm_hires(starttime, endtime):
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
    data : DataFrame
        Requested data
    """
    fgm_options = url_options
    readargs = {'names': ['year', 'doy', 'hour', 'minute', 'second',
                          'Bx', 'By', 'Bz', '|B|'],
                'delim_whitespace': True}

    data = []
    dtimes = util._daysplitinterval(starttime, endtime)
    # Loop through years
    for dtime in dtimes:
        date = dtime[0]
        yearstr = date.strftime('%Y')
        fgm_options['FILE_NAME'] = ('U' + yearstr[-2:] +
                                    date.strftime('%j') + 'SH.ASC')
        # Local locaiton to download to
        local_dir = os.path.join(ulysses_dir, 'fgm', 'hires', yearstr)
        local_file = os.path.join(local_dir, fgm_options['FILE_NAME'])
        local_hdf = local_file[:-4] + '.hdf'
        # If we have already saved a hdf file
        if os.path.exists(local_hdf):
            thisdata = pd.read_hdf(local_hdf)
        else:
            # Put together remote url
            fgm_options['FILE_PATH'] = '/ufa/HiRes/VHM-FGM/' + yearstr
            remote_url = ulysses_url
            for key in fgm_options:
                remote_url += key + '=' + fgm_options[key] + '&'
            f = util.load(fgm_options['FILE_NAME'], local_dir, remote_url)

            # Read in data
            thisdata = pd.read_table(f, **readargs)
            # Process data/time
            thisdata = _convert_ulysses_time(thisdata)
            if use_hdf:
                thisdata.to_hdf(local_hdf, 'fgm_hires')
        data.append(thisdata)
    return util.timefilter(data, starttime, endtime)


def swoops_ions(starttime, endtime):
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
    data : DataFrame
        Requested data
    """
    swoops_options = url_options
    readargs = {'names': ['year', 'doy', 'hour', 'minute', 'second',
                          'r', 'hlat', 'hlon', 'n_p', 'n_a',
                          'T_p_large', 'T_p_small',
                          'v_r', 'v_t', 'v_n', 'iqual'],
                'delim_whitespace': True}

    data = []
    months_loaded = []
    dtimes = util._daysplitinterval(starttime, endtime)
    # Loop through individual days
    for dtime in dtimes:
        thisdate = dtime[0]
        # Get first day of the month
        first_day = date(thisdate.year, thisdate.month, 1)
        # Check if this month's data already loaded
        if first_day in months_loaded:
            continue
        doy = first_day.strftime('%j')

        swoops_options['FILE_NAME'] = ('u' +
                                       first_day.strftime('%y') +
                                       doy +
                                       'bam.dat')
        swoops_options['FILE_PATH'] =\
            ('/ufa/stageIngestArea/swoops/ions/bamion' +
             first_day.strftime('%y') + '.zip_files')

        # Put together url for this days data
        remote_url = ulysses_url
        for key in swoops_options:
            remote_url += key + '=' + swoops_options[key] + '&'
        # Local locaiton to download to
        local_dir = os.path.join(ulysses_dir, 'swoops', 'ions',
                                 first_day.strftime('%Y'))

        # Load data
        try:
            f = util.load(swoops_options['FILE_NAME'], local_dir, remote_url)
        except HTTPError:
            print('No SWOOPS ion data available for date %s' % first_day)
            continue

        # Read in data
        thisdata = pd.read_table(f, **readargs)
        # Process data/time
        thisdata = _convert_ulysses_time(thisdata)
        data.append(thisdata)
        months_loaded.append(first_day)

    return util.timefilter(data, starttime, endtime)


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
