"""
Methods for importing data from the Ulysses spacecraft.

All data is publically available at http://ufa.esac.esa.int/ufa/
"""
import os
import pandas as pd
from datetime import datetime, date
from urllib.error import HTTPError

from heliopy.data import helper
from heliopy import config

use_hdf = config['use_hdf']
data_dir = config['download_dir']

ulysses_dir = os.path.join(data_dir, 'ulysses')
ulysses_url = 'http://ufa.esac.esa.int/ufa-sl-server/data-action?'
url_options = {'PROTOCOL': 'HTTP',
               'PRODUCT_TYPE': 'ALL'}


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
    dtimes = helper._daysplitinterval(starttime, endtime)
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
            f = helper.load(fgm_options['FILE_NAME'], local_dir, remote_url)

            # Read in data
            thisdata = pd.read_table(f, **readargs)
            # Process data/time
            thisdata = _convert_ulysses_time(thisdata)
            if use_hdf:
                thisdata.to_hdf(local_hdf, 'fgm_hires')
        data.append(thisdata)
    return helper.timefilter(data, starttime, endtime)


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
    dtimes = helper._daysplitinterval(starttime, endtime)
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
            f = helper.load(swoops_options['FILE_NAME'], local_dir, remote_url)
        except HTTPError:
            print('No SWOOPS ion data available for date %s' % first_day)
            continue

        # Read in data
        thisdata = pd.read_table(f, **readargs)
        # Process data/time
        thisdata = _convert_ulysses_time(thisdata)
        data.append(thisdata)
        months_loaded.append(first_day)

    return helper.timefilter(data, starttime, endtime)


def _convert_ulysses_time(data):
    """Method to convert timestamps to datetimes"""
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
