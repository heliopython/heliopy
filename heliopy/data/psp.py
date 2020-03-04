"""
Methods for importing data from Parker Solar Probe.
"""
import astropy.units as u
import pathlib
import urllib.error

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

    def load_local_file(self, interval, product_list=None, want_xr=False):
        local_path = self.local_path(interval)
        cdf = util._load_cdf(local_path)
        return util.cdf2df(cdf, index_key=self.epoch_label)


# SWEAP classes/methods
class _SWEAPDownloader(_PSPDownloader):
    units = {'u/e': u.dimensionless_unscaled}
    # Fill in some missing units
    for i in range(3):
        for j in ['p', 'p1', 'a', '3']:
            units[f'v{j}_fit_SC_{i}'] = u.km / u.s
            units[f'v{j}_fit_SC_uncertainty_{i}'] = u.km / u.s
            units[f'v{j}_fit_RTN_{i}'] = u.km / u.s
            units[f'v{j}_fit_RTN_uncertainty_{i}'] = u.km / u.s
            units[f'v{j}_moment_SC_{i}'] = u.km / u.s
            units[f'v{j}_moment_SC_deltahigh_{i}'] = u.km / u.s
            units[f'v{j}_moment_SC_deltalow_{i}'] = u.km / u.s
            units[f'v{j}_moment_RTN_{i}'] = u.km / u.s
            units[f'v{j}_moment_RTN_deltahigh_{i}'] = u.km / u.s
            units[f'v{j}_moment_RTN_deltalow_{i}'] = u.km / u.s

    def __init__(self, level):
        assert level in (2, 3)
        self.level = level

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return (pathlib.Path('psp') / 'sweap' / 'spc' /
                f'l{self.level}' / f'l{self.level}i' / year)

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_swp_spc_l{self.level}i_{datestr}_v01.cdf'


def sweap_spc_l2(starttime, endtime):
    """
    SWEAP SPC proton and alpha particle moments and fits.
    """
    dl = _SWEAPDownloader(level=2)
    return dl.load(starttime, endtime)


def sweap_spc_l3(starttime, endtime):
    """
    SWEAP SPC proton and alpha particle moments and fits.
    """
    dl = _SWEAPDownloader(level=3)
    return dl.load(starttime, endtime)


# FIELDS classes/methods
class _FIELDSDownloader(_PSPDownloader):
    pass


class _FIELDSmag_RTN_1min_Downloader(_FIELDSDownloader):
    epoch_label = 'epoch_mag_RTN_1min'

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return pathlib.Path('psp') / 'fields' / 'l2' / 'mag_rtn_1min' / year

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d')
        return f'psp_fld_l2_mag_rtn_1min_{datestr}_v01.cdf'


class _FIELDSmag_RTN_Downloader(_FIELDSDownloader):
    epoch_label = 'epoch_mag_RTN'

    def intervals(self, starttime, endtime):
        daily = self.intervals_daily(starttime, endtime)
        intervals = []
        # Split into 4 hourly intervals
        for interval in daily:
            intervals += interval.split(4)
        # Remove intervals from the beginning
        for interval in intervals[:4].copy():
            if starttime > interval.end:
                intervals.pop(0)
        # Remove intervals from the end
        for interval in intervals[-4:].copy():
            if endtime < interval.start:
                intervals.pop(-1)
        return intervals

    def local_dir(self, interval):
        year = interval.start.strftime('%Y')
        return pathlib.Path('psp') / 'fields' / 'l2' / 'mag_rtn' / year

    def fname(self, interval):
        datestr = interval.start.strftime('%Y%m%d%H')
        return f'psp_fld_l2_mag_rtn_{datestr}_v01.cdf'


def fields_mag_rtn_1min(starttime, endtime):
    """
    1 minute averaged magnetic field data.
    """
    dl = _FIELDSmag_RTN_1min_Downloader()
    return dl.load(starttime, endtime)


def fields_mag_rtn(starttime, endtime):
    """
    Full resolution magnetic field data.
    """
    dl = _FIELDSmag_RTN_Downloader()
    return dl.load(starttime, endtime)
