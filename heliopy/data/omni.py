"""
Methods for importing data from the OMNI.

All data is publically available at
https://cdaweb.gsfc.nasa.gov/pub/data/omni.
"""
import pathlib as path

import pandas as pd
import numpy as np
import astropy.units as u
from collections import OrderedDict

from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
omni_dir = data_dir / 'omni'
remote_omni_dir = 'https://cdaweb.gsfc.nasa.gov/pub/data/omni/'


def low(starttime, endtime, try_download=True):
    """
    Import data from OMNI Web Interface.

    Parameters
    ----------
        starttime : datetime
            Interval start time.
        endtime : datetime
            Interval end time.

    Returns
    -------
        data : :class:`~sunpy.timeseries.TimeSeries`
    """

    # Directory relative to main OMNI data directory
    local_dir = omni_dir / 'low'
    dirs = []
    fnames = []
    names = ['Year', 'Decimal Day', 'Hour', 'Bartels Rotation Number',
             'ID IMF Spacecraft', 'ID SW Plasma Spacecraft', '# of points (IMF Average)',
             '# of points (Plasma Average)', '|B|', 'Magnitude of Avg Field Vector',
             'Lat. Angle of Aver. Field Vector', 'Long. Angle of Aver. Field Vector',
             'Bx GSE, GSM', 'By GSE', 'Bz GSE', 'By GSM', 'Bz GSM', 'sigma |B|',
             'sigma B', 'sigma Bx', 'sigma By', 'sigma Bz', 'Proton Temperature',
             'Proton Density', 'Plasma Flow Speed', 'Plasma Flow Long. Angle',
             'Plasma Flow Lat. Angle', 'Na/Np', 'Flow Pressure', 'sigma T',
             'sigma N', 'sigma V', 'sigma phi V', 'sigma theta V', 'sigma Na/Np',
             'Electric Field', 'Plasma Beta', 'Alfven Mach Number', 'Kp', 'R',
             'DST Index', 'AE Index', 'Proton Flux > 1MeV', 'Proton Flux > 2MeV',
             'Proton Flux > 4MeV', 'Proton Flux > 10MeV', 'Proton Flux > 30MeV',
             'Proton Flux > 60MeV', 'flag', 'ap index', 'f10.7 index', 'PC(N) index',
             'AL index (Kyoto)', 'AU index (Kyoto)', 'Magnetosonic Mach Number']
    extension = '.dat'
    for year in range(starttime.year, endtime.year + 1):
        fnames.append("omni2_{}".format(year))
        dirs.append(local_dir)


    def download_func(remote_base_url, local_base_dir,
                      directory, fname, extension):
        util.load()

    def processing_func():
        thisdata = pandas.read_table(<>, names=names, delim_whitespace=True)
        year = thisdata['Year'][0]
        day_list = list(thisdata['Decimal Day'])
        hour_list = list(thisdata['Hour'])
        len_ = len(thisdata)
        time_index = convert_datetime(year, day_list, hour_list, len_)
        thisdata['Time'] = time_index
        thisdata.set_index('Time')
        return thisdata


    def convert_datetime(year, day_list, hour_list, len_):
        datetime_index = []
        base_date = dt.datetime(year, 1, 1, 0, 0, 0)
        for x in range(0, len):
            delta_day = day_list[x]
            delta_hour = hour_list[x]
            time_delta = dt.timedelta(days=day_list[x], hours=hour_list[x])
            datetime_index.append(base_date + time_delta)
        return datetime_index


    return util.process(dirs, fnames, extension, omni_dir,
                        remote_omni_dir, download_func, processing_func,
                        starttime, endtime)
