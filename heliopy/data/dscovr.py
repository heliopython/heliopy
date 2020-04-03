"""
Methods for importing data from DSCOVR.
"""
import pathlib
from heliopy.data import util

spdf_url = 'https://spdf.gsfc.nasa.gov/pub/data/'


class _MagDownloader(util.Downloader):
    def intervals(self, starttime, endtime):
        return self.intervals_daily(starttime, endtime)

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f"dscovr_h0_mag_{datestr}_v01.cdf"

    def local_dir(self, interval):
        return (pathlib.Path('dscovr') / 'h0' / 'mag' /
                interval.start.strftime('%Y'))

    def download(self, interval):
        filename = self.fname(interval)
        local_dir = self.local_path(interval).parent
        remote_base_url = spdf_url + str(self.local_dir(interval))
        print(filename)
        print(remote_base_url)
        util._download_remote(remote_base_url, filename, local_dir)

    def load_local_file(self, interval):
        # Read in data
        cdf = util._load_cdf(self.local_path(interval),)
        df = util.cdf2df(cdf, 'Epoch1', ignore=['Time1_PB5'])
        df.index.name = 'Time'
        return df


def mag_h0(starttime, endtime):
    """
    Import magnetic field data from DSCOVR Spacecraft.

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
    return _MagDownloader().load(starttime, endtime)
