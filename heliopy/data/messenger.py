"""
Methods for importing data from the Messenger spacecraft.

All data is publically available at ftp://spdf.gsfc.nasa.gov/pub/data/messenger
"""
import os
import pandas as pd
import pathlib as path

from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
mess_dir = data_dir / 'messenger'
remote_mess_dir = 'ftp://spdf.gsfc.nasa.gov/pub/data/messenger/'


def mag_rtn(starttime, endtime, try_download=True):
    """
    Import magnetic field in RTN coordinates from Messenger.

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
    # Directory relative to main WIND data directory
    relative_dir = path.Path('rtn')
    fnames = []
    dirs = []
    extension = '.cdf'
    data = []
    ignore = ['Quality_Flag']
    daylist = util._daysplitinterval(starttime, endtime)
    for day in daylist:
        date = day[0]
        this_relative_dir = relative_dir / str(date.year)
        filename = 'messenger_mag_rtn_' +\
            str(date.year) +\
            str(date.month).zfill(2) +\
            str(date.day).zfill(2) +\
            '_v01'
        fnames.append(filename)
        dirs.append(this_relative_dir)

    local_base_dir = mess_dir
    remote_base_url = remote_mess_dir

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
        remote_url = remote_base_url + str(directory)
        filename = fname + extension
        local_dir = local_base_dir / directory
        util._download_remote(remote_url, filename, local_dir)

    def processing_func(cdf):
        thisdata = util.cdf2df(cdf, 'Epoch', ignore=ignore)
        return thisdata

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime,
                        try_download=try_download)
