"""
Methods for importing data from Parker Solar Probe.
"""
import pathlib
import urllib.error

import astropy.units as u
from heliopy.data import cdasrest
from heliopy.data import util


class _PSPDownloader(util.Downloader):
    base_url = 'https://spdf.gsfc.nasa.gov/pub/data/'
    epoch_label = 'Epoch'

    def intervals(self, starttime, endtime):
        return self.intervals_daily(starttime, endtime)

    def download(self, interval):
        url = self.base_url + str(self.local_dir(interval))
        try:
            util._download_remote(url,
                                  self.fname(interval),
                                  self.local_path(interval).parent)
        except urllib.error.HTTPError:
            raise util.NoDataError

    def load_local_file(self, interval):
        local_path = self.local_path(interval)
        cdf = util._load_cdf(local_path)
        return util.cdf2df(
            cdf, index_key=self.epoch_label, badvalues=self.badvalues)


# SWEAP classes/methods
class _SWEAPDownloader(_PSPDownloader):
    badvalues = None


class _SWEAPL3Downloader(_SWEAPDownloader):
    badvalues = [-1e31]

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return pathlib.Path('psp') / 'sweap' / 'spc' / 'l3' / 'l3i' / year

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_swp_spc_l3i_{datestr}_v01.cdf'


def sweap_spc_l3(starttime, endtime):
    dl = _SWEAPL3Downloader()
    return dl.load(starttime, endtime)


# FIELDS classes/methods
class _FIELDSDownloader(_PSPDownloader):
    badvalues = None


class _FIELDSmag_RTN_1min_Downloader(_FIELDSDownloader):
    epoch_label = 'epoch_mag_RTN_1min'

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        month = interval.start.strftime('%m')
        return pathlib.Path('psp') / 'fields' / 'l2' / 'mag_rtn_1min' / year

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_fld_l2_mag_rtn_1min_{datestr}_v01.cdf'


def fields_mag_rtn_1min(starttime, endtime):
    dl = _FIELDSmag_RTN_1min_Downloader()
    return dl.load(starttime, endtime)
