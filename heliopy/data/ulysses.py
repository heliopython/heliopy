"""
Methods for importing data from the Ulysses spacecraft.

All data is publically available at http://ufa.esac.esa.int/ufa/
"""
import os
import pandas as pd
from datetime import datetime

import heliopy.time as heliotime
from heliopy.data import helper
from heliopy import config

data_dir = config['default']['download_dir']
ulysses_dir = os.path.join(data_dir, 'ulysses')
ulysses_url = 'http://ufa.esac.esa.int/ufa-sl-server/data-action?'
url_options = {'PROTOCOL': 'HTTP'}

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
    fgm_options['PRODUCT_TYPE'] = 'ALL'

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

        readargs = {'names': ['year', 'DOY', 'hour', 'minute', 'second',
                              'Bx', 'By', 'Bz', '|B|'],
                    'delim_whitespace': True}
        # Read in data
        thisdata = pd.read_table(f, **readargs)
        # Process data/time
        thisdata['year'] += 1900
        thisdata['Time'] = pd.to_datetime(thisdata['year'].astype(str) + ':' +
                                          thisdata['DOY'].astype(str),
                                          format='%Y:%j')
        thisdata['Time'] += (pd.to_timedelta(thisdata['hour'], unit='h') +
                             pd.to_timedelta(thisdata['minute'], unit='m') +
                             pd.to_timedelta(thisdata['second'], unit='s'))
        thisdata = thisdata.drop(['year', 'DOY', 'hour', 'minute', 'second'],
                                 axis=1)
        data.append(thisdata)

    return helper.timefilter(data, starttime, endtime)
