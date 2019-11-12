"""
Methods for importing data from Parker Solar Probe.
"""
import pathlib
import urllib.error

import astropy.units as u
from heliopy.data import cdasrest
from heliopy.data import util


class _SWEAPDownloader(util.Downloader):
    def intervals(self, starttime, endtime):
        return self.intervals_daily(starttime, endtime)

    def download(self, interval):
        base_url = 'https://spdf.gsfc.nasa.gov/pub/data/'
        base_url += str(self.local_dir(interval))
        try:
            util._download_remote(base_url,
                                  self.fname(interval),
                                  self.local_path(interval).parent)
        except urllib.error.HTTPError:
            raise util.NoDataError

    def load_local_file(self, interval):
        local_path = self.local_path(interval)
        cdf = util._load_cdf(local_path)
        return util.cdf2df(cdf, index_key='Epoch', badvalues=[-1e31])


class _SWEAPL3Downloader(_SWEAPDownloader):
    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return pathlib.Path('psp') / 'sweap' / 'spc' / 'l3' / 'l3i' / year

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_swp_spc_l3i_{datestr}_v01.cdf'


def sweap_spc_l3(starttime, endtime):
    dl = _SWEAPL3Downloader()
    return dl.load(starttime, endtime)
