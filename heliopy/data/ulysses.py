"""
Methods for importing data from the Ulysses spacecraft.

All data is publically available at http://ufa.esac.esa.int/ufa/
"""
import os
import pandas as pd
from datetime import datetime
from urllib.error import HTTPError

import heliopy.time as heliotime
from heliopy.data import helper
from heliopy import config

data_dir = config['default']['download_dir']
ulysses_dir = os.path.join(data_dir, 'ulysses')
ulysses_url = 'http://ufa.esac.esa.int/ufa-sl-server/data-action?'
url_options = {'PROTOCOL': 'HTTP',
               'PRODUCT_TYPE': 'ALL'}

# http://ufa.esac.esa.int/ufa-sl-server/data-action?PROTOCOL=HTTP&PRODUCT_TYPE=ALL&FILE_NAME=U95006SH.ASC&FILE_PATH=/ufa/HiRes/VHM-FGM/1995


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
    dtimes = heliotime.daysplitinterval(starttime, endtime)
    # Loop through years
    for dtime in dtimes:
        date = dtime[0]
        fgm_options['FILE_NAME'] = ('U' +
                                    date.strftime('%y') +
                                    date.strftime('%j') +
                                    'SH.ASC')
        fgm_options['FILE_PATH'] = '/ufa/HiRes/VHM-FGM/' + date.strftime('%Y')
        # Put together url for this days data
        remote_url = ulysses_url
        for key in fgm_options:
            remote_url += key + '=' + fgm_options[key] + '&'

        # Local locaiton to download to
        local_dir = os.path.join(ulysses_dir, 'fgm', 'hires',
                                 date.strftime('%Y'))

        f = helper.load(fgm_options['FILE_NAME'], local_dir, remote_url)

        # Read in data
        thisdata = pd.read_table(f, **readargs)
        # Process data/time
        thisdata = _convert_ulysses_time(thisdata)
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
    dtimes = heliotime.daysplitinterval(starttime, endtime)
    # Loop through individual days
    for dtime in dtimes:
        date = dtime[0]
        swoops_options['FILE_NAME'] = ('u' +
                                       date.strftime('%y') +
                                       date.strftime('%j') +
                                       'bam.dat')
        swoops_options['FILE_PATH'] =\
            ('/ufa/stageIngestArea/swoops/ions/bamion' +
             date.strftime('%y') + '.zip_files')

        # Put together url for this days data
        remote_url = ulysses_url
        for key in swoops_options:
            remote_url += key + '=' + swoops_options[key] + '&'
        # Local locaiton to download to
        local_dir = os.path.join(ulysses_dir, 'swoops', 'ions',
                                 date.strftime('%Y'))

        try:
            f = helper.load(swoops_options['FILE_NAME'], local_dir, remote_url)
        except HTTPError:
            print('No SWOOPS ion data available for date %s' % date)
            continue

        # Read in data
        thisdata = pd.read_table(f, **readargs)
        # Process data/time
        thisdata = _convert_ulysses_time(thisdata)
        data.append(thisdata)

    return helper.timefilter(data, starttime, endtime)


def _convert_ulysses_time(data):
    """Method to convert timestamps to datetimes"""
    data['year'] += 1900
    data['Time'] = pd.to_datetime(data['year'].astype(str) + ':' +
                                  data['doy'].astype(str),
                                  format='%Y:%j')
    data['Time'] += (pd.to_timedelta(data['hour'], unit='h') +
                     pd.to_timedelta(data['minute'], unit='m') +
                     pd.to_timedelta(data['second'], unit='s'))
    data = data.drop(['year', 'doy', 'hour', 'minute', 'second'],
                     axis=1)
    return data
