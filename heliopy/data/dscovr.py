"""
Methods for importing data from the DSCOVR.

All data is publically available at
ftp://spdf.gsfc.nasa.gov/pub/data/dscovr/.
"""
import pathlib as path

from heliopy.data import util
from heliopy import config

data_dir = path.Path(config['download_dir'])
dscovr_dir = data_dir / 'dscovr'
dscovr_url = 'https://spdf.gsfc.nasa.gov/pub/data/dscovr/'


def mag_h0(starttime, endtime):
    """
    Imports  magnetic field data from DSCOVR Spacecraft.
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

    dirs = []
    fnames = []
    extension = '.cdf'
    ignore = ['Time1_PB5']
    daylist = util._daysplitinterval(starttime, endtime)
    for day in daylist:
        date = day[0]
        filename = "dscovr_h0_mag_{}{:02}{:02}_v01".format(
                     date.year, date.month, date.day)
        fnames.append(filename)
        this_relative_dir = 'h0/mag/' + str(date.year)
        dirs.append(this_relative_dir)

    local_base_dir = dscovr_dir
    remote_base_url = dscovr_url

    def download_func(remote_base_url, local_base_dir,
                      directory, fname, remote_fname, extension):
            remote_url = remote_base_url + str(directory)
            util.load(fname + extension,
                      local_base_dir / directory,
                      remote_url)

    def processing_func(cdf):
        df = util.cdf2df(cdf, 'Epoch1', ignore=ignore)
        df.index.name = 'Time'
        return df

    return util.process(dirs, fnames, extension, local_base_dir,
                        remote_base_url, download_func, processing_func,
                        starttime, endtime)
